"""Deterministic, loss-preserving Markdown migrations. No model or network calls."""
from __future__ import annotations

import base64
import copy
import difflib
import hashlib
import json
import importlib.util
import os
import posixpath
import re
import uuid
import zlib
from pathlib import Path, PurePosixPath


# These are project facts and records, not ForgeKit policy. Filled documents may
# legitimately replace the starter's headings, tables and explanatory prose.
PROJECT_FACT_DOCS = {
    'api', 'architecture', 'change-impact', 'changelog', 'code-ownership',
    'codebase-map', 'codex-next-work-order', 'database-design', 'defect-fix-plan',
    'defect-review', 'dependency-review', 'deployment', 'environment-matrix',
    'exploration-report', 'handover-audit', 'implementation-plan', 'incident-review',
    'project-plan', 'project-suitability', 'project-trial-record', 'quality-metrics',
    'release-pipeline', 'requirements', 'risk-register', 'task-board', 'task-intake',
    'tech-decisions', 'technical-debt', 'testing', 'threat-model', 'traceability',
    'version-roadmap', 'work-log',
}

class Conflict(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest() if data is not None else None


def safe_path(root, relative):
    p = PurePosixPath(relative)
    if (not relative or p.is_absolute() or '\\' in relative or ':' in relative
            or any(x in ('', '.', '..') for x in relative.split('/'))):
        raise Conflict(f'Unsafe path: {relative}')
    if p.parts[0] not in {'.forgekit', '.codex', '.agents', '.claude', 'governance', 'scripts', 'migrations', 'AGENTS.md', 'CLAUDE.md'}:
        raise Conflict(f'Path outside managed surface: {relative}')
    root = Path(root).resolve()
    result = root.joinpath(*p.parts)
    for node in (result, *result.parents):
        if node == root:
            break
        if node.is_symlink() or (hasattr(node, 'is_junction') and node.is_junction()):
            raise Conflict(f'Linked migration target: {relative}')
    if not result.resolve().is_relative_to(root):
        raise Conflict(f'Path escapes project: {relative}')
    if result.exists() and not result.is_file():
        raise Conflict(f'Target is not a file: {relative}')
    if result.exists() and result.stat().st_nlink > 1:
        raise Conflict(f'Hard-linked migration target: {relative}')
    return result


def decode(data):
    try:
        return data.decode('utf-8-sig').replace('\r\n', '\n')
    except UnicodeError as exc:
        raise Conflict('Text is not UTF-8') from exc


def merge_text(base, local, incoming):
    """Merge non-overlapping edits; conflicts retain both alternatives in the report."""
    if local == base or local == incoming:
        return incoming
    if incoming == base:
        return local
    b, l, n = map(decode, (base, local, incoming))
    if l == b or l == n:
        return incoming
    if n == b:
        return local
    lines = b.splitlines(keepends=True)

    def changes(text):
        other = text.splitlines(keepends=True)
        return [(i, j, other[a:z]) for op, i, j, a, z in
                difflib.SequenceMatcher(None, lines, other, autojunk=False).get_opcodes() if op != 'equal']

    edits = changes(n)
    for edit in changes(l):
        if edit in edits:
            continue
        i, j, replacement = edit
        for a, z, new in edits:
            intersects = max(i, a) < min(j, z)
            same_insert = i == j == a == z
            interior_insert = (i == j and a < i < z) or (a == z and i < a < j)
            if intersects or same_insert or interior_insert:
                raise Conflict(f'Overlapping edits at baseline lines {min(i, a)+1}-{max(j, z)+1}')
        edits.append(edit)
    result = list(lines)
    for i, j, replacement in sorted(edits, key=lambda e: (e[0], e[1]), reverse=True):
        result[i:j] = replacement
    return ''.join(result).encode('utf-8')


def sections(data):
    """H2 sections outside fences, with optional stable IDs. Preserve opaque spans."""
    text = decode(data)
    parts, current, content, fence, pending = {}, '__preamble__', [], None, None
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        mark = re.fullmatch(r'<!-- forgekit:section ([a-z0-9._-]+) -->\s*', line)
        if not fence and mark:
            if pending:
                raise Conflict('Repeated section marker')
            pending = mark.group(1)
            continue
        fm = re.match(r'^(`{3,}|~{3,})', stripped)
        if fm:
            if fence is None:
                fence = fm.group(1)
            elif fm.group(1)[0] == fence[0] and len(fm.group(1)) >= len(fence):
                fence = None
        heading = re.match(r'^## (.+?)\s*$', line) if not fence else None
        if heading:
            parts[current] = ''.join(content)
            current = pending or heading.group(1)
            pending = None
            if current in parts:
                raise Conflict(f'Duplicate section: {current}')
            content = [line]
        else:
            if pending and line.strip():
                raise Conflict('Section marker must precede a heading')
            content.append(line)
    if pending:
        raise Conflict('Section marker without heading')
    parts[current] = ''.join(content)
    return parts


def mark_sections(data):
    text = decode(data)
    if '<!-- forgekit:section ' in text:
        sections(data)
        return data
    blocks = sections(data)
    out = []
    for heading, body in blocks.items():
        if heading != '__preamble__':
            sid = 's-' + digest(heading.encode())[:12]
            out.append(f'<!-- forgekit:section {sid} -->\n')
        out.append(body)
    return ''.join(out).encode()


def user_region(data, additions):
    start, end = '<!-- forgekit:user begin -->', '<!-- forgekit:user end -->'
    text = decode(data)
    if text.count(start) != text.count(end) or text.count(start) > 1:
        raise Conflict('Invalid user region')
    if start in text:
        left, rest = text.split(start)
        user, right = rest.split(end)
    else:
        left, user, right = text.rstrip() + '\n\n', '\n', '\n'
    for origin, content in additions:
        marker = '<!-- forgekit:origin ' + origin + ' -->'
        if marker in user:
            raise Conflict(f'Duplicate migrated origin: {origin}')
        user += f'\n{marker}\n{content.rstrip()}\n'
    return (left + start + user + end + right).encode()


def separate_user(data):
    text = decode(data)
    start, end = '<!-- forgekit:user begin -->', '<!-- forgekit:user end -->'
    if start not in text and end not in text:
        return data, ''
    if text.count(start) != 1 or text.count(end) != 1 or text.index(start) > text.index(end):
        raise Conflict('Invalid user region')
    before, rest = text.split(start)
    user, after = rest.split(end)
    return (before + after).encode(), user


def merge_markdown(base, local, incoming):
    """Stable sections permit template reordering and user-only sections."""
    raw_local = local
    base, _ = separate_user(base)
    local, custom = separate_user(local)
    incoming, _ = separate_user(incoming)
    # Strip markers only for comparison with legacy unmarked baselines.
    b, l, n = sections(base), sections(local), sections(incoming)
    def by_heading(blocks):
        result = {}
        for key, body in blocks.items():
            heading = body.splitlines()[0] if body.startswith('## ') else '__preamble__'
            if heading in result:
                raise Conflict(f'Ambiguous heading: {heading}')
            result[heading] = (key, body)
        return result
    if '<!-- forgekit:section ' not in decode(base):
        nb = by_heading(n)
        def normalize(blocks):
            return {nb.get(h, (k, ''))[0]: v for h, (k, v) in by_heading(blocks).items()}
        b, l = normalize(b), normalize(l)
    out, extras = [], []
    for key, new in n.items():
        old = b.get(key)
        here = l.get(key)
        if old is None:
            if here is not None and here != new:
                raise Conflict(f'Both sides added section: {key}')
            merged = new
        elif here is None:
            if new != old:
                raise Conflict(f'Deleted locally but updated by template: {key}')
            continue
        else:
            try:
                merged = decode(merge_text(old.encode(), here.encode(), new.encode()))
            except Conflict as exc:
                raise Conflict(f'{key}: {exc}') from exc
        if key != '__preamble__':
            out.append(f'<!-- forgekit:section {key if re.fullmatch("[a-z0-9._-]+",key) else "s-"+digest(key.encode())[:12]} -->\n')
        out.append(merged)
    for key, here in l.items():
        if key not in n:
            if key in b and here.rstrip() != b[key].rstrip():
                raise Conflict(f'Customized section retired without mapping: {key}')
            if key not in b:
                extras.append(('local-' + digest(key.encode())[:12], here))
    result = ''.join(out).encode()
    if custom:
        result = user_region(result, [])
        text = decode(result).replace('<!-- forgekit:user begin -->\n', '<!-- forgekit:user begin -->' + custom)
        result = text.encode()
    if extras:
        result = user_region(result, extras)
    # No normalization for a completely unchanged template.
    return raw_local if base == incoming else result


def merge_entry(base, local, incoming):
    """Move local insertions to a user region; never silently replace edited rules."""
    old, _ = separate_user(base)
    here, custom = separate_user(local)
    a, b = decode(old).splitlines(keepends=True), decode(here).splitlines(keepends=True)
    additions = []
    for op, i, j, x, y in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == 'equal':
            continue
        if op == 'insert':
            additions.extend(b[x:y])
        elif ''.join(a[i:j]).strip() != ''.join(b[x:y]).strip():
            raise Conflict(f'Entry rules were replaced or deleted (first difference at baseline lines {i+1}-{j}); '
                           'review the whole entry, then use --entry-resolutions for an explicit preserved merge')
    result = user_region(incoming, [])
    text = decode(result).replace('<!-- forgekit:user begin -->\n', '<!-- forgekit:user begin -->' + (custom or '\n'))
    result = text.encode()
    added = ''.join(additions)
    if not added.strip():
        return result
    # Each migration step has its own provenance. Carry prior user-region origins
    # through unchanged; whitespace introduced by the region is not a new rule.
    origin = 'entry-' + digest(old + b'\0' + incoming + b'\0' + added.encode())[:16]
    return user_region(result, [(origin, added)])


def payload(migration, relative):
    path = PurePosixPath(relative)
    if path.is_absolute() or '..' in path.parts or '\\' in relative or ':' in relative:
        raise Conflict(f'Invalid migration payload: {relative}')
    root = migration['_path'].parent.resolve()
    target = root.joinpath(*path.parts)
    if target.is_symlink() or not target.resolve().is_relative_to(root):
        raise Conflict(f'Payload escapes package: {relative}')
    return target.read_bytes()


def rewrite_references(data, source, destination, moves):
    """Retarget Markdown links and exact path code spans, leaving fenced code opaque."""
    def mapped(value, link=False):
        path, sep, fragment = value.partition('#')
        if not path or re.match(r'^[a-z]+:', path, re.I) or path.startswith('/'):
            return value
        direct = path in moves
        resolved = path if direct else posixpath.normpath(posixpath.join(posixpath.dirname(source), path))
        if resolved not in moves and (not link or source == destination):
            return value
        replacement = moves.get(resolved, resolved)
        replacement = replacement if direct else posixpath.relpath(replacement, posixpath.dirname(destination) or '.')
        return replacement + sep + fragment
    result, fence = [], None
    for line in decode(data).splitlines(keepends=True):
        marker = re.match(r'^\s*(`{3,}|~{3,})', line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            result.append(line)
            continue
        if fence is None:
            line = re.sub(r'(?<!`)`([^`\n]+)`(?!`)', lambda m: '`' + mapped(m.group(1)) + '`', line)
            line = re.sub(r'(\]\()([^\s)]+)(\))', lambda m: m.group(1) + mapped(m.group(2), True) + m.group(3), line)
        result.append(line)
    return ''.join(result).encode()


def preserved_entry_candidate(local, incoming):
    """A review candidate, not an automatic assertion of rule compatibility."""
    # Nested user delimiters would make later upgrades misinterpret ownership.
    if any(marker in decode(local) for marker in ('<!-- forgekit:user begin -->', '<!-- forgekit:user end -->')):
        raise Conflict('Full-entry preservation requires an entry without existing user delimiters')
    return user_region(incoming, [('reviewed-entry-' + digest(local)[:16], decode(local))])


def load_entry_resolutions(path, root, state):
    if path is None:
        return {}, None
    path = Path(path).resolve()
    raw = path.read_bytes()
    packet = json.loads(decode(raw))
    if not isinstance(packet, dict) or packet.get('schema_version') != 1:
        raise Conflict('Invalid entry resolution schema')
    project = packet.get('project_root')
    if not isinstance(project, str) or not Path(project).is_absolute() or Path(project).resolve() != root:
        raise Conflict('Entry resolution belongs to a different project')
    if packet.get('from_version') != state['forgekit_version']:
        raise Conflict('Entry resolution source version changed')
    entries = packet.get('entries')
    if not isinstance(entries, list) or not entries:
        raise Conflict('Entry resolution requires a nonempty entries list')
    result = {}
    for item in entries:
        if not isinstance(item, dict):
            raise Conflict('Invalid entry resolution item')
        target = item.get('target')
        if target not in ('AGENTS.md', 'CLAUDE.md') or target in result:
            raise Conflict('Entry resolution target must be a unique AGENTS.md or CLAUDE.md')
        if not isinstance(item.get('migration_id'), str):
            raise Conflict('Entry resolution requires a migration ID')
        for key in ('local_sha256', 'incoming_sha256', 'resolved_sha256'):
            if not isinstance(item.get(key), str) or not re.fullmatch('[0-9a-f]{64}', item[key]):
                raise Conflict(f'Invalid entry resolution checksum: {key}')
        if not isinstance(item.get('resolved_text'), str):
            raise Conflict('Entry resolution requires resolved_text')
        candidate = item['resolved_text'].encode('utf-8')
        if digest(candidate) != item['resolved_sha256']:
            raise Conflict('Entry resolution candidate checksum mismatch')
        result[target] = {**item, 'candidate': candidate}
    return result, (path, raw)


def build_plan(root, state, migrations, entry_resolutions=None):
    root = Path(root).resolve()
    resolutions, resolution_input = load_entry_resolutions(entry_resolutions, root, state)
    resolved_entries = {}
    original, virtual, baselines, conflicts, moves = {}, {}, {}, [], []
    lock_updates, retired_lock = {}, {'README.md'}
    preserved_documents, failed_targets = [], set()
    new_state = copy.deepcopy(state)

    def read(relative):
        if relative not in original:
            path = safe_path(root, relative)
            original[relative] = path.read_bytes() if path.exists() else None
            virtual[relative] = original[relative]
        return virtual[relative]

    read('.forgekit/state.json')
    lock_data = read('.forgekit/template-lock.json')
    lock = json.loads(decode(lock_data)) if lock_data else {'schema_version': 2, 'files': []}
    if lock.get('schema_version') not in (1, 2):
        raise Conflict('Unsupported template lock schema')
    boundary_bytes = read('.forgekit/project-boundary.yml')
    boundary = decode(boundary_bytes) if boundary_bytes else ''
    match = re.search(r'^\s*managed_docs_root:\s*[\"\']?([^\r\n\"\']+)', boundary, re.M)
    docs_root = match.group(1).strip() if match else '.forgekit/docs'
    match = re.search(r'^\s*change_root:\s*[\"\']?([^\r\n\"\']+)', boundary, re.M)
    change_root = match.group(1).strip() if match else '.forgekit/changes'
    def actual(path):
        for default, configured in (('.forgekit/docs', docs_root), ('.forgekit/changes', change_root)):
            if path.startswith(default + '/'):
                return configured + path[len(default):]
        return path
    reference_moves = {actual(a['target']): actual(a['destinations']['*'])
                       for m in migrations for a in m['actions'] if a['type'] == 'relocate_markdown'}

    # Earlier releases did not migrate every template file. Their published
    # snapshots supply exact ancestry for files skipped by an intermediate step.
    known_templates, ancestor_ids, ancestor_blobs, lineage_initialized = {}, {}, {}, set()
    normalized_ancestors, raw_ancestors = {}, {}
    lock_by_path = {entry['target_path']: entry for entry in lock.get('files', [])}
    for migration in migrations:
        if migration.get('legacy_baselines'):
            catalog = json.loads(decode(payload(migration, migration['legacy_baselines'])))
            ancestor_blobs.update(catalog['blobs'])
            for version_paths in catalog['versions'].values():
                for path, checksum in version_paths.items():
                    ancestor_ids.setdefault(actual(path), set()).add(checksum)
            for path, checksums in catalog.get('artifacts', {}).items():
                ancestor_ids.setdefault(actual(path), set()).update(checksums)
            for path, checksum in catalog.get('versions', {}).get(state['forgekit_version'], {}).items():
                data = zlib.decompress(base64.b64decode(catalog['blobs'][checksum], validate=True))
                if digest(data) != checksum:
                    raise Conflict(f'Historical baseline checksum mismatch: {path}')
                known_templates[actual(path)] = data
    for path, checksums in ancestor_ids.items():
        normalized_ancestors[path], raw_ancestors[path] = {}, {}
        for checksum in sorted(checksums):
            data = zlib.decompress(base64.b64decode(ancestor_blobs[checksum], validate=True))
            if digest(data) != checksum:
                raise Conflict(f'Historical baseline checksum mismatch: {path}')
            normalized_ancestors[path][digest(decode(data).encode())] = data
            # Older installs recorded source/installed hashes after checkout conversion.
            canonical = decode(data).encode()
            for variant in (data, canonical, canonical.replace(b'\n', b'\r\n')):
                raw_ancestors[path][digest(variant)] = data
                raw_ancestors[path][digest(b'\xef\xbb\xbf' + variant)] = data

    def check_current(read_file):
        if not any(m.get('check_current_docs') for m in migrations):
            return []
        spec = importlib.util.spec_from_file_location('forgekit_current_integrity', Path(__file__).with_name('check-current-docs-integrity.py'))
        checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker)
        board = read_file(actual('.forgekit/docs/task-board.md'))
        intake = read_file(actual('.forgekit/docs/task-intake.md'))
        if board is None or intake is None:
            return ['Current task-board or task-intake is missing; restore current state before upgrading']
        sources = checker.real_source_records(decode(intake))
        return [f"Active task {task['id']} has an unresolved source backlink" for task in checker.active_tasks(decode(board))
                if not task['sources'] or any(source not in sources for source in task['sources'])]

    for problem in check_current(read):
        conflicts.append({'migration': 'preflight', 'target': docs_root, 'reason': problem})

    for migration in migrations:
        predecessors = migration.get('from', new_state['forgekit_version'])
        predecessors = predecessors if isinstance(predecessors, list) else [predecessors]
        if not any(p == '*' or p == new_state['forgekit_version'] for p in predecessors):
            raise Conflict('Migration chain does not match the current version')
        retired_lock.update(actual(p) for p in migration.get('template_lock', {}).get('retire_targets', []))
        for action in migration['actions']:
            kind = action['type']
            if kind == 'ensure_directory':
                continue
            if kind == 'set_state_feature':
                new_state.setdefault('features', {})[action['name']] = action['value']
                continue
            target = actual(action['target'])
            if target in failed_targets:
                continue
            try:
                local = read(target)
                base = payload(migration, action['baseline']) if action.get('baseline') else None
                if target not in lineage_initialized:
                    lineage_initialized.add(target)
                    entry = lock_by_path.get(target, {})
                    checksum = entry.get('source_checksum', '').removeprefix('sha256:')
                    if local is not None and digest(decode(local).encode()) in normalized_ancestors.get(target, {}):
                        known_templates[target] = local
                    elif checksum in raw_ancestors.get(target, {}):
                        known_templates[target] = raw_ancestors[target][checksum]
                    elif entry.get('baseline_b64'):
                        candidate = base64.b64decode(entry['baseline_b64'], validate=True)
                        if digest(candidate) != checksum:
                            raise Conflict('Stored baseline does not match its source checksum')
                        known_templates[target] = candidate
                if target in known_templates:
                    base = known_templates[target]
                incoming = payload(migration, action['source']) if action.get('source') else None
                if kind == 'relocate_markdown':
                    if local is None:
                        continue
                    if base is None:
                        raise Conflict('Relocation requires baseline')
                    base_body, _ = separate_user(base)
                    local_body, custom = separate_user(local)
                    def heading_sections(data):
                        result = {}
                        for key, body in sections(data).items():
                            heading = body.splitlines()[0][3:] if body.startswith('## ') else '__preamble__'
                            if heading in result:
                                raise Conflict(f'Ambiguous relocation heading: {heading}')
                            result[heading] = body
                        return result
                    b, l = heading_sections(base_body), heading_sections(local_body)
                    if custom.strip():
                        l['__user__'] = custom
                    destinations = action['destinations']
                    for heading, content in l.items():
                        if content.rstrip() == b.get(heading, '').rstrip():
                            continue
                        if action.get('rules_only') and heading in b:
                            # New rules may appear anywhere; edits to old rules need resolution.
                            old_lines = b[heading].rstrip().splitlines()
                            local_lines = content.rstrip().splitlines()
                            inserted = []
                            for op, i, j, x, y in difflib.SequenceMatcher(None, old_lines, local_lines, autojunk=False).get_opcodes():
                                if op == 'insert':
                                    inserted.extend(local_lines[x:y])
                                elif op != 'equal' and ''.join(old_lines[i:j]).strip() != ''.join(local_lines[x:y]).strip():
                                    raise Conflict(f'Customized retired rule: {heading}')
                            content = '\n'.join(inserted).strip()
                        if not content.strip():
                            continue
                        destination = actual(destinations.get(heading, destinations['*']))
                        content = decode(rewrite_references(content.encode(), target, destination, reference_moves))
                        dest = read(destination)
                        if dest is None:
                            raise Conflict(f'Missing relocation destination: {destination}')
                        origin = digest((target + '#' + heading).encode())[:16]
                        virtual[destination] = user_region(dest, [(origin, content)])
                        moves.append({'source': target, 'section': heading, 'target': destination, 'sha256': digest(content.encode())})
                    virtual[target] = None
                    known_templates.pop(target, None)
                elif kind == 'remove_file_if_baseline_matches':
                    if local not in (None, base):
                        raise Conflict('Customized retired file requires mapping')
                    virtual[target] = None
                    known_templates.pop(target, None)
                elif kind in ('replace_file_if_baseline_matches', 'merge_markdown', 'merge_entry', 'copy_file_if_missing'):
                    if incoming is None:
                        raise Conflict('Missing incoming payload')
                    resolution = resolutions.get(target)
                    if resolution and resolution['migration_id'] == migration['id']:
                        if target in resolved_entries:
                            raise Conflict('Entry resolution matched more than one action')
                        if digest(local) != resolution['local_sha256'] or digest(incoming) != resolution['incoming_sha256']:
                            raise Conflict('Entry resolution input changed; review a new candidate')
                        if local is None or resolution['candidate'] != preserved_entry_candidate(local, incoming):
                            raise Conflict('Entry resolution must preserve the full local entry under the incoming template')
                        virtual[target] = resolution['candidate']
                        resolved_entries[target] = resolution['candidate']
                    elif local is None or local == base or local == incoming or (base is not None and decode(local) == decode(base)):
                        virtual[target] = incoming
                    elif action.get('content_policy') == 'project_facts':
                        if target not in {docs_root + '/' + name + '.md' for name in PROJECT_FACT_DOCS}:
                            raise Conflict('Project-facts policy is outside the managed fact documents')
                        # Starter structure is not a contract for project-owned facts.
                        # Keep the whole document, including deliberately removed placeholders.
                        virtual[target] = local
                        preserved_documents.append(target)
                    elif base is None:
                        raise Conflict('Unknown baseline for existing file')
                    elif kind == 'merge_entry' or target in ('AGENTS.md', 'CLAUDE.md'):
                        virtual[target] = merge_entry(base, local, incoming)
                    elif target.endswith('.md'):
                        virtual[target] = merge_markdown(base, local, incoming)
                    else:
                        virtual[target] = merge_text(base, local, incoming)
                    baselines[target] = incoming
                    known_templates[target] = incoming
                    if 'lock_entry' in action:
                        lock_updates[target] = action['lock_entry']
                else:
                    raise Conflict(f'Unsupported action: {kind}')
            except (Conflict, UnicodeError, OSError, ValueError) as exc:
                failed_targets.add(target)
                conflicts.append({'migration': migration['id'], 'target': target, 'action': action.get('id'), 'reason': str(exc)})
        new_state['forgekit_version'] = migration['to']
        new_state.setdefault('features', {}).update(migration.get('features', {}))

    for migration in migrations:
        for relative in migration.get('reference_paths', []):
            path = actual(relative)
            try:
                value = read(path)
                if value is not None:
                    virtual[path] = rewrite_references(value, path, path, reference_moves)
            except (Conflict, OSError, ValueError) as exc:
                conflicts.append({'migration': migration['id'], 'target': path, 'reason': str(exc)})

    for target in resolutions:
        if target not in resolved_entries or virtual.get(target) != resolved_entries[target]:
            conflicts.append({'migration': 'resolution', 'target': target,
                              'reason': 'Entry resolution was not used or later actions changed the reviewed candidate'})

    for problem in check_current(read):
        conflicts.append({'migration': 'postflight', 'target': docs_root, 'reason': problem})

    by_target = {entry['target_path']: entry for entry in lock.get('files', [])}
    for path in retired_lock:
        by_target.pop(path, None)
    for path, baseline in baselines.items():
        if virtual.get(path) is None:
            continue
        entry = by_target.setdefault(path, {'target_path': path, 'source_path': path, 'role': 'managed_doc', 'render_mode': 'copy', 'update_policy': 'merge'})
        if path in lock_updates:
            entry.update({k: v for k, v in lock_updates[path].items() if k not in ('target_path', 'checksum')})
        entry.update(source_checksum='sha256:' + digest(baseline), installed_checksum='sha256:' + digest(virtual[path]),
                     baseline_b64=base64.b64encode(baseline).decode(), document_id=path)
    for path, value in virtual.items():
        if value is None:
            by_target.pop(path, None)
    lock.update(schema_version=2, installed_version=new_state['forgekit_version'], managed_docs_root=docs_root, change_root=change_root, files=list(by_target.values()))
    virtual['.forgekit/template-lock.json'] = (json.dumps(lock, ensure_ascii=False, indent=2) + '\n').encode()
    new_state['last_upgrade'] = {'from': state['forgekit_version'], 'to': new_state['forgekit_version'],
                                 'migrations': [m['id'] for m in migrations], 'mode': 'structured',
                                 'manual_merge_items': 0, 'review_needed_actions': []}
    virtual['.forgekit/state.json'] = (json.dumps(new_state, ensure_ascii=False, indent=2) + '\n').encode()
    writes = {p: value for p, value in virtual.items() if value != original[p]}
    public = {'schema_version': 2, 'from': state['forgekit_version'], 'to': new_state['forgekit_version'],
              'version_chain': [state['forgekit_version']] + [m['to'] for m in migrations],
              'status': 'conflict' if conflicts else ('ready' if writes else 'current'),
              'inputs': {p: digest(v) for p, v in original.items()},
              'actions': [{'target': p, 'operation': 'remove' if v is None else 'write', 'sha256': digest(v)} for p, v in writes.items()],
              'preserved': moves, 'preserved_documents': preserved_documents, 'conflicts': conflicts}
    if resolution_input:
        public['entry_resolution'] = {'packet_sha256': digest(resolution_input[1]), 'project_root': str(root),
                                     'entries': [{'target': p, 'sha256': digest(v)} for p, v in resolved_entries.items()]}
    public['plan_hash'] = digest(json.dumps(public, sort_keys=True, ensure_ascii=False).encode())
    return {'public': public, 'original': original, 'writes': writes, 'resolution_input': resolution_input}


def apply_plan(root, plan, expected_hash=None, fault=None):
    """Preflight all targets, persist rollback bytes, write state last, restore on error."""
    info = plan['public']
    if info['conflicts']:
        raise Conflict('Unresolved migration conflicts; no files changed')
    if expected_hash and expected_hash != info['plan_hash']:
        raise Conflict('Plan changed since confirmation; re-plan required')
    if plan.get('resolution_input'):
        path, raw = plan['resolution_input']
        if Path(root).resolve() != Path(info['entry_resolution']['project_root']) or path.read_bytes() != raw:
            raise Conflict('Entry resolution changed after planning; re-plan required')
    for relative, data in plan['original'].items():
        path = safe_path(root, relative)
        if (path.read_bytes() if path.exists() else None) != data:
            raise Conflict(f'File changed after planning: {relative}')
    fault = fault or (lambda stage: None)
    snapshot = plan['original']
    created_dirs, touched = [], []
    report_root = '.forgekit/reports/upgrades/' + uuid.uuid4().hex
    backup = {p: None if d is None else base64.b64encode(d).decode() for p, d in snapshot.items() if p in plan['writes']}
    result_info = {**info, 'status': 'applied', 'report': report_root + '/result.json'}
    additions = {report_root + '/rollback.json': (json.dumps({'schema_version': 1, 'files': backup}, ensure_ascii=False) + '\n').encode()}
    # The success report is installed after the state; a failed transaction removes it.
    final_report = report_root + '/result.json'
    snapshot = {**snapshot, final_report: None}
    report_bytes = (json.dumps(result_info, ensure_ascii=False, indent=2) + '\n').encode()
    writes = {**additions, **plan['writes'], final_report: report_bytes}
    order = sorted(writes, key=lambda p: (p == final_report, p not in additions, p == '.forgekit/state.json', p))
    try:
        for relative in order:
            path = safe_path(root, relative)
            if relative in snapshot and (path.read_bytes() if path.exists() else None) != snapshot[relative]:
                raise Conflict(f'Concurrent modification: {relative}')
            parents = []
            parent = path.parent
            while not parent.exists():
                parents.append(parent)
                parent = parent.parent
            for parent in reversed(parents):
                parent.mkdir()
                created_dirs.append(parent)
            data = writes[relative]
            touched.append(relative)
            if data is None:
                path.unlink(missing_ok=True)
            else:
                with path.open('wb') as handle:
                    handle.write(data)
                    handle.flush()
                    os.fsync(handle.fileno())
                if path.read_bytes() != data:
                    raise Conflict(f'Write verification failed: {relative}')
            fault('after_write:' + relative)
        fault('after_state_write')
    except BaseException as original_error:
        recovery_errors = []
        for relative in reversed(touched):
            if relative in additions:
                continue
            try:
                path = safe_path(root, relative)
                old = snapshot.get(relative)
                if old is None:
                    path.unlink(missing_ok=True)
                else:
                    path.write_bytes(old)
            except (OSError, Conflict) as recovery_error:
                recovery_errors.append(f'{relative}: {recovery_error}')
        if recovery_errors:
            raise Conflict(f'Upgrade failed: {original_error}; rollback incomplete: {recovery_errors}; recovery backup: {report_root}/rollback.json') from original_error
        for relative in additions:
            safe_path(root, relative).unlink(missing_ok=True)
        for directory in reversed(created_dirs):
            directory.rmdir()
        raise
    return result_info
