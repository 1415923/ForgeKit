"""Rebuild the explicit v0.47 package from preserved v0.46 payloads and current template."""
import hashlib
import base64
import io
import json
import shutil
import subprocess
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / 'project-template'
PACKAGE = ROOT / 'migrations/0.47.0'

from structured_upgrade import PROJECT_FACT_DOCS


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())


def target(source):
    if source.startswith('docs/'):
        return '.forgekit/' + source
    if source.startswith('changes/'):
        return '.forgekit/' + source
    return source


def main():
    old = json.loads((PACKAGE / 'baseline-index.json').read_text(encoding='utf-8'))
    manifest_path = TEMPLATE / '.forgekit/template-manifest.json'
    current = json.loads(manifest_path.read_text(encoding='utf-8'))
    retired = json.loads((ROOT / 'config/v047-document-moves.json').read_text())
    catalog_path = PACKAGE / 'legacy-baselines.json'
    if not catalog_path.is_file():
        versions = {}
        tags = subprocess.run(['git', 'tag', '--list', 'v0.*'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
        for tag in tags:
            version = tuple(map(int, tag[1:].split('.')))
            if not (0, 36, 0) <= version < (0, 46, 0):
                continue
            result = subprocess.run(['git', 'archive', '--format=zip', tag, 'project-template'], cwd=ROOT, capture_output=True, check=True)
            with zipfile.ZipFile(io.BytesIO(result.stdout)) as archive:
                entries = {}
                for name in archive.namelist():
                    src = name[len('project-template/'):]
                    if name.endswith('/') or src.startswith('migrations/') or src in ('README.md', '.forgekit/state.json', '.forgekit/template-manifest.json'):
                        continue
                    entries[target(src)] = base64.b64encode(archive.read(name)).decode()
                versions[tag[1:]] = entries
        save(catalog_path, {'schema_version': 1, 'versions': versions})
    catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
    if catalog['schema_version'] == 1:
        versions, blobs = {}, {}
        for version, paths in catalog['versions'].items():
            versions[version] = {}
            for path, encoded in paths.items():
                data = base64.b64decode(encoded)
                checksum = hashlib.sha256(data).hexdigest()
                versions[version][path] = checksum
                blobs[checksum] = base64.b64encode(zlib.compress(data, 9)).decode()
        save(catalog_path, {'schema_version': 2, 'encoding': 'zlib+base64', 'versions': versions, 'blobs': blobs})
        catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
    # Published migration payloads can differ from release-tag template snapshots.
    artifacts = {}
    for descriptor_path in sorted((ROOT / 'migrations').glob('*/migration.json')):
        if descriptor_path.parent == PACKAGE:
            continue
        descriptor = json.loads(descriptor_path.read_text(encoding='utf-8-sig'))
        for action in descriptor['actions']:
            if not action.get('target'):
                continue
            for field in ('source', 'baseline'):
                if not action.get(field):
                    continue
                data = (descriptor_path.parent / action[field]).read_bytes()
                checksum = hashlib.sha256(data).hexdigest()
                catalog['blobs'][checksum] = base64.b64encode(zlib.compress(data, 9)).decode()
                artifacts.setdefault(action['target'], set()).add(checksum)
    catalog['artifacts'] = {p: sorted(ids) for p, ids in sorted(artifacts.items())}
    save(catalog_path, catalog)
    old_entries = {target(i['source_path']): i for i in old['files'] if not i['source_path'].startswith('migrations/')}
    entries = {i['source_path']: i for i in current['files']
               if (TEMPLATE / i['source_path']).is_file() and not i['source_path'].startswith('migrations/0.47.0/')}
    for p in TEMPLATE.rglob('*'):
        if not p.is_file():
            continue
        src = p.relative_to(TEMPLATE).as_posix()
        if 'migrations' in p.relative_to(TEMPLATE).parts or '__pycache__' in p.parts or src in ('README.md', '.forgekit/template-manifest.json', '.forgekit/state.json'):
            continue
        if src not in entries:
            role = 'skill' if src.startswith('.agents/skills/') else 'script' if src.startswith('scripts/') else 'metadata'
            install_target = '${managed_docs_root}/' + src[5:] if src.startswith('docs/') else '${change_root}/' + src[8:] if src.startswith('changes/') else target(src)
            entries[src] = {'source_path': src, 'target_path': install_target, 'role': role,
                            'update_policy': 'merge' if src.endswith('.md') else 'replace', 'render_mode': 'copy'}
    actions, expected = [], {'migration.json', 'baseline-index.json', 'legacy-baselines.json'}
    for src, entry in sorted(entries.items()):
        if src.startswith('docs/'):
            entry['target_path'] = '${managed_docs_root}/' + src[5:]
        elif src.startswith('changes/'):
            entry['target_path'] = '${change_root}/' + src[8:]
        if src.startswith('migrations/'):
            continue
        dst = target(src)
        baseline = PACKAGE / 'baseline' / dst
        incoming = (TEMPLATE / src).read_bytes()
        old_bytes = baseline.read_bytes() if baseline.is_file() else None
        if incoming == old_bytes:
            continue
        kind = 'merge_entry' if dst in ('AGENTS.md', 'CLAUDE.md') else 'merge_markdown' if dst.endswith('.md') and old_bytes is not None else 'replace_file_if_baseline_matches' if old_bytes is not None else 'copy_file_if_missing'
        action = {'id': 'update-' + dst.replace('/', '-'), 'type': kind, 'safety': 'safe',
                  'source': 'files/' + dst, 'target': dst, 'lock_entry': entry}
        if src.startswith('docs/') and Path(src).stem in PROJECT_FACT_DOCS:
            action['content_policy'] = 'project_facts'
        if old_bytes is not None:
            action['baseline'] = 'baseline/' + dst
            expected.add(action['baseline'])
        path = PACKAGE / action['source']
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(incoming)
        expected.add(action['source'])
        actions.append(action)
    for src, dst in retired.items():
        destinations = {'*': target(dst)}
        if src == '.codex/scope.md':
            destinations.update({'验收标准': '.forgekit/docs/requirements.md', '风险与依赖': '.forgekit/docs/risk-register.md'})
        action = {'id': 'relocate-' + src.replace('/', '-'), 'type': 'relocate_markdown', 'safety': 'safe',
                  'target': target(src), 'baseline': 'baseline/' + target(src), 'destinations': destinations}
        if src in ('.codex/rules.md', 'docs/context-continuity.md', 'docs/workflow-router.md'):
            action['rules_only'] = True
        actions.append(action)
        expected.add(action['baseline'])
    descriptor = {'schema_version': 2, 'id': 'forgekit-0.47.0', 'title': 'Astra convergence and structured customization migration',
                  'from': '0.46.0', 'to': '0.47.0', 'risk': 'high', 'actions': actions,
                  'manual_review': ['Only unresolved overlapping edits, unknown baselines, or ambiguous structures stop apply.'],
                  'non_goals': ['No business README, root-layout move, model API call, task invention, publish or deploy.'],
                  'inventory': ['baseline-index.json'], 'check_current_docs': True,
                  'features': {'structured_migration': True}, 'template_lock': {'retire_targets': ['README.md']}}
    descriptor['legacy_baselines'] = 'legacy-baselines.json'
    descriptor['reference_paths'] = sorted(target(src) for src in entries if src.endswith('.md') and not src.startswith('migrations/'))
    save(PACKAGE / 'migration.json', descriptor)
    # Keep the captured original baseline inventory: it is reproducible input, not current project truth.
    descriptor['inventory'] = sorted(['baseline-index.json', 'legacy-baselines.json'] + [p.relative_to(PACKAGE).as_posix() for p in (PACKAGE / 'baseline').rglob('*') if p.is_file() and p.relative_to(PACKAGE).as_posix() not in expected])
    save(PACKAGE / 'migration.json', descriptor)
    mirror = TEMPLATE / 'migrations/0.47.0'
    allowed = expected | set(descriptor['inventory'])
    for package_root in (PACKAGE, mirror):
        for path in package_root.rglob('*'):
            if path.is_file() and path.relative_to(package_root).as_posix() not in allowed:
                assert path.resolve().is_relative_to(package_root.resolve())
                path.unlink()
    for p in PACKAGE.rglob('*'):
        if p.is_file():
            dst = mirror / p.relative_to(PACKAGE)
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(p.read_bytes())
    current.update(schema_version=2, template_version='0.47.0', files=list(entries.values()))
    for entry in current['files']:
        if entry['source_path'].endswith('.md') and not entry['source_path'].startswith('migrations/'):
            entry['document_id'] = target(entry['source_path'])
        entry['checksum'] = 'sha256:' + hashlib.sha256((TEMPLATE / entry['source_path']).read_bytes()).hexdigest()
    save(manifest_path, current)
    print(f'[ok] v0.47 package: {len(actions)} actions; historical packages untouched')


if __name__ == '__main__':
    main()
