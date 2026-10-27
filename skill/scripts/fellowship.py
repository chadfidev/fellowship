"""Local, cooperative Fellowship checkpoints and native lifecycle hooks."""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import time


def now():
    return datetime.now(timezone.utc).isoformat()


def git(cwd, *args):
    return subprocess.run(['git', '-C', str(cwd), *args], check=True, capture_output=True, text=True, timeout=10).stdout.strip()


def project(cwd):
    root = Path(git(Path(cwd).resolve(), 'rev-parse', '--show-toplevel')).resolve()
    common = Path(git(root, 'rev-parse', '--path-format=absolute', '--git-common-dir')).resolve()
    marker = root / '.fellowship/project.json'
    if not marker.exists() and common.name == '.git':
        marker = common.parent / '.fellowship/project.json'
    if marker.is_symlink():
        raise ValueError('Fellowship enrollment marker must not be a symlink')
    if not marker.is_file():
        return None
    config = json.loads(marker.read_text())
    if not isinstance(config, dict) or config.get('version') != 1 or config.get('enabled') is not True:
        raise ValueError('Unsupported or disabled Fellowship enrollment')
    return root, common / 'fellowship'


def atomic(path, data):
    if path.is_symlink():
        raise ValueError('Refusing a symlink in Fellowship state')
    fd, name = tempfile.mkstemp(prefix='.fellowship-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(json.dumps(data, indent=2) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


@contextmanager
def locked(directory):
    if directory.is_symlink():
        raise ValueError('Refusing symlinked Fellowship state directory')
    directory.mkdir(mode=0o700, exist_ok=True)
    lock = directory / 'state.lock'
    fd = os.open(lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'a+') as stream:
        deadline = time.monotonic() + 1.5
        while True:
            try:
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise ValueError('Fellowship state lock is busy; stop status is unconfirmed')
                time.sleep(0.02)
        path = directory / 'state.json'
        if path.is_symlink():
            raise ValueError('Refusing symlinked Fellowship state')
        state = json.loads(path.read_text()) if path.exists() else {
            'version': 1, 'pause_requested': False, 'sessions': {}, 'checkpoints': {}
        }
        if (not isinstance(state, dict) or state.get('version') != 1
                or type(state.get('pause_requested')) is not bool
                or not isinstance(state.get('sessions'), dict)
                or not isinstance(state.get('checkpoints'), dict)):
            raise ValueError('Invalid Fellowship state; preserve it for recovery')
        if any(not isinstance(row, dict) or not isinstance(row.get('inflight'), dict)
               or row.get('state') not in ('active', 'idle') for row in state['sessions'].values()):
            raise ValueError('Invalid Fellowship session metadata; preserve it for recovery')
        yield state
        atomic(path, state)


def snapshot(root, note=''):
    head = subprocess.run(['git', '-C', str(root), 'rev-parse', '--verify', '--quiet', 'HEAD'], capture_output=True, text=True, timeout=10)
    if head.returncode not in (0, 1):
        raise ValueError('Cannot inspect repository HEAD for checkpoint')
    return {'utc': now(), 'worktree': str(root), 'head': head.stdout.strip() if head.returncode == 0 else None,
            'git_status': git(root, 'status', '--short'), 'note': note[:2000]}


def status(state):
    pending = [key for key, row in state['sessions'].items()
               if row.get('state') == 'active' or row.get('inflight')]
    return dict(state, pending=pending, status=(
        'active' if not state['pause_requested'] else 'stop-unconfirmed' if pending else 'paused'))


def context(event, text):
    return {'hookSpecificOutput': {'hookEventName': event, 'additionalContext': text}}


def deny(reason):
    return {'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': 'deny', 'permissionDecisionReason': reason}}


def checkpoint_control(payload, root):
    if payload.get('tool_name') not in ('Bash', 'exec_command'):
        return False
    try:
        command = payload.get('tool_input', {}).get('command', payload.get('tool_input', {}).get('cmd', ''))
        if any(char in command for char in '$`;&|\n<>'):
            return False
        parts = shlex.split(command)
    except (ValueError, TypeError):
        return False
    if len(parts) < 3 or parts[0] not in ('python3', sys.executable, shutil.which('python3')):
        return False
    candidate = Path(parts[1]).resolve()
    trusted = Path(__file__).resolve()
    local = root / '.fellowship/scripts/fellowship.py'
    if candidate != trusted and (local.is_symlink() or candidate != local or not local.is_file() or local.read_bytes() != trusted.read_bytes()):
        return False
    if parts[2] not in ('status', 'checkpoint'):
        return False
    parser = cli_parser()
    try:
        parsed = parser.parse_args(parts[2:])
        return parsed.action in ('status', 'checkpoint') and Path(git(parsed.project, 'rev-parse', '--show-toplevel')).resolve() == root
    except SystemExit:
        return False


def hook(payload, provider):
    event = payload.get('hook_event_name', '')
    cwd = payload.get('cwd')
    if not isinstance(cwd, str):
        return deny('Fellowship hook received no working directory') if event == 'PreToolUse' else {}
    try:
        enrolled = project(cwd)
    except subprocess.CalledProcessError:
        return {}
    if enrolled is None:
        return {}
    root, directory = enrolled
    session = payload.get('session_id')
    if not isinstance(session, str) or not session:
        raise ValueError('Fellowship hook received no session identity')
    identity = f'{provider}:{session}'
    if event in ('PreToolUse', 'PostToolUse', 'PostToolUseFailure', 'PermissionDenied') and payload.get('agent_id'):
        identity = f"{provider}:{payload['agent_id']}"
    with locked(directory) as state:
        row = state['sessions'].setdefault(identity, {'state': 'idle', 'inflight': {}, 'worktree': str(root)})
        row['last_seen'] = now()
        if event in ('PreToolUse', 'PostToolUse', 'PostToolUseFailure', 'PermissionDenied'):
            row['worktree'] = str(root)
        if event == 'UserPromptSubmit':
            row['state'] = 'active'
            prompt = payload.get('prompt', '').strip().lower().rstrip('.!')
            if prompt in ('bedtime', '/bedtime', '/fellowship bedtime'):
                state['pause_requested'] = True
                state['pause_requested_at'] = now()
            elif prompt in ('/fellowship resume', 'resume fellowship'):
                state['pause_requested'] = False
                state['resumed_at'] = now()
        elif event == 'SubagentStart':
            child = payload.get('agent_id')
            if child:
                state['sessions'][f'{provider}:{child}'] = {
                    'state': 'active', 'inflight': {}, 'parent': identity,
                    'worktree': str(root), 'last_seen': now()}
        elif event == 'SubagentStop':
            child = payload.get('agent_id')
            child_row = state['sessions'].get(f'{provider}:{child}')
            if child_row:
                checkout = project(child_row['worktree'])
                if checkout is None or checkout[1] != directory:
                    raise ValueError('Child checkout is unavailable or belongs to a different repository')
                state['checkpoints'][f'{provider}:{child}'] = snapshot(checkout[0], 'Native subagent stop; inspect its task packet and native history on resume.')
                child_row['state'] = 'idle'
        elif event == 'PreToolUse':
            tool = payload.get('tool_name', '')
            permitted = tool in ('Read', 'Glob', 'Grep', 'read', 'glob', 'grep', 'interrupt_agent', 'list_agents', 'wait_agent', 'collaborationinterrupt_agent', 'collaborationlist_agents', 'collaborationwait_agent') or checkpoint_control(payload, root)
            if state['pause_requested'] and not permitted:
                return deny('Fellowship bedtime is active. Checkpoint promptly and stop; leave review, dispatch, merging, and new work for explicit resume.')
            tool_id = payload.get('tool_use_id')
            row['state'] = 'active'
            # Spawn lifetime is tracked by SubagentStart/Stop, not its creation call.
            if tool_id and tool not in ('Agent', 'spawn_agent', 'collaborationspawn_agent'):
                row['inflight'][str(tool_id)] = payload.get('tool_name', 'unknown')
        elif event in ('PostToolUse', 'PostToolUseFailure', 'PermissionDenied'):
            row['inflight'].pop(str(payload.get('tool_use_id', '')), None)
        elif event in ('Stop', 'SessionEnd', 'Interrupt'):
            row['state'] = 'idle'
            state['checkpoints'][identity] = snapshot(root, 'Native stop checkpoint. Preserve the listed checkout; resume only authorized scope and consult the task packet.')
        if state['pause_requested'] and event in ('SessionStart', 'UserPromptSubmit', 'SubagentStart', 'PostToolUse', 'PostToolUseFailure'):
            return context(event, 'Fellowship bedtime is active: checkpoint promptly and stop. Do not start review, merge, or new work. Unacknowledged sessions or in-flight operations remain stop-unconfirmed. Application services are separate. Send the standalone user command resume fellowship to continue.')
        if event == 'SessionStart':
            return context(event, 'Fellowship project enrolled. For coding, read .fellowship/README.md and preserve the current project execution boundary. Keep planning and staffing proportionate to the approved outcome. Unrelated chat and document work do not require the coding workflow. This session is registered for local cooperative pause.')
    return {}


def cli_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['status', 'bedtime', 'resume', 'checkpoint', 'hook'])
    parser.add_argument('--project', default=os.getcwd())
    parser.add_argument('--provider', choices=['codex', 'claude'])
    parser.add_argument('--session', default='manual')
    parser.add_argument('--note', default='')
    return parser


def main():
    args = cli_parser().parse_args()
    payload = {}
    try:
        if args.action == 'hook':
            payload = json.load(sys.stdin)
            if not isinstance(payload, dict) or not args.provider:
                raise ValueError('Hook needs a provider and JSON object')
            result = hook(payload, args.provider)
        else:
            enrolled = project(args.project)
            if enrolled is None:
                raise ValueError('Project is not enrolled in Fellowship')
            root, directory = enrolled
            with locked(directory) as state:
                if args.action in ('bedtime', 'resume'):
                    state['pause_requested'] = args.action == 'bedtime'
                    state['last_control_at'] = now()
                if args.action in ('bedtime', 'checkpoint'):
                    state['checkpoints'][args.session] = snapshot(root, args.note)
                result = status(state)
        print(json.dumps(result))
        return 0
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        if args.action == 'hook':
            if payload.get('hook_event_name') == 'PreToolUse':
                print(json.dumps(deny(f'Fellowship state could not be verified: {exc}')))
            else:
                print(json.dumps({'systemMessage': f'Fellowship checkpoint/stop status is unconfirmed: {exc}'}))
            return 0
        print(f'Fellowship: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
