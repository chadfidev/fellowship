import json
import io
import os
import shlex
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


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
            self.assertEqual(sorted(r['name'] for r in roles), ['aragorn', 'frodo', 'frodo-important', 'galadriel', 'gandalf'])
            self.assertEqual(next(r for r in roles if r['name'] == 'aragorn')['model'], 'gpt-6.1-sol')
            self.assertIn('Astra or Fable', next(r for r in roles if r['name'] == 'gandalf')['developer_instructions'])
            for name in ('gandalf', 'frodo'):
                role = next(r for r in roles if r['name'] == name)
                self.assertEqual(role['model'], 'gpt-6-luna', name)
                self.assertEqual(role['model_reasoning_effort'], 'high', name)
            self.assertEqual(next(r for r in roles if r['name'] == 'frodo-important')['model'], 'gpt-6.1-sol')
            aragorn, frodo = (claude / 'agents/aragorn.md').read_text(), (claude / 'agents/frodo.md').read_text()
            self.assertIn('model: opus\neffort: high\n', aragorn)
            self.assertIn('model: haiku\neffort: medium\n', frodo)
            self.assertNotIn('protocol.md', frodo)
            self.assertTrue((claude / 'skills/fellowship/references/roles/workers.md').is_file())
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

    def test_selected_app_installs_only_that_home_and_uninstall_preserves_edits(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            codex, claude = root / 'codex', root / 'claude'
            codex.mkdir()
            claude.mkdir()
            command = [sys.executable, str(SOURCE / 'install.py'), 'install', '--app', 'codex', '--codex-home', str(codex), '--claude-home', str(claude)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((codex / 'skills/fellowship/install-receipt.json').is_file())
            self.assertFalse((claude / 'skills').exists())
            managed = codex / 'skills/fellowship/models.json'
            managed.write_text('user edit\n')
            result = subprocess.run([sys.executable, str(SOURCE / 'install.py'), 'uninstall', '--app', 'codex', '--codex-home', str(codex)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(managed.read_text(), 'user edit\n')
            self.assertFalse((codex / 'skills/fellowship/scripts/fellowship.py').exists())
            self.assertFalse((codex / 'AGENTS.md').exists())

    def test_ambiguous_detection_and_forbidden_routing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            home = root / 'home'
            (home / '.codex').mkdir(parents=True)
            (home / '.claude').mkdir()
            result = subprocess.run([sys.executable, str(SOURCE / 'install.py'), 'install'], capture_output=True, text=True, env={**__import__('os').environ, 'HOME': str(home), 'CODEX_HOME': str(home / '.codex')})
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Cannot safely select', result.stderr)
            import importlib.util
            spec = importlib.util.spec_from_file_location('fellowship_install', SOURCE / 'install.py')
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            policy = json.loads((SOURCE / 'models.json').read_text())
            policy_path = root / 'models.json'
            module.MODEL_PATH = policy_path
            for provider, forbidden in (('claude', 'fable'), ('codex', 'astra'), ('codex', 'inherit'), ('claude', 'inherit')):
                changed = json.loads(json.dumps(policy))
                changed['profiles']['coder'][provider] = forbidden
                policy_path.write_text(json.dumps(changed))
                with self.assertRaisesRegex(ValueError, 'not authorized'):
                    module.model_policy()
            changed = json.loads(json.dumps(policy))
            changed['profiles']['coder']['effort'] = 'low'
            policy_path.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, 'high reasoning effort'):
                module.model_policy()
            changed = json.loads(json.dumps(policy))
            changed['profiles']['coder']['claude_effort'] = 'extreme'
            policy_path.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, 'claude_effort'):
                module.model_policy()

    def test_reinstall_removes_retired_unedited_files_and_keeps_edited_ones(self):
        with tempfile.TemporaryDirectory() as temp:
            claude = Path(temp) / 'claude'
            claude.mkdir()
            command = [sys.executable, str(SOURCE / 'install.py'), 'install', '--app', 'claude', '--claude-home', str(claude)]
            self.assertEqual(subprocess.run(command, capture_output=True, text=True).returncode, 0)
            receipt_path = claude / 'skills/fellowship/install-receipt.json'
            receipt = json.loads(receipt_path.read_text())
            retired, edited = claude / 'agents/elrond.md', claude / 'agents/bilbo.md'
            retired.write_text('old managed role\n')
            edited.write_text('user edit\n')
            receipt['files']['agents/elrond.md'] = __import__('hashlib').sha256(b'old managed role\n').hexdigest()
            receipt['files']['agents/bilbo.md'] = __import__('hashlib').sha256(b'original\n').hexdigest()
            receipt_path.write_text(json.dumps(receipt))
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(retired.exists())
            self.assertEqual(edited.read_text(), 'user edit\n')
            self.assertEqual(json.loads(result.stdout)['retired_preserved'], [str((claude / 'agents/bilbo.md').resolve())])
            self.assertNotIn('agents/elrond.md', json.loads(receipt_path.read_text())['files'])

    def test_auto_detection_selects_only_one_existing_home_and_rejects_none(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp) / 'home'
            (home / '.codex').mkdir(parents=True)
            env = {**__import__('os').environ, 'HOME': str(home), 'CODEX_HOME': str(home / '.codex')}
            result = subprocess.run([sys.executable, str(SOURCE / 'install.py'), 'install'], capture_output=True, text=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((home / '.codex/skills/fellowship/install-receipt.json').is_file())
            self.assertFalse((home / '.claude').exists())
            (home / '.codex').rename(home / 'codex-moved')
            env['CODEX_HOME'] = str(home / '.codex')
            result = subprocess.run([sys.executable, str(SOURCE / 'install.py'), 'install'], capture_output=True, text=True, env=env)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Cannot safely select', result.stderr)

    def test_modified_instruction_block_is_refused_on_update(self):
        with tempfile.TemporaryDirectory() as temp:
            codex = Path(temp) / 'codex'
            codex.mkdir()
            command = [sys.executable, str(SOURCE / 'install.py'), 'install', '--app', 'codex', '--codex-home', str(codex)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            instructions = codex / 'AGENTS.md'
            instructions.write_text(instructions.read_text().replace('Bedtime means', 'Personally edited: bedtime means'))
            edited = instructions.read_bytes()
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('independently modified', result.stderr)
            self.assertEqual(instructions.read_bytes(), edited)
            uninstall = [sys.executable, str(SOURCE / 'install.py'), 'uninstall', '--app', 'codex', '--codex-home', str(codex)]
            result = subprocess.run(uninstall, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('instruction block was modified', result.stderr)
            self.assertTrue((codex / 'skills/fellowship/scripts/fellowship.py').exists())

    def test_uninstall_restores_existing_instruction_bytes_exactly(self):
        with tempfile.TemporaryDirectory() as temp:
            codex = Path(temp) / 'codex'
            codex.mkdir()
            instructions = codex / 'AGENTS.md'
            original = b'Existing user instructions.\r\n\r\n'
            instructions.write_bytes(original)
            install = [sys.executable, str(SOURCE / 'install.py'), 'install', '--app', 'codex', '--codex-home', str(codex)]
            result = subprocess.run(install, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            uninstall = [sys.executable, str(SOURCE / 'install.py'), 'uninstall', '--app', 'codex', '--codex-home', str(codex)]
            result = subprocess.run(uninstall, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(instructions.read_bytes(), original)

    def test_uninstall_preserves_empty_groups_and_rejects_symlink_or_traversal_receipts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            codex = root / 'codex'
            codex.mkdir()
            settings = codex / 'hooks.json'
            settings.write_text(json.dumps({'hooks': {'Stop': [{'matcher': 'peer', 'hooks': []}]}}))
            install = [sys.executable, str(SOURCE / 'install.py'), 'install', '--app', 'codex', '--codex-home', str(codex)]
            result = subprocess.run(install, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            uninstall = [sys.executable, str(SOURCE / 'install.py'), 'uninstall', '--app', 'codex', '--codex-home', str(codex)]
            result = subprocess.run(uninstall, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(settings.read_text())['hooks']['Stop'], [{'matcher': 'peer', 'hooks': []}])

            receipt = codex / 'skills/fellowship/install-receipt.json'
            receipt.parent.mkdir(parents=True, exist_ok=True)
            outside = root / 'outside.json'
            outside.write_text(json.dumps({'version': 1, 'files': {}}))
            receipt.symlink_to(outside)
            result = subprocess.run(uninstall, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(outside.exists())
            receipt.unlink()
            receipt.write_text(json.dumps({'version': 1, 'files': {'.': '0' * 64}}))
            result = subprocess.run(uninstall, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(outside.exists())

    def test_install_refuses_settings_symlink_before_mutating_owned_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            codex = root / 'codex'
            codex.mkdir()
            command = [sys.executable, str(SOURCE / 'install.py'), 'install', '--app', 'codex', '--codex-home', str(codex)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            receipt = codex / 'skills/fellowship/install-receipt.json'
            receipt_before = receipt.read_bytes()
            managed = codex / 'skills/fellowship/models.json'
            managed_before = managed.read_bytes()
            settings = codex / 'hooks.json'
            target = root / 'external-settings.json'
            external = settings.read_bytes()
            settings.rename(target)
            settings.symlink_to(target)
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('active settings symlink', result.stderr)
            self.assertEqual(receipt.read_bytes(), receipt_before)
            self.assertEqual(managed.read_bytes(), managed_before)
            self.assertEqual(target.read_bytes(), external)

    def test_uninstall_refuses_active_settings_or_instruction_symlinks_before_mutation(self):
        for active_name in ('hooks.json', 'AGENTS.md'):
            with self.subTest(active_name=active_name), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                codex = root / 'codex'
                codex.mkdir()
                install = [sys.executable, str(SOURCE / 'install.py'), 'install', '--app', 'codex', '--codex-home', str(codex)]
                result = subprocess.run(install, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                active = codex / active_name
                target = root / f'dotfile-{active_name}'
                original = active.read_bytes()
                active.rename(target)
                active.symlink_to(target)
                uninstall = [sys.executable, str(SOURCE / 'install.py'), 'uninstall', '--app', 'codex', '--codex-home', str(codex)]
                result = subprocess.run(uninstall, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('active configuration symlink', result.stderr)
                self.assertTrue((codex / 'skills/fellowship/install-receipt.json').exists())
                self.assertTrue((codex / 'skills/fellowship/scripts/fellowship.py').exists())
                self.assertEqual(target.read_bytes(), original)

    def test_update_refuses_to_remove_customized_hook(self):
        with tempfile.TemporaryDirectory() as temp:
            codex = Path(temp) / 'codex'
            codex.mkdir()
            command = [sys.executable, str(SOURCE / 'install.py'), 'install', '--app', 'codex', '--codex-home', str(codex)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            settings = codex / 'hooks.json'
            config = json.loads(settings.read_text())
            hook = config['hooks']['Stop'][-1]['hooks'][0]
            hook['timeout'] = 9
            settings.write_text(json.dumps(config))
            edited = settings.read_bytes()
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('hook was customized or is unowned', result.stderr)
            self.assertEqual(settings.read_bytes(), edited)
            uninstall = [sys.executable, str(SOURCE / 'install.py'), 'uninstall', '--app', 'codex', '--codex-home', str(codex)]
            result = subprocess.run(uninstall, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('hook was customized', result.stderr)
            preserved = json.loads(settings.read_text())['hooks']['Stop'][-1]['hooks'][0]
            self.assertEqual(preserved['timeout'], 9)
            self.assertTrue((codex / 'skills/fellowship/scripts/fellowship.py').exists())

    def test_hook_command_uses_running_interpreter_not_path_python3(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            codex = root / 'codex'
            codex.mkdir()
            bindir = root / 'bin'
            bindir.mkdir()
            fake_python = bindir / 'python3'
            fake_python.write_text('#!/bin/sh\nexit 99\n')
            fake_python.chmod(0o755)
            env = {**os.environ, 'PATH': str(bindir) + os.pathsep + os.environ.get('PATH', '')}
            result = subprocess.run([sys.executable, str(SOURCE / 'install.py'), 'install', '--app', 'codex', '--codex-home', str(codex)], capture_output=True, text=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            command = json.loads((codex / 'hooks.json').read_text())['hooks']['Stop'][-1]['hooks'][0]['command']
            expected = shlex.join([sys.executable, str((codex / 'skills/fellowship/scripts/fellowship.py').resolve()), 'hook', '--provider', 'codex'])
            self.assertEqual(command, expected)

    def test_entrypoint_rejects_python_before_311(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('fellowship_install_version_test', SOURCE / 'install.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        stderr = io.StringIO()
        with patch.object(module.sys, 'version_info', (3, 9, 6)), patch.object(module.sys, 'argv', ['install.py', 'install']), patch.object(module.sys, 'stderr', stderr):
            self.assertEqual(module.main(), 2)
        self.assertIn('Python 3.11 or newer', stderr.getvalue())

    def test_prefixed_helper_command_cannot_be_updated_or_uninstalled(self):
        with tempfile.TemporaryDirectory() as temp:
            codex = Path(temp) / 'codex'
            codex.mkdir()
            install = [sys.executable, str(SOURCE / 'install.py'), 'install', '--app', 'codex', '--codex-home', str(codex)]
            result = subprocess.run(install, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            settings = codex / 'hooks.json'
            config = json.loads(settings.read_text())
            hook = config['hooks']['PreToolUse'][-1]['hooks'][0]
            hook['command'] = 'env FELLOWSHIP_TRACE=1 ' + hook['command']
            settings.write_text(json.dumps(config))
            edited = settings.read_bytes()
            for action in ('install', 'uninstall'):
                command = [sys.executable, str(SOURCE / 'install.py'), action, '--app', 'codex', '--codex-home', str(codex)]
                result = subprocess.run(command, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Fellowship hook was customized', result.stderr)
                self.assertEqual(settings.read_bytes(), edited)
                self.assertTrue((codex / 'skills/fellowship/install-receipt.json').exists())
                self.assertTrue((codex / 'skills/fellowship/scripts/fellowship.py').exists())

    def test_quoted_helper_command_with_timeout_edit_is_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            codex = Path(temp) / "O'Brien" / 'codex'
            codex.mkdir(parents=True)
            install = [sys.executable, str(SOURCE / 'install.py'), 'install', '--app', 'codex', '--codex-home', str(codex)]
            result = subprocess.run(install, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            settings = codex / 'hooks.json'
            config = json.loads(settings.read_text())
            hook = config['hooks']['PreToolUse'][-1]['hooks'][0]
            hook['command'] = 'env FELLOWSHIP_TRACE=1 ' + hook['command']
            hook['timeout'] = 9
            settings.write_text(json.dumps(config))
            edited = settings.read_bytes()
            receipt = codex / 'skills/fellowship/install-receipt.json'
            receipt_before = receipt.read_bytes()
            helper = codex / 'skills/fellowship/scripts/fellowship.py'
            helper_before = helper.read_bytes()
            for action in ('install', 'uninstall'):
                command = [sys.executable, str(SOURCE / 'install.py'), action, '--app', 'codex', '--codex-home', str(codex)]
                result = subprocess.run(command, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Fellowship hook was customized', result.stderr)
                self.assertEqual(settings.read_bytes(), edited)
                self.assertEqual(receipt.read_bytes(), receipt_before)
                self.assertEqual(helper.read_bytes(), helper_before)

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
            self.assertEqual(len(list((repo / '.codex/agents').glob('*.toml'))), 5)
            self.assertNotIn(str(SOURCE), (repo / '.codex/agents/frodo.toml').read_text())
            self.assertFalse((repo / '.git/fellowship').exists())
            role_ignored = subprocess.run(['git', '-C', str(repo), 'check-ignore', '-q', '.claude/agents/gandalf.md'])
            self.assertNotEqual(role_ignored.returncode, 0)
            private_ignored = subprocess.run(['git', '-C', str(repo), 'check-ignore', '-q', '.claude/worktrees/private/file'])
            self.assertEqual(private_ignored.returncode, 0)
            agents = repo / 'AGENTS.md'
            agents.write_text(agents.read_text().replace('Fellowship is installed for this project', 'User-edited Fellowship block'))
            edited = agents.read_bytes()
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('independently modified', result.stderr)
            self.assertEqual(agents.read_bytes(), edited)


if __name__ == '__main__':
    unittest.main()
