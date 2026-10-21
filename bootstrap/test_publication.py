#!/usr/bin/env python3
"""Synthetic policy tests. No credentials, network or changes to live settings."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('publication', Path(__file__).with_name('publication_check.py'))
P = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(P)


class PolicyTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        base = Path(temp.name)
        self.root = base / 'repo'
        self.root.mkdir()
        (self.root / '.gitignore').write_text('*\n!*/\n!/.gitignore\n!/config.json\n')
        (self.root / 'config.json').write_text('{}\n')
        self.policy = base / 'private.json'
        self.policy.write_text(json.dumps({'version': 1, 'patterns': [r'gateway\.internal\.example\.test', 'example-internal-marketplace']}))
        self.policy.chmod(0o600)
        for target, value in [('ROOT', self.root), ('PRIVATE_RULES_PATH', self.policy)]:
            p = patch.object(P, target, value)
            p.start()
            self.addCleanup(p.stop)

    def fake_git(self, *args):
        if args[0] == 'rev-list':
            return b'abcdef123456\n'
        if args[0] == 'ls-tree':
            return b'100644 blob aabbcc\tconfig.json\0'
        if args[0] == 'cat-file':
            return b'{}'
        return b''

    def test_generic_metadata_denied(self):
        for text in ['person@' + 'company.test', '/Users/' + 'someone/config']:
            self.assertTrue(P.scan_text('fixture', text))

    def test_secret_shapes_denied_and_redacted(self):
        for text in ['ghp_' + 'a' * 40, '-----BEGIN ' + 'PRIVATE KEY-----',
                     'client_secret: "' + 'a' * 32 + '"',
                     'https://username:' + 'password@example.com/']:
            findings = P.scan_text('fixture', text)
            self.assertTrue(findings)
            self.assertNotIn(text, '\n'.join(findings))

    def test_public_examples_allowed(self):
        self.assertEqual(P.scan_text('fixture', 'reader@example.test https://mcp.notion.com/mcp'), [])
        self.assertEqual(P.scan_text('fixture', '123+public@users.noreply.github.com'), [])

    def test_private_patterns_loaded_and_not_echoed(self):
        for text in ['https://gateway.internal.example.test/mcp', 'example-internal-marketplace']:
            findings = P.scan_text('fixture', text, P.load_private_rules())
            self.assertTrue(findings)
            self.assertIn('private-rule-', findings[0])
            self.assertNotIn(text, '\n'.join(findings))

    def test_binary_requires_review(self):
        self.assertTrue(P.scan_bytes('fixture', b'\xff\x00'))

    def test_unknown_file_and_symlink_denied(self):
        with patch.object(P, 'git', return_value=b''):
            self.assertEqual(P.check(), [])
            (self.root / 'extra.txt').write_text('unreviewed')
            self.assertTrue(P.check())
            (self.root / 'extra.txt').unlink()
            (self.root / 'config.json').unlink()
            (self.root / 'config.json').symlink_to(self.root / '.gitignore')
            self.assertTrue(P.check())

    def test_missing_private_policy_warns_locally_and_blocks_release(self):
        self.policy.unlink()
        warnings = []
        with patch.object(P, 'git', side_effect=self.fake_git), patch.object(P.shutil, 'which', return_value='/scanner'), patch.object(P.subprocess, 'run') as scanner:
            self.assertEqual(P.check(warnings=warnings), [])
            self.assertTrue(warnings)
            self.assertTrue(any('Private denylist missing' in p for p in P.check(release=True)))
            scanner.assert_not_called()

    def test_invalid_private_policy_refuses_without_echo(self):
        for value in ['not-json', '{}', '{"version":1,"patterns":["[sensitive-fixture"]}']:
            self.policy.write_text(value)
            with patch.object(P, 'git', side_effect=self.fake_git):
                findings = P.check()
            self.assertTrue(any('denylist unreadable' in p for p in findings))
            self.assertNotIn(value, '\n'.join(findings))

    def test_unreadable_private_policy_blocks(self):
        with patch.object(P, 'load_private_rules', side_effect=PermissionError), patch.object(P, 'git', side_effect=self.fake_git):
            self.assertTrue(any('denylist unreadable' in p for p in P.check()))

    def test_private_policy_inside_repo_or_symlink_rejected(self):
        with patch.object(P, 'PRIVATE_RULES_PATH', self.root / 'config.json'):
            with self.assertRaises(ValueError):
                P.load_private_rules()
        link = self.policy.with_name('link.json')
        link.symlink_to(self.policy)
        with patch.object(P, 'PRIVATE_RULES_PATH', link):
            with self.assertRaises(ValueError):
                P.load_private_rules()

    @unittest.skipUnless(os.name == 'posix', 'POSIX mode check')
    def test_publicly_readable_private_policy_rejected(self):
        self.policy.chmod(0o644)
        with self.assertRaises(ValueError):
            P.load_private_rules()

    def test_explicit_empty_policy_is_valid(self):
        self.policy.write_text('{"version":1,"patterns":[]}')
        self.assertEqual(P.load_private_rules(), {})

    def test_missing_scanner_and_history_block_release(self):
        with patch.object(P, 'git', return_value=b''), patch.object(P.shutil, 'which', return_value=None):
            problems = P.check(release=True)
        self.assertTrue(any('scanner missing' in p for p in problems))
        self.assertTrue(any('committed public history' in p for p in problems))

    def test_private_rules_cover_history_and_metadata(self):
        for command in ['cat-file', 'show', 'for-each-ref']:
            def git(*args):
                return b'https://gateway.internal.example.test/mcp' if args[0] == command else self.fake_git(*args)
            with patch.object(P, 'git', side_effect=git), patch.object(P.shutil, 'which', return_value='/scanner'), patch.object(P.subprocess, 'run') as scanner:
                findings = P.check(release=True)
                self.assertTrue(any('private-rule-' in p for p in findings), command)
                scanner.assert_not_called()

    def test_disallowed_history_modes_block(self):
        for mode, kind in [('120000', 'blob'), ('160000', 'commit')]:
            def git(*args):
                return f'{mode} {kind} aabbcc\tconfig.json\0'.encode() if args[0] == 'ls-tree' else self.fake_git(*args)
            with patch.object(P, 'git', side_effect=git), patch.object(P.shutil, 'which', return_value=None):
                self.assertTrue(any('unapproved path or mode' in p for p in P.check(release=True)))

    def test_gitleaks_failure_blocks_and_output_is_suppressed(self):
        for code in [1, 2]:
            result = subprocess.CompletedProcess([], code, b'sensitive-output', b'sensitive-output')
            with patch.object(P, 'git', side_effect=self.fake_git), patch.object(P.shutil, 'which', return_value='/scanner'), patch.object(P.subprocess, 'run', return_value=result):
                findings = P.check(release=True)
            self.assertTrue(any('Gitleaks failed' in p for p in findings))
            self.assertNotIn('sensitive-output', '\n'.join(findings))

    def test_clean_release_invokes_redacted_scanner_without_config_env(self):
        result = subprocess.CompletedProcess([], 0)
        with patch.object(P, 'git', side_effect=self.fake_git), patch.object(P.shutil, 'which', return_value='/scanner'), patch.dict(os.environ, {'GITLEAKS_CONFIG': '/unused'}), patch.object(P.subprocess, 'run', return_value=result) as scanner:
            self.assertEqual(P.check(release=True), [])
            args, kwargs = scanner.call_args
            self.assertIn('--redact=100', args[0])
            self.assertIn('--ignore-gitleaks-allow', args[0])
            self.assertNotIn('GITLEAKS_CONFIG', kwargs['env'])
            self.assertEqual(kwargs['cwd'], self.root)


if __name__ == '__main__':
    unittest.main()
