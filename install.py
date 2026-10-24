"""Install Fellowship into Codex/Claude Code without replacing unrelated state."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent
SKILL = HERE / 'skill' if (HERE / 'skill').is_dir() else HERE.parent
MODEL_PATH = HERE / 'models.json' if (HERE / 'models.json').is_file() else SKILL / 'models.json'
BEGIN, END = '<!-- BEGIN FELLOWSHIP -->', '<!-- END FELLOWSHIP -->'
ROLES = {
    'gandalf': ('gandalf', 'strong', 'Coordinate approved scope, assignments, integration, and bedtime.'),
    'elrond': ('elrond', 'strong', 'Plan consequential designs, interfaces, dependencies, and acceptance.'),
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


def block(path, text, begin=BEGIN, end=END):
    path = Path(path).resolve()
    original = path.read_text() if path.exists() else ''
    if original.count(begin) != original.count(end) or original.count(begin) > 1:
        raise ValueError(f'Ambiguous Fellowship instruction block: {path}')
    new = f'{begin}\n{text.strip()}\n{end}'
    if begin in original:
        left, rest = original.split(begin, 1)
        _, right = rest.split(end, 1)
        updated = left + new + right
    else:
        updated = original + ('\n' if original.endswith('\n') else '\n\n' if original else '') + new + '\n'
    return path, updated.encode()


def model_policy():
    data = json.loads(MODEL_PATH.read_text())
    for profile in ('strong', 'economy', 'coder'):
        row = data['profiles'][profile]
        if not all(isinstance(row.get(key), str) and row[key] for key in ('codex', 'claude', 'effort')):
            raise ValueError('Each model profile needs codex, claude, and effort strings')
        if 'astra' in row['codex'].lower():
            raise ValueError('Astra is not authorized for this Fellowship installation')
    return data


def native_roles(provider, reference, policy):
    rendered = {}
    for name, (role, profile, description) in ROLES.items():
        refs = f'If .fellowship/pack exists in the checkout, read its protocol.md and roles/{role}.md; otherwise read {reference}/protocol.md and {reference}/roles/{role}.md. '
        instructions = (f'You are {name}, a Fellowship agent. ' + refs +
            'Read current project instructions and the approved task packet. The packet is your brief; do not restart approved planning. '
            'Preserve peer work. Only Gandalf dispatches or integrates. Return unresolved decisions to the coordinator. '
            'Fellowship owns coordination, routing, handoff, and bedtime; use Superpowers techniques within the approved task and Ponytail restraint. '
            'On bedtime checkpoint promptly and stop; leave review, merges, and new work for explicit resume. '
            'Use important worker variants for important tasks; changing persona does not establish review independence. '
            'Native permissions and current user instructions prevail. Never choose Astra without explicit current active user selection.')
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


def hook_config(existing, script, provider):
    config = json.loads(json.dumps(existing))
    command = shlex.join([shutil.which('python3') or sys.executable, str(script), 'hook', '--provider', provider])
    group = {'hooks': [{'type': 'command', 'command': command, 'timeout': 3}]}
    for event in EVENTS:
        rows = config.setdefault('hooks', {}).setdefault(event, [])
        preserved = []
        for row in rows:
            children = [h for h in row.get('hooks', []) if not str(h.get('command', '')).endswith(f'{shlex.quote(str(script))} hook --provider {provider}')]
            if children:
                preserved.append(dict(row, hooks=children))
        rows[:] = preserved
        if group not in rows:
            rows.append(group)
    return config


def install(codex, claude):
    policy = model_policy()
    plans = []
    for provider, root, instruction_name in [('codex', Path(codex).resolve(), 'AGENTS.md'), ('claude', Path(claude).resolve(), 'CLAUDE.md')]:
        files = skill_files(policy)
        files.update(native_roles(provider, root / 'skills/fellowship/references', policy))
        preflight(root, files)
        instruction = ('For coding in a Git repository, or a new code project intended for Git, use Fellowship: read ' +
            str(root / 'skills/fellowship/SKILL.md') + '. The main assistant is Gandalf. Delegate independent bounded work when useful; use at most two coding workers and an independent strong Aragorn review. '
            'An approved packet is the worker brief; preserve existing user approvals. Fellowship governs coordination/model routing/handoffs/bedtime; Superpowers provides task-relevant techniques and Ponytail keeps implementation and staffing small. '
            'Bedtime means checkpoint promptly and stop, leaving review and merging for explicit resume. Preserve current project boundaries. No skill expands authority or overrides native policy or current user instructions.')
        instruction_path, instruction_bytes = block(root / instruction_name, instruction)
        settings = root / ('hooks.json' if provider == 'codex' else 'settings.json')
        config = json.loads(settings.read_text()) if settings.exists() else {}
        updated = hook_config(config, root / 'skills/fellowship/scripts/fellowship.py', provider)
        plans.append((root, files, instruction_path, instruction_bytes, settings, updated))
    for root, files, instruction_path, instruction_bytes, settings, updated in plans:
        for relative, content in files.items():
            write_atomic(root / relative, content)
        write_atomic(instruction_path, instruction_bytes)
        write_atomic(settings, (json.dumps(updated, indent=2) + '\n').encode())
        write_atomic(root / 'skills/fellowship/install-receipt.json', (json.dumps({'version': 1, 'files': {p: sha(data) for p, data in files.items()}}, indent=2) + '\n').encode())
    return {'installed': ['codex', 'claude'], 'native_profiles_per_app': len(ROLES), 'other_apps_changed': False}


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

The main assistant is Gandalf. Model routing is pinned in `models.json`; important worker variants use strong models. Existing user approvals persist. Fellowship governs coordination/routing/handoff/bedtime; Superpowers techniques and Ponytail restraint apply within the approved task. A role is not additional authorization.

Local control: `python3 .fellowship/scripts/fellowship.py status --project .`, `bedtime --project .`, or `resume --project .` after explicit user resume. Registered native sessions share pause state across local worktrees in the Git common directory. Hooks block supported new work while paused; they do not kill processes or guarantee remote shutdown. Preserve rich task intent/next actions in the project's current handoff as well as mechanical checkpoints.

Codex/Claude global installs supply lifecycle hooks. A collaborator can load the project-local native roles and contracts from a clean clone; install their own trusted hooks before claiming cooperative pause enforcement. Each collaborator uses their own credentials. Do not share private saves or account state.
''').encode()
    for provider, directory in [('codex', '.codex'), ('claude', '.claude')]:
        for relative, content in native_roles(provider, '.fellowship/pack', policy).items():
            files[f'{directory}/{relative}'] = content
    receipt_path = owned / 'install-receipt.json'
    if owned.exists() and not receipt_path.exists():
        raise ValueError('Existing project enrollment has no ownership receipt; preserve it')
    preflight(root, files, receipt_path)
    blocks = [block(root / name, 'Fellowship is installed for this project: read `.fellowship/README.md` before coding, delegating, resuming, or handling bedtime. Preserve the latest project execution boundary; this onboarding does not resume feature work. Approved task packets are worker briefs. Fellowship controls coordination/routing/handoff/bedtime; Superpowers techniques and Ponytail restraint apply inside that scope.') for name in ['AGENTS.md', 'CLAUDE.md']]
    ignored = subprocess.run(['git', '-C', str(root), 'check-ignore', '--stdin'], input='\n'.join(f'.claude/agents/{name}.md' for name in ROLES) + '\n', capture_output=True, text=True)
    if ignored.returncode not in (0, 1):
        raise ValueError('Cannot inspect project ignore rules')
    if ignored.returncode == 0:
        if (root / '.gitignore').is_symlink():
            raise ValueError('Project ignore file is a symlink; preserve it for explicit review')
        patterns = ['!/.claude/', '/.claude/*', '!/.claude/agents/', '/.claude/agents/*'] + [f'!/.claude/agents/{name}.md' for name in ROLES]
        blocks.append(block(root / '.gitignore', '\n'.join(patterns), '# BEGIN FELLOWSHIP AGENTS', '# END FELLOWSHIP AGENTS'))
    for relative, content in files.items():
        write_atomic(root / relative, content)
    for target, content in blocks:
        write_atomic(target, content)
    write_atomic(receipt_path, (json.dumps({'version': 1, 'files': {p: sha(data) for p, data in files.items()}}, indent=2) + '\n').encode())
    return {'project': str(root), 'enrolled': True, 'native_profiles_per_app': len(ROLES), 'application_source_changed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['install', 'onboard'])
    parser.add_argument('--codex-home', default=os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
    parser.add_argument('--claude-home', default=str(Path.home() / '.claude'))
    parser.add_argument('--project')
    args = parser.parse_args()
    try:
        if args.action == 'onboard' and not args.project:
            raise ValueError('onboard requires --project')
        print(json.dumps(install(args.codex_home, args.claude_home) if args.action == 'install' else onboard(args.project)))
        return 0
    except (ValueError, OSError, subprocess.SubprocessError, KeyError) as exc:
        print(f'Fellowship: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
