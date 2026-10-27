"""Install Fellowship into Codex/Claude Code without replacing unrelated state."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent
SKILL = HERE / 'skill' if (HERE / 'skill').is_dir() else HERE.parent
MODEL_PATH = HERE / 'models.json' if (HERE / 'models.json').is_file() else SKILL / 'models.json'
BEGIN, END = '<!-- BEGIN FELLOWSHIP -->', '<!-- END FELLOWSHIP -->'
ROLES = {
    'gandalf': ('gandalf', 'economy', 'Coordinate routine approved scope, assignments, integration, and bedtime; escalate consequential decisions.'),
    'elrond': ('elrond', 'economy', 'Plan routine designs and acceptance; use a strong model for consequential architecture or interfaces.'),
    'bilbo': ('bilbo', 'economy', 'Write bounded task briefs and maintain source-attributed handoffs.'),
    'legolas': ('legolas', 'economy', 'Answer a focused codebase or primary-source research question.'),
    'frodo': ('workers', 'coder', 'Implement one bounded ordinary task in an owned checkout.'),
    'sam': ('workers', 'coder', 'Implement one bounded ordinary task independently of peer workers.'),
    'frodo-important': ('workers', 'strong', 'Frodo with a strong model for consequential or ambiguous implementation.'),
    'sam-important': ('workers', 'strong', 'Sam with a strong model for consequential or ambiguous implementation.'),
    'gimli': ('gimli', 'economy', 'Run specified isolated checks and report reproducible verification evidence.'),
    'aragorn': ('aragorn', 'strong', 'Review the exact implementation revision independently; return source fixes to its author.'),
    'galadriel': ('galadriel', 'strong', 'Assess a security-sensitive boundary within the authorized review scope.'),
    'eowyn': ('eowyn', 'strong', 'Assess observable user experience and accessibility; the user owns product acceptance.')
}
EVENTS = ['SessionStart', 'UserPromptSubmit', 'PreToolUse', 'PostToolUse', 'SubagentStart', 'SubagentStop', 'Stop', 'SessionEnd']


def sha(content):
    return hashlib.sha256(content).hexdigest()


def write_atomic(path, content):
    path = Path(path)
    if path.is_symlink():
        raise ValueError(f'Refusing to replace a symlink: {path}')
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o600
    fd, temporary = tempfile.mkstemp(prefix='.fellowship-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def block(path, text, begin=BEGIN, end=END, expected_hash=None):
    path = Path(path)
    if path.is_symlink():
        raise ValueError(f'Refusing instruction symlink: {path}')
    path = path.resolve()
    original = path.read_bytes() if path.exists() else b''
    begin_bytes, end_bytes = begin.encode(), end.encode()
    if original.count(begin_bytes) != original.count(end_bytes) or original.count(begin_bytes) > 1:
        raise ValueError(f'Ambiguous Fellowship instruction block: {path}')
    new = f'{begin}\n{text.strip()}\n{end}'.encode()
    if begin_bytes in original:
        left, rest = original.split(begin_bytes, 1)
        managed, right = rest.split(end_bytes, 1)
        current = begin_bytes + managed + end_bytes
        if expected_hash is None and current != new:
            raise ValueError(f'Existing Fellowship instruction block has no verifiable ownership; preserve it: {path}')
        if expected_hash is not None and sha(current) != expected_hash:
            raise ValueError(f'Fellowship instruction block was independently modified; preserve it: {path}')
        updated = left + new + right
    else:
        if expected_hash is not None:
            raise ValueError(f'Fellowship instruction block was removed independently; preserve it: {path}')
        updated = original + (b'\n' if original.endswith(b'\n') else b'\n\n' if original else b'') + new + b'\n'
    return path, updated

def block_hash(content, begin=BEGIN, end=END):
    begin_bytes, end_bytes = begin.encode(), end.encode()
    if content.count(begin_bytes) != 1 or content.count(end_bytes) != 1:
        raise ValueError('Cannot record ambiguous Fellowship block')
    start = content.index(begin_bytes)
    finish = content.index(end_bytes) + len(end_bytes)
    return sha(content[start:finish])


def model_policy():
    data = json.loads(MODEL_PATH.read_text())
    for profile in ('strong', 'economy', 'coder', 'medium'):
        row = data['profiles'][profile]
        if not all(isinstance(row.get(key), str) and row[key] and row[key] == row[key].strip() for key in ('codex', 'claude', 'effort')):
            raise ValueError('Each model profile needs nonempty, trimmed codex, claude, and effort strings')
        for provider in ('codex', 'claude'):
            model = row[provider].lower()
            if 'astra' in model or 'fable' in model or model == 'inherit':
                raise ValueError('Astra, Fable, and inherited routes are not authorized in Fellowship native model routing')
        if any(model in row['codex'].lower() for model in ('luna', 'sol')) and row['effort'] != 'high':
            raise ValueError('Luna and Sol model profiles must use high reasoning effort')
    return data


def native_roles(provider, reference, policy):
    rendered = {}
    for name, (role, profile, description) in ROLES.items():
        refs = f'If .fellowship/pack exists in the checkout, read its protocol.md and roles/{role}.md; otherwise read {reference}/protocol.md and {reference}/roles/{role}.md. '
        instructions = (f'You are {name}, a Fellowship agent. ' + refs +
            'Read current project instructions and the approved task packet. The packet is your brief; do not restart approved planning. '
            'Preserve peer work. Only Gandalf dispatches or integrates. Return unresolved decisions to the coordinator. '
            'Fellowship owns coordination, routing, handoff, and bedtime. '
            'On bedtime checkpoint promptly and stop; leave review, merges, and new work for explicit resume. '
            'Use important worker variants for important tasks; changing persona does not establish review independence. '
            f'Routine coordination and planning use the configured economy model at high effort. For ordinary worker tasks only, medium-complexity Claude work may use the configured medium profile ({policy["profiles"]["medium"]["claude"]}); Codex routine work remains Luna at high effort. Reviewers retain their strong profile, and consequential decisions use strong. Never propagate an override into child/helper calls. ' +
            'Native permissions and current user instructions prevail. Never route worker, reviewer, retry, fallback, or other child/helper calls through Astra or Fable. Preserve the user-selected main-session model and authentication route.')
        model = policy['profiles'][profile][provider]
        if provider == 'codex':
            fields = {'name': name, 'description': description, 'model': model,
                      'model_reasoning_effort': policy['profiles'][profile]['effort'], 'developer_instructions': instructions}
            rendered[f'agents/{name}.toml'] = ('# Fellowship managed; regenerate with install.py.\n' + '\n'.join(f'{key} = {json.dumps(value, ensure_ascii=False)}' for key, value in fields.items()) + '\n').encode()
        else:
            tools = 'Read, Grep, Glob, WebSearch, WebFetch' if name == 'legolas' else 'Read, Grep, Glob' if name in ('elrond', 'aragorn', 'galadriel', 'eowyn') else None
            front = f'---\nname: {name}\ndescription: {json.dumps(description)}\nmodel: {model}\n'
            if tools:
                front += f'tools: {tools}\n'
            rendered[f'agents/{name}.md'] = (front + '---\n\n<!-- Fellowship managed; regenerate with install.py. -->\n\n' + instructions + '\n').encode()
    return rendered


def skill_files(policy):
    files = {}
    for p in SKILL.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc' and p.name != 'install-receipt.json':
            files[f'skills/fellowship/{p.relative_to(SKILL)}'] = p.read_bytes()
    files['skills/fellowship/models.json'] = (json.dumps(policy, indent=2) + '\n').encode()
    files['skills/fellowship/scripts/install.py'] = Path(__file__).read_bytes()
    return files


def preflight(root, files, receipt_path=None):
    receipt_path = receipt_path or root / 'skills/fellowship/install-receipt.json'
    if receipt_path.is_symlink():
        raise ValueError(f'Refusing install receipt symlink: {receipt_path}')
    old = json.loads(receipt_path.read_text())['files'] if receipt_path.exists() else {}
    for relative, content in files.items():
        path = root / relative
        parent = path.parent
        while parent != root:
            if parent.is_symlink():
                raise ValueError(f'Refusing managed-file symlink ancestor: {parent}')
            parent = parent.parent
        if path.is_symlink():
            raise ValueError(f'Refusing managed-file symlink: {path}')
        if path.exists() and path.read_bytes() != content and old.get(relative) != sha(path.read_bytes()):
            raise ValueError(f'Unknown or independently modified file; preserve it: {path}')


def references_helper(command, script):
    if not isinstance(command, str):
        return False
    path = str(script)
    return path in command or shlex.quote(path) in command

def hook_config(existing, script, provider, previous_hook=None, previous_command=None):
    config = json.loads(json.dumps(existing))
    command = shlex.join([sys.executable, str(script), 'hook', '--provider', provider])
    managed_hook = {'type': 'command', 'command': command, 'timeout': 3}
    events = EVENTS + (['PostToolUseFailure', 'PermissionDenied'] if provider == 'claude' else [])
    for event in events:
        replaced_prior = False
        rows = config.setdefault('hooks', {}).setdefault(event, [])
        kept_rows = []
        for row in rows:
            children = row.get('hooks', [])
            kept = []
            for hook in children:
                owned = previous_hook is not None and hook == previous_hook
                if previous_hook is None and previous_command and hook == {'type': 'command', 'command': previous_command, 'timeout': 3}:
                    owned = True
                if owned and not replaced_prior:
                    replaced_prior = True
                    kept.append(managed_hook)
                    continue
                if references_helper(hook.get('command'), script) and not owned:
                    raise ValueError(f'Fellowship hook was customized or is unowned; preserve it: {event}')
                kept.append(hook)
            if kept:
                kept_rows.append(dict(row, hooks=kept))
            elif len(kept) != len(children):
                kept_rows.append(dict(row, hooks=[]))
            else:
                kept_rows.append(row)
        rows[:] = kept_rows
        if not any(any(hook == managed_hook for hook in row.get('hooks', [])) for row in rows):
            rows.append({'hooks': [managed_hook]})
    return config, managed_hook

def app_receipt(root):
    safe_owned_paths(root, ['skills/fellowship/install-receipt.json'])
    path = root / 'skills/fellowship/install-receipt.json'
    if path.is_symlink():
        raise ValueError(f'Refusing install receipt symlink: {path}')
    return json.loads(path.read_text()) if path.is_file() else {}

def install(codex, claude, apps):
    policy = model_policy()
    plans = []
    candidates = {'codex': (Path(codex).resolve(), 'AGENTS.md'), 'claude': (Path(claude).resolve(), 'CLAUDE.md')}
    for provider in apps:
        root, instruction_name = candidates[provider]
        receipt = app_receipt(root)
        managed = receipt.get('managed', {})
        files = skill_files(policy)
        files.update(native_roles(provider, root / 'skills/fellowship/references', policy))
        preflight(root, files)
        instruction = ('For coding in a Git repository, or a new code project intended for Git, use Fellowship: read ' +
            str(root / 'skills/fellowship/SKILL.md') + '. The main assistant is Gandalf. Delegate independent bounded work when useful; use at most two coding workers and an independent strong Aragorn review. '
            'An approved packet is the worker brief; preserve existing user approvals. Fellowship governs coordination/model routing/handoffs/bedtime. Never route worker, reviewer, retry, fallback, or other child/helper calls through Astra or Fable; preserve the user-selected main-session model and authentication route. '
            'Bedtime means checkpoint promptly and stop, leaving review and merging for explicit resume. Preserve current project boundaries. No skill expands authority or overrides native policy or current user instructions.')
        instruction_target = root / instruction_name
        prior_instruction = instruction_target.read_bytes() if instruction_target.is_file() else b''
        had_block = BEGIN.encode() in prior_instruction
        settings = root / ('hooks.json' if provider == 'codex' else 'settings.json')
        if settings.is_symlink():
            raise ValueError(f'Refusing active settings symlink: {settings}')
        instruction_path, instruction_bytes = block(instruction_target, instruction, expected_hash=managed.get('instruction'))
        instruction_created = managed.get('instruction_created', not instruction_target.exists())
        prefix_hex = managed.get('instruction_prefix')
        suffix_hex = managed.get('instruction_suffix')
        if prefix_hex is None:
            prefix = b'' if had_block else (b'\n' if prior_instruction.endswith(b'\n') else b'\n\n' if prior_instruction else b'')
            suffix = b'' if had_block else b'\n'
        else:
            prefix, suffix = bytes.fromhex(prefix_hex), bytes.fromhex(suffix_hex or '')
        config = json.loads(settings.read_text()) if settings.exists() else {}
        command = managed.get('hook_command')
        previous_hook = managed.get('hook')
        if previous_hook is None and command:
            previous_hook = {'type': 'command', 'command': command, 'timeout': 3}
        updated, hook = hook_config(config, root / 'skills/fellowship/scripts/fellowship.py', provider, previous_hook, command)
        plans.append((provider, root, files, instruction_path, instruction_bytes, settings, updated, hook, instruction_created, prefix, suffix))
    for provider, root, files, instruction_path, instruction_bytes, settings, updated, hook, instruction_created, prefix, suffix in plans:
        for relative, content in files.items():
            write_atomic(root / relative, content)
        write_atomic(instruction_path, instruction_bytes)
        write_atomic(settings, (json.dumps(updated, indent=2) + '\n').encode())
        begin, end_marker = BEGIN.encode(), END.encode()
        block_start = instruction_bytes.index(begin)
        block_end = instruction_bytes.index(end_marker, block_start) + len(end_marker)
        block_text = instruction_bytes[block_start:block_end]
        write_atomic(root / 'skills/fellowship/install-receipt.json', (json.dumps({'version': 1, 'files': {p: sha(data) for p, data in files.items()}, 'managed': {'instruction': sha(block_text), 'hook': hook, 'hook_command': hook['command'], 'instruction_created': instruction_created, 'instruction_prefix': prefix.hex(), 'instruction_suffix': suffix.hex()}}, indent=2) + '\n').encode())
    return {'installed': apps, 'native_profiles_per_app': len(ROLES), 'other_apps_changed': False}

def safe_owned_paths(root, files):
    for relative in files:
        relative_path = Path(relative)
        if relative_path.is_absolute() or not relative_path.parts or '..' in relative_path.parts:
            raise ValueError(f'Invalid managed path in install receipt: {relative}')
        path = root / relative_path
        parent = path.parent
        while parent != root:
            if parent.is_symlink():
                raise ValueError(f'Refusing uninstall through symlink ancestor: {parent}')
            parent = parent.parent
        if path.is_symlink():
            raise ValueError(f'Refusing uninstall symlink: {path}')

def uninstall(home, provider):
    root = Path(home).resolve()
    receipt_path = root / 'skills/fellowship/install-receipt.json'
    safe_owned_paths(root, ['skills/fellowship/install-receipt.json'])
    if not receipt_path.is_file():
        return {'uninstalled': provider, 'removed': 0, 'modified_preserved': 0, 'receipt_found': False}
    receipt = json.loads(receipt_path.read_text())
    files = receipt.get('files')
    if receipt.get('version') != 1 or not isinstance(files, dict):
        raise ValueError(f'Invalid install receipt: {receipt_path}')
    safe_owned_paths(root, [*files, 'skills/fellowship/install-receipt.json'])
    managed = receipt.get('managed', {})
    instruction_name = 'AGENTS.md' if provider == 'codex' else 'CLAUDE.md'
    instruction_path = root / instruction_name
    settings = root / ('hooks.json' if provider == 'codex' else 'settings.json')
    for active_path in (instruction_path, settings):
        if active_path.is_symlink():
            raise ValueError(f'Refusing uninstall through active configuration symlink; preserve installation assets: {active_path}')
    if instruction_path.is_file():
        content = instruction_path.read_bytes()
        begin, end_marker = BEGIN.encode(), END.encode()
        if begin in content or end_marker in content:
            if content.count(begin) != 1 or content.count(end_marker) != 1:
                raise ValueError(f'Fellowship instruction block is ambiguous; preserve installation assets: {instruction_path}')
            start = content.index(begin)
            end = content.index(end_marker) + len(end_marker)
            if not managed.get('instruction') or sha(content[start:end]) != managed['instruction']:
                raise ValueError(f'Fellowship instruction block was modified; preserve installation assets: {instruction_path}')
    command = managed.get('hook_command')
    owned_hook = managed.get('hook') or {'type': 'command', 'command': command, 'timeout': 3}
    helper_script = root / 'skills/fellowship/scripts/fellowship.py'
    if settings.is_file() and command:
        config = json.loads(settings.read_text())
        for rows in config.get('hooks', {}).values():
            for row in rows:
                if any(references_helper(hook.get('command'), helper_script) and hook != owned_hook for hook in row.get('hooks', [])):
                    raise ValueError(f'Fellowship hook was customized; preserve installation assets and reconcile it first: {settings}')
    removed = modified = 0
    if instruction_path.is_file() and not instruction_path.is_symlink():
        content = instruction_path.read_bytes()
        begin, end_marker = BEGIN.encode(), END.encode()
        if content.count(begin) == content.count(end_marker) == 1:
            start = content.index(begin)
            end = content.index(end_marker) + len(end_marker)
            if sha(content[start:end]) == managed.get('instruction'):
                left, right = content[:start], content[end:]
                prefix = bytes.fromhex(managed.get('instruction_prefix', ''))
                suffix = bytes.fromhex(managed.get('instruction_suffix', ''))
                if prefix and left.endswith(prefix):
                    left = left[:-len(prefix)]
                if suffix and right.startswith(suffix):
                    right = right[len(suffix):]
                remaining = left + right
                if managed.get('instruction_created') and not remaining:
                    instruction_path.unlink()
                else:
                    write_atomic(instruction_path, remaining)
                removed += 1
            else:
                modified += 1
        else:
            modified += 1
    if settings.is_file():
        config = json.loads(settings.read_text())
        settings_changed = False
        for event, rows in config.get('hooks', {}).items():
            kept_rows = []
            for row in rows:
                children = row.get('hooks', [])
                kept = [hook for hook in children if hook != owned_hook]
                changed = len(children) != len(kept)
                settings_changed |= changed
                if changed and row != {'hooks': [owned_hook]}:
                    kept_rows.append(dict(row, hooks=kept))
                elif not changed:
                    kept_rows.append(row)
            if len(kept_rows) != len(rows) or any(a != b for a, b in zip(kept_rows, rows)):
                config['hooks'][event] = kept_rows
        if settings_changed:
            write_atomic(settings, (json.dumps(config, indent=2) + '\n').encode())
    for relative, expected in files.items():
        path = root / relative
        if path.is_file() and sha(path.read_bytes()) == expected:
            path.unlink()
            removed += 1
        elif path.exists():
            modified += 1
    if receipt_path.exists():
        receipt_path.unlink()
        removed += 1
    for directory in sorted({(root / name).parent for name in files}, key=lambda p: len(p.parts), reverse=True):
        try:
            directory.rmdir()
        except OSError:
            pass
    return {'uninstalled': provider, 'removed': removed, 'modified_preserved': modified, 'receipt_found': True}


def onboard(path):
    root = Path(subprocess.run(['git', '-C', str(Path(path).resolve()), 'rev-parse', '--show-toplevel'], check=True, capture_output=True, text=True).stdout.strip()).resolve()
    owned = root / '.fellowship'
    marker = owned / 'project.json'
    if owned.is_symlink():
        raise ValueError('Refusing symlinked project enrollment')
    if owned.exists() and not marker.exists():
        raise ValueError('Existing .fellowship directory has unknown ownership')
    policy = model_policy()
    files = {'.fellowship/pack/' + str(p.relative_to(SKILL / 'references')): p.read_bytes() for p in (SKILL / 'references').rglob('*') if p.is_file()}
    files['.fellowship/models.json'] = (json.dumps(policy, indent=2) + '\n').encode()
    files['.fellowship/scripts/fellowship.py'] = (SKILL / 'scripts/fellowship.py').read_bytes()
    files['.fellowship/project.json'] = b'{"version": 1, "enabled": true}\n'
    files['.fellowship/README.md'] = ('''# Fellowship project entrypoint

Read existing project instructions and the latest governing execution boundary first. This setup does not resume feature work. Use `pack/protocol.md`, your role under `pack/roles/`, the existing task ledger, and current handoff; keep historical claims separate.

The main assistant is Gandalf. Model routing is pinned in `models.json`; important worker variants use strong models. Existing user approvals persist. Fellowship governs coordination/routing/handoff/bedtime. A role is not additional authorization.

Local control: `python3 .fellowship/scripts/fellowship.py status --project .` or `checkpoint --project . --note 'next action'` uses the project helper when it matches the trusted installed helper. Use `bedtime --project .` to pause. In a paused hooked chat, the user must send the standalone `resume fellowship` command (or supported `/fellowship resume`); longer prose does not implicitly clear the guard and the agent cannot self-resume through Bash. From the user's own terminal, `resume --project .` is available after deciding to resume. Registered native sessions share pause state across local worktrees in the Git common directory. Hooks block supported new work while paused; they do not kill processes or guarantee remote shutdown. Preserve rich task intent/next actions in the project's current handoff as well as mechanical checkpoints.

Codex/Claude global installs supply lifecycle hooks. A collaborator can load the project-local native roles and contracts from a clean clone; install their own trusted hooks before claiming cooperative pause enforcement. Each collaborator uses their own credentials. Do not share private saves or account state.
''').encode()
    for provider, directory in [('codex', '.codex'), ('claude', '.claude')]:
        for relative, content in native_roles(provider, '.fellowship/pack', policy).items():
            files[f'{directory}/{relative}'] = content
    receipt_path = owned / 'install-receipt.json'
    if owned.exists() and not receipt_path.exists():
        raise ValueError('Existing project enrollment has no ownership receipt; preserve it')
    prior = json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
    previous_blocks = prior.get('managed', {}).get('blocks', {})
    preflight(root, files, receipt_path)
    message = 'Fellowship is installed for this project: read `.fellowship/README.md` before coding, delegating, resuming, or handling bedtime. Preserve the latest project execution boundary; this onboarding does not resume feature work. Approved task packets are worker briefs. Fellowship controls coordination/routing/handoff/bedtime.'
    blocks = []
    for name in ['AGENTS.md', 'CLAUDE.md']:
        target, content = block(root / name, message, expected_hash=previous_blocks.get(name))
        blocks.append((name, target, content, BEGIN, END))
    ignored = subprocess.run(['git', '-C', str(root), 'check-ignore', '--stdin'], input='\n'.join(f'.claude/agents/{name}.md' for name in ROLES) + '\n', capture_output=True, text=True)
    if ignored.returncode not in (0, 1):
        raise ValueError('Cannot inspect project ignore rules')
    if ignored.returncode == 0:
        if (root / '.gitignore').is_symlink():
            raise ValueError('Project ignore file is a symlink; preserve it for explicit review')
        patterns = ['!/.claude/', '/.claude/*', '!/.claude/agents/', '/.claude/agents/*'] + [f'!/.claude/agents/{name}.md' for name in ROLES]
        target, content = block(root / '.gitignore', '\n'.join(patterns), '# BEGIN FELLOWSHIP AGENTS', '# END FELLOWSHIP AGENTS', expected_hash=previous_blocks.get('.gitignore'))
        blocks.append(('.gitignore', target, content, '# BEGIN FELLOWSHIP AGENTS', '# END FELLOWSHIP AGENTS'))
    for relative, content in files.items():
        write_atomic(root / relative, content)
    block_digests = {}
    for name, target, content, begin, end in blocks:
        write_atomic(target, content)
        block_digests[name] = block_hash(content, begin, end)
    write_atomic(receipt_path, (json.dumps({'version': 1, 'files': {p: sha(data) for p, data in files.items()}, 'managed': {'blocks': block_digests}}, indent=2) + '\n').encode())
    return {'project': str(root), 'enrolled': True, 'native_profiles_per_app': len(ROLES), 'application_source_changed': False}


def selected_apps(args):
    if args.app:
        return ['codex', 'claude'] if args.app == 'both' else [args.app]
    explicit = []
    if args.codex_home is not None:
        explicit.append('codex')
    if args.claude_home is not None:
        explicit.append('claude')
    if explicit:
        return explicit
    existing = [name for name, path in (('codex', Path(os.environ.get('CODEX_HOME', Path.home() / '.codex'))), ('claude', Path(Path.home() / '.claude'))) if path.is_dir()]
    if len(existing) == 1:
        return existing
    raise ValueError('Cannot safely select an application; pass --app codex, --app claude, or --app both')

def main():
    if sys.version_info < (3, 11):
        print('Fellowship requires Python 3.11 or newer', file=sys.stderr)
        return 2
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['install', 'uninstall', 'onboard'])
    parser.add_argument('--app', choices=['codex', 'claude', 'both'])
    parser.add_argument('--codex-home')
    parser.add_argument('--claude-home')
    parser.add_argument('--project')
    args = parser.parse_args()
    codex_home = args.codex_home or os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))
    claude_home = args.claude_home or str(Path.home() / '.claude')
    try:
        if args.action == 'onboard':
            if not args.project:
                raise ValueError('onboard requires --project')
            result = onboard(args.project)
        else:
            apps = selected_apps(args)
            if args.action == 'install':
                result = install(codex_home, claude_home, apps)
            else:
                homes = {'codex': codex_home, 'claude': claude_home}
                result = {'results': [uninstall(homes[app], app) for app in apps]}
        print(json.dumps(result))
        return 0
    except (ValueError, OSError, subprocess.SubprocessError, KeyError, json.JSONDecodeError) as exc:
        print(f'Fellowship: {exc}', file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
