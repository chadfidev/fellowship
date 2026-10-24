import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'skill/scripts/fellowship.py'


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / 'repo'
        self.repo.mkdir()
        self.env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True, env=self.env)
        (self.repo / '.fellowship').mkdir()
        (self.repo / '.fellowship/project.json').write_text(json.dumps({'version': 1, 'enabled': True}))

    def run_cli(self, *args, ok=True):
        r = subprocess.run([sys.executable, str(SCRIPT), *args, '--project', str(self.repo)], text=True, capture_output=True, env=self.env)
        if ok:
            self.assertEqual(r.returncode, 0, r.stderr)
            return json.loads(r.stdout)
        return r

    def hook(self, event, provider='codex', session='s1', **extra):
        payload = dict(hook_event_name=event, cwd=str(self.repo), session_id=session)
        payload.update(extra)
        r = subprocess.run([sys.executable, str(SCRIPT), 'hook', '--provider', provider], input=json.dumps(payload), text=True, capture_output=True, env=self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout or '{}')

    def test_bedtime_preserves_dirty_work_and_requires_all_active_acknowledgments(self):
        (self.repo / 'owned-wip.txt').write_text('unfinished work')
        self.hook('UserPromptSubmit', prompt='work on my assigned task')
        self.hook('UserPromptSubmit', provider='claude', session='s2', prompt='work on my assigned task')
        self.hook('UserPromptSubmit', prompt='bedtime')
        self.hook('Stop')
        state = self.run_cli('status')
        self.assertEqual(state['status'], 'stop-unconfirmed')
        self.assertIn('claude:s2', state['pending'])
        self.hook('Stop', provider='claude', session='s2')
        state = self.run_cli('status')
        self.assertEqual(state['status'], 'paused')
        self.assertEqual((self.repo / 'owned-wip.txt').read_text(), 'unfinished work')
        self.assertIn('owned-wip.txt', state['checkpoints']['codex:s1']['git_status'])

    def test_pause_denies_new_supported_work_and_does_not_resume_on_prose(self):
        self.run_cli('bedtime')
        r = self.hook('PreToolUse', tool_name='Bash', tool_use_id='t1', tool_input={'command': 'touch should-not-exist'})
        self.assertEqual(r['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertFalse((self.repo / 'should-not-exist').exists())
        self.hook('UserPromptSubmit', prompt='Explain how resume works; do not resume anything.')
        self.assertTrue(self.run_cli('status')['pause_requested'])
        self.hook('UserPromptSubmit', prompt='/fellowship resume')
        self.assertFalse(self.run_cli('status')['pause_requested'])

    def test_inflight_operation_is_not_mistaken_for_stopped(self):
        self.hook('PreToolUse', tool_name='Bash', tool_use_id='t1', tool_input={'command': 'long-operation'})
        self.run_cli('bedtime')
        self.hook('Stop')
        self.assertEqual(self.run_cli('status')['status'], 'stop-unconfirmed')
        self.hook('PostToolUse', tool_name='Bash', tool_use_id='t1', tool_input={})
        self.assertEqual(self.run_cli('status')['status'], 'paused')

    def test_corrupt_state_denies_work_and_is_preserved(self):
        self.run_cli('bedtime')
        state = self.repo / '.git/fellowship/state.json'
        state.write_text('{corrupt')
        r = self.hook('PreToolUse', tool_name='Bash', tool_use_id='t1', tool_input={'command': 'echo work'})
        self.assertEqual(r['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertEqual(state.read_text(), '{corrupt')

    def test_unenrolled_project_is_untouched(self):
        (self.repo / '.fellowship/project.json').unlink()
        self.assertEqual(self.hook('SessionStart'), {})
        self.assertFalse((self.repo / '.git/fellowship').exists())

    def test_worktree_uses_same_pause_state(self):
        subprocess.run(['git', '-C', str(self.repo), 'add', '.fellowship/project.json'], check=True, env=self.env)
        subprocess.run(['git', '-C', str(self.repo), '-c', 'user.name=Fellowship Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'fixture'], check=True, env=self.env)
        other = Path(self.temp.name) / 'other'
        subprocess.run(['git', '-C', str(self.repo), 'worktree', 'add', '-qb', 'worker', str(other)], check=True, env=self.env)
        self.run_cli('bedtime')
        r = subprocess.run([sys.executable, str(SCRIPT), 'status', '--project', str(other)], text=True, capture_output=True, env=self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(json.loads(r.stdout)['pause_requested'])

    def test_preexisting_worktree_without_marker_still_observes_primary_pause(self):
        subprocess.run(['git', '-C', str(self.repo), '-c', 'user.name=Fellowship Test', '-c', 'user.email=test@example.invalid', 'commit', '--allow-empty', '-qm', 'fixture before enrollment'], check=True, env=self.env)
        other = Path(self.temp.name) / 'old-worker'
        subprocess.run(['git', '-C', str(self.repo), 'worktree', 'add', '-qb', 'old-worker', str(other)], check=True, env=self.env)
        self.run_cli('bedtime')
        payload = {'hook_event_name': 'PreToolUse', 'cwd': str(other), 'session_id': 'old-worker', 'tool_name': 'Bash', 'tool_use_id': 't1', 'tool_input': {'command': 'touch bad'}}
        r = subprocess.run([sys.executable, str(SCRIPT), 'hook', '--provider', 'codex'], input=json.dumps(payload), text=True, capture_output=True, env=self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout).get('hookSpecificOutput', {}).get('permissionDecision'), 'deny')

    def test_pause_checkpoint_command_cannot_hide_shell_side_effects(self):
        self.run_cli('bedtime')
        import shlex
        for command in [shlex.join([sys.executable, str(SCRIPT), 'status', '--project', str(self.repo)]) + ' ; touch hidden',
                        f'{sys.executable} {SCRIPT} checkpoint --note "$(touch hidden)" --project {self.repo}']:
            r = self.hook('PreToolUse', tool_name='Bash', tool_use_id='t1', tool_input={'command': command})
            self.assertEqual(r.get('hookSpecificOutput', {}).get('permissionDecision'), 'deny')

    def test_malformed_session_metadata_fails_closed(self):
        self.run_cli('bedtime')
        p = self.repo / '.git/fellowship/state.json'
        data = json.loads(p.read_text())
        data['sessions']['codex:s1'] = {'state': 'active', 'inflight': []}
        p.write_text(json.dumps(data))
        r = self.hook('PreToolUse', tool_name='Bash', tool_use_id='t1', tool_input={'command': 'echo work'})
        self.assertEqual(r['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_native_subagent_lifecycle_does_not_leave_spawn_call_inflight(self):
        self.hook('PreToolUse', tool_name='collaborationspawn_agent', tool_use_id='spawn1', tool_input={})
        self.hook('SubagentStart', agent_id='child1', agent_type='legolas')
        self.hook('SubagentStop', agent_id='child1', agent_type='legolas')
        self.hook('Stop')
        self.run_cli('bedtime')
        self.assertEqual(self.run_cli('status')['status'], 'paused')

    def test_claude_failed_or_denied_tools_reach_confirmed_stop(self):
        for terminal in ('PostToolUseFailure', 'PermissionDenied'):
            self.hook('PreToolUse', provider='claude', tool_name='Read', tool_use_id=terminal, tool_input={})
            self.hook(terminal, provider='claude', tool_name='Read', tool_use_id=terminal, tool_input={})
        self.hook('Stop', provider='claude')
        self.run_cli('bedtime')
        self.assertEqual(self.run_cli('status')['status'], 'paused')

    def test_claude_background_child_does_not_reactivate_stopped_parent(self):
        self.hook('UserPromptSubmit', provider='claude', prompt='Do the bounded read-only task.')
        self.hook('SubagentStart', provider='claude', agent_id='c1', agent_type='legolas')
        self.hook('Stop', provider='claude')
        self.hook('PreToolUse', provider='claude', agent_id='c1', tool_name='Read', tool_use_id='c-read', tool_input={})
        self.hook('PostToolUse', provider='claude', agent_id='c1', tool_name='Read', tool_use_id='c-read', tool_input={})
        self.hook('SubagentStop', provider='claude', agent_id='c1', agent_type='legolas')
        self.run_cli('bedtime')
        self.assertEqual(self.run_cli('status')['status'], 'paused')

    def test_child_stop_checkpoints_observed_worktree(self):
        subprocess.run(['git', '-C', str(self.repo), 'add', '.fellowship/project.json'], check=True, env=self.env)
        subprocess.run(['git', '-C', str(self.repo), '-c', 'user.name=Fellowship Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'fixture'], check=True, env=self.env)
        other = Path(self.temp.name) / 'child-worktree'
        subprocess.run(['git', '-C', str(self.repo), 'worktree', 'add', '-qb', 'child', str(other)], check=True, env=self.env)
        (other / 'child-wip.txt').write_text('preserve me')
        self.hook('SubagentStart', agent_id='c1')
        self.hook('PreToolUse', agent_id='c1', cwd=str(other), tool_name='Read', tool_use_id='r1', tool_input={})
        self.hook('PostToolUse', agent_id='c1', cwd=str(other), tool_name='Read', tool_use_id='r1', tool_input={})
        self.hook('SubagentStop', agent_id='c1')
        state = self.run_cli('status')
        checkpoint = state['checkpoints']['codex:c1']
        self.assertEqual(Path(checkpoint['worktree']).resolve(), other.resolve())
        self.assertIn('child-wip.txt', checkpoint['git_status'])
        self.assertEqual((other / 'child-wip.txt').read_text(), 'preserve me')
        self.hook('SubagentStart', agent_id='c1')
        self.hook('PreToolUse', agent_id='c1', cwd=str(other), tool_name='Read', tool_use_id='r2', tool_input={})
        self.hook('PostToolUse', agent_id='c1', cwd=str(other), tool_name='Read', tool_use_id='r2', tool_input={})
        subprocess.run(['git', '-C', str(self.repo), 'worktree', 'remove', '--force', str(other)], check=True, env=self.env)
        result = self.hook('SubagentStop', agent_id='c1')
        self.assertIn('unconfirmed', result.get('systemMessage', ''))
        self.run_cli('bedtime')
        self.assertEqual(self.run_cli('status')['status'], 'stop-unconfirmed')
        self.assertIn('child-wip.txt', self.run_cli('status')['checkpoints']['codex:c1']['git_status'])

    def test_child_checkpoint_rejects_checkout_in_other_repository(self):
        self.hook('SubagentStart', agent_id='c1')
        other = Path(self.temp.name) / 'unrelated'
        subprocess.run(['git', 'init', '-q', str(other)], check=True, env=self.env)
        self.run_cli('bedtime')
        p = self.repo / '.git/fellowship/state.json'
        state = json.loads(p.read_text())
        state['sessions']['codex:c1']['worktree'] = str(other)
        p.write_text(json.dumps(state))
        result = self.hook('SubagentStop', agent_id='c1')
        self.assertIn('unconfirmed', result.get('systemMessage', ''))
        self.assertEqual(self.run_cli('status')['status'], 'stop-unconfirmed')
        self.assertNotIn('codex:c1', self.run_cli('status')['checkpoints'])

    def test_paused_guard_accepts_only_matching_owned_project_helper(self):
        target = self.repo / '.fellowship/scripts/fellowship.py'
        target.parent.mkdir()
        shutil.copyfile(SCRIPT, target)
        self.run_cli('bedtime')
        import shlex
        command = shlex.join([sys.executable, str(target), 'checkpoint', '--project', str(self.repo), '--note', 'Preserve the task intent.'])
        r = self.hook('PreToolUse', tool_name='Bash', tool_use_id='checkpoint1', tool_input={'command': command})
        self.assertNotEqual(r.get('hookSpecificOutput', {}).get('permissionDecision'), 'deny')
        self.hook('PostToolUse', tool_name='Bash', tool_use_id='checkpoint1', tool_input={})
        target.write_text(target.read_text() + '\nprint("unreviewed project helper")\n')
        r = self.hook('PreToolUse', tool_name='Bash', tool_use_id='checkpoint2', tool_input={'command': command})
        self.assertEqual(r.get('hookSpecificOutput', {}).get('permissionDecision'), 'deny')

    def test_nonobject_enrollment_fails_closed(self):
        for value in ([], None):
            (self.repo / '.fellowship/project.json').write_text(json.dumps(value))
            r = self.hook('PreToolUse', tool_name='Bash', tool_use_id='t1', tool_input={'command': 'echo work'})
            self.assertEqual(r.get('hookSpecificOutput', {}).get('permissionDecision'), 'deny')


if __name__ == '__main__':
    unittest.main()
