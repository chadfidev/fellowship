import json
import os
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
        payload = dict(hook_event_name=event, cwd=str(self.repo), session_id=session, **extra)
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


if __name__ == '__main__':
    unittest.main()
