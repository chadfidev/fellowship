import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1]


class InstallTests(unittest.TestCase):
    def test_native_roles_and_unrelated_configuration_survive_repeat_install(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            codex = root / 'codex'
            claude = root / 'claude'
            codex.mkdir()
            claude.mkdir()
            (codex / 'AGENTS.md').write_text('Existing Codex instructions.\n')
            (codex / 'config.toml').write_text('model = "gpt-6.1-sol"\n')
            settings = {'theme': 'dark', 'hooks': {'Stop': [{'hooks': [{'type': 'command', 'command': 'existing-hook'}]}]}}
            (claude / 'settings.json').write_text(json.dumps(settings))
            (claude / 'CLAUDE.md').write_text('Existing Claude instructions.\n')
            command = [sys.executable, str(SOURCE / 'install.py'), 'install', '--codex-home', str(codex), '--claude-home', str(claude)]
            for _ in range(2):
                result = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            import tomllib
            roles = [tomllib.loads(p.read_text()) for p in (codex / 'agents').glob('*.toml')]
            self.assertEqual(len(roles), 12)
            self.assertEqual(next(r for r in roles if r['name'] == 'aragorn')['model'], 'gpt-6.1-sol')
            self.assertEqual(next(r for r in roles if r['name'] == 'frodo')['model'], 'gpt-6-luna')
            self.assertEqual(next(r for r in roles if r['name'] == 'frodo-important')['model'], 'gpt-6.1-sol')
            self.assertIn('model: opus', (claude / 'agents/aragorn.md').read_text())
            self.assertIn('model: haiku', (claude / 'agents/frodo.md').read_text())
            self.assertEqual((codex / 'config.toml').read_text(), 'model = "gpt-6.1-sol"\n')
            self.assertTrue((codex / 'AGENTS.md').read_text().startswith('Existing Codex instructions.\n'))
            self.assertEqual((codex / 'AGENTS.md').read_text().count('<!-- BEGIN FELLOWSHIP -->'), 1)
            updated = json.loads((claude / 'settings.json').read_text())
            self.assertEqual(updated['theme'], 'dark')
            self.assertEqual(updated['hooks']['Stop'][0], settings['hooks']['Stop'][0])
            self.assertEqual(len(updated['hooks']['Stop']), 2)
            self.assertIn('PostToolUseFailure', updated['hooks'])
            self.assertIn('PermissionDenied', updated['hooks'])
            updated['hooks']['Stop'][-1]['hooks'].append({'type': 'command', 'command': 'peer-hook-in-shared-group'})
            (claude / 'settings.json').write_text(json.dumps(updated))
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            children = [h for row in json.loads((claude / 'settings.json').read_text())['hooks']['Stop'] for h in row['hooks']]
            self.assertIn({'type': 'command', 'command': 'peer-hook-in-shared-group'}, children)
            self.assertFalse((root / 'opencode').exists())
            self.assertFalse((root / 'pi').exists())

    def test_unknown_owned_role_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            codex, claude = root / 'codex', root / 'claude'
            (codex / 'agents').mkdir(parents=True)
            (codex / 'agents/gandalf.toml').write_text('Existing personal Gandalf.\n')
            result = subprocess.run([sys.executable, str(SOURCE / 'install.py'), 'install', '--codex-home', str(codex), '--claude-home', str(claude)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((codex / 'agents/gandalf.toml').read_text(), 'Existing personal Gandalf.\n')

    def test_onboarding_is_repeatable_and_keeps_existing_instructions(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            subprocess.run(['git', 'init', '-q', str(repo)], check=True)
            (repo / 'AGENTS.md').write_text('Existing project boundaries.\n')
            (repo / '.gitignore').write_text('.claude/\nwork/\n')
            command = [sys.executable, str(SOURCE / 'install.py'), 'onboard', '--project', str(repo)]
            for _ in range(2):
                r = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue((repo / 'AGENTS.md').read_text().startswith('Existing project boundaries.\n'))
            self.assertEqual((repo / 'AGENTS.md').read_text().count('<!-- BEGIN FELLOWSHIP -->'), 1)
            self.assertEqual(len(list((repo / '.codex/agents').glob('*.toml'))), 12)
            self.assertNotIn(str(SOURCE), (repo / '.codex/agents/frodo.toml').read_text())
            self.assertFalse((repo / '.git/fellowship').exists())
            role_ignored = subprocess.run(['git', '-C', str(repo), 'check-ignore', '-q', '.claude/agents/gandalf.md'])
            self.assertNotEqual(role_ignored.returncode, 0)
            private_ignored = subprocess.run(['git', '-C', str(repo), 'check-ignore', '-q', '.claude/worktrees/private/file'])
            self.assertEqual(private_ignored.returncode, 0)


if __name__ == '__main__':
    unittest.main()
