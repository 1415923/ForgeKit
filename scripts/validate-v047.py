"""Validate the v0.47 capability, migration, ownership and distribution contract."""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from structured_upgrade import sections, separate_user


def validate(repo):
    errors = []
    def require(condition, message):
        if not condition:
            errors.append(message)
    def read(path):
        return (repo / path).read_text(encoding='utf-8')
    version = read('VERSION').strip()
    spec = importlib.util.spec_from_file_location('entry_policy_checks', repo / 'scripts/validate-agent-entries.py')
    policy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(policy)
    require(version == '0.47.0', 'VERSION must be 0.47.0')
    for path in ('.codex-plugin/plugin.json', '.claude-plugin/plugin.json', '.agents/plugins/marketplace.json', '.claude-plugin/marketplace.json'):
        data = json.loads(read(path))
        values = re.findall(r'"version"\s*:\s*"([^"]+)"', json.dumps(data))
        require(values and all(v == version for v in values), f'Public version drift: {path}')
    require(not (repo / 'usage.html').exists(), 'usage.html is retired')
    for path in ('.gitattributes', 'project-template/.gitattributes'):
        require('*.md text eol=lf' in read(path).splitlines(), f'checkout-contract: Markdown LF rule missing: {path}')
    for forbidden in ('plugins', '.codex-plugin/user-rules', '.claude-plugin/user-rules'):
        require(not (repo / forbidden).exists(), f'Forbidden plugin distribution path: {forbidden}')
    capabilities = json.loads(read('config/skill-capabilities.json'))
    canonical, aliases = capabilities['canonical'], capabilities['aliases']
    require(len(canonical) == 7 and len(set(canonical)) == 7 and len(aliases) == 3, 'Expected seven canonical capabilities and three aliases')
    config = json.loads(read('config/skill-projections.json'))
    require({x['skill'] for x in config['entries']} == set(canonical) | set(aliases), 'Capability/projection mismatch')
    for entry in config['entries']:
        name = entry['skill']
        for relative in entry['managed_files']:
            source = repo / 'skills' / name / relative
            projection = repo / config['target_root'] / name / relative
            require(source.is_file() and projection.is_file(), f'Missing Skill payload: {name}/{relative}')
            if source.is_file() and projection.is_file():
                require(source.read_bytes() == projection.read_bytes(), f'Projection drift: {name}/{relative}')
        text = read(f'skills/{name}/SKILL.md')
        for rule, matched in policy.detect_policy_contradictions(policy.extract_policy_prose(text, set(canonical) | set(aliases))):
            require(False, policy.contradiction_error(name, rule, matched))
        require(text.isascii(), f'Skill must be ASCII: {name}')
        require(text.startswith(f'---\nname: {name}\n'), f'Skill name/frontmatter mismatch: {name}')
        desc = re.search(r'^description: (.+)$', text, re.M)
        require(desc is not None and len(desc.group(1)) <= 200, f'Skill description must be concise: {name}')
        yaml = read(f'skills/{name}/agents/openai.yaml')
        require(f'${name}\\n' in yaml, f'Explicit default invocation missing: {name}')
        if name in aliases or name == 'document-backfill':
            require('allow_implicit_invocation: false' in yaml, f'Explicit-only policy missing: {name}')
        if name in aliases:
            require(f"../{aliases[name]['skill']}/SKILL.md" in text, f'Alias destination mismatch: {name}')
        for link in re.findall(r'\]\(([^)#]+)', text):
            if not re.match(r'\w+://', link):
                require((repo / 'skills' / name / link).is_file(), f'Broken Skill reference: {name}: {link}')
    retired = json.loads(read('config/v047-document-moves.json'))
    for path, destination in retired.items():
        require(not (repo / 'project-template' / path).exists(), f'Retired template path: {path}')
        require((repo / 'project-template' / destination).is_file(), f'Missing merge destination: {destination}')
    for path in ('AGENTS.md', 'CLAUDE.md'):
        text = read('project-template/' + path)
        for skill in canonical:
            require(skill in text, f'Missing canonical route: {path}: {skill}')
        for rule, matched in policy.detect_policy_contradictions(policy.extract_policy_prose(text, set(canonical) | set(aliases))):
            require(False, policy.contradiction_error(path, rule, matched))
        require(len(text) < 3000, f'Entry too large: {path}')
        for ref in ('project-boundary.yml', 'codebase-map.md', 'testing.md', '.codex/stacks/<stack>/', 'forgekit-project.py', 'TODO_REVIEW'):
            require(ref in text, f'Missing startup boundary or validation reference: {path}: {ref}')
        require('<!-- forgekit:user begin -->' in text, f'Missing user region: {path}')
        sections(separate_user(text.encode())[0])
    contract = read('project-template/governance/agent-entry-contract.md')
    for anchor in ('Project and Write Boundary', 'Evidence and No Fabrication', 'Audit Default', 'Bounded Local Authorization', 'External and Irreversible Actions', 'Minimum Evidence-Based Writeback', 'Skill Routing'):
        require('## ' + anchor in contract, f'Missing normative contract: {anchor}')
    for name in ('code-review', 'security-review'):
        text = read(f'skills/{name}/SKILL.md')
        for field in ('impact_severity', 'blocking', 'failure_path', 'blocked_scope'):
            require(field in text, f'Missing structured finding contract: {name}: {field}')
    manifest = json.loads(read('project-template/.forgekit/template-manifest.json'))
    state = json.loads(read('project-template/.forgekit/state.json'))
    require(manifest['schema_version'] == 2 and manifest['template_version'] == version and state['forgekit_version'] == version, 'Template metadata version mismatch')
    require(not any(x['source_path'] == 'README.md' for x in manifest['files']), 'Business README must remain user-owned')
    package = repo / 'migrations' / version
    descriptor = json.loads((package / 'migration.json').read_text(encoding='utf-8'))
    require(descriptor['from'] == '0.46.0' and descriptor['to'] == version and descriptor['schema_version'] == 2, 'Migration predecessor/schema mismatch')
    expected = {'migration.json', *descriptor.get('inventory', [])}
    seen = set()
    for action in descriptor['actions']:
        require(action['target'] != 'README.md', 'Migration targets business README')
        require(action['target'] not in seen, f'Duplicate migration target: {action["target"]}')
        seen.add(action['target'])
        for field in ('source', 'baseline'):
            if field in action:
                expected.add(action[field])
        if 'source' in action:
            payload = package / action['source']
            entry = action['lock_entry']
            current = repo / 'project-template' / entry['source_path']
            require(payload.is_file() and current.is_file() and payload.read_bytes() == current.read_bytes(), f'Incoming payload drift: {action["target"]}')
    require({p.relative_to(package).as_posix() for p in package.rglob('*') if p.is_file()} == expected, 'Migration payload inventory mismatch')
    for p in package.rglob('*'):
        if p.is_file():
            mirror = repo / 'project-template/migrations' / version / p.relative_to(package)
            require(mirror.is_file() and mirror.read_bytes() == p.read_bytes(), f'Migration mirror drift: {p.relative_to(package)}')
    for relative in ('structured_upgrade.py', 'forgekit-upgrade.py'):
        require((repo / 'scripts' / relative).read_bytes() == (repo / 'project-template/scripts' / relative).read_bytes(), f'Runtime mirror drift: {relative}')
    result = subprocess.run([sys.executable, '-B', str(repo / 'scripts/update-template-manifest.py'), 'check', '--repo-root', str(repo)], capture_output=True, text=True, encoding='utf-8', errors='replace', env=dict(os.environ, PYTHONUTF8='1'))
    require(result.returncode == 0, 'Manifest validation: ' + result.stdout + result.stderr)
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        errors = validate(Path(args.repo_root).resolve())
    except (OSError, ValueError, KeyError) as exc:
        errors = [str(exc)]
    for error in errors:
        print('[fail] ' + error)
    if errors:
        raise SystemExit(1)
    print('[ok] v0.47 capability, entry, migration and manifest contracts passed')


if __name__ == '__main__':
    main()
