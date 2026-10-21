#!/usr/bin/env python3
"""Offline prompt structure checks, not model trials or an installation test."""
import importlib.util
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / 'docs/prompts/personal-research-and-voice.md'
SPEC = importlib.util.spec_from_file_location('publication', ROOT / 'bootstrap/publication_check.py')
POLICY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(POLICY)


class PromptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = PROMPT.read_text()
        cls.blocks = re.findall(r'^```text\n(.*?)^```$', cls.document, re.M | re.S)
        cls.prompt = cls.blocks[0] if cls.blocks else ''

    def test_one_self_contained_copyable_prompt(self):
        self.assertEqual(len(self.blocks), 1)
        for section in range(1, 8):
            self.assertRegex(self.prompt, rf'(?m)^{section}\. ')
        self.assertIn('If none are present, proceed with the unpersonalized starter profile.', self.prompt)

    def test_publication_policy_and_no_machine_paths(self):
        self.assertEqual(POLICY.scan_text('setup-prompt', self.document), [])
        self.assertNotRegex(self.document, r'(?:/home/[^\s/]+/|[A-Za-z]:\\Users\\)')

    def test_research_and_writing_are_separate(self):
        for required in [
            'Neither the parent nor a delegated writer may start research',
            'Further research requires a separate explicit request from me',
            'A meaning-preservation check compares the draft only with its supplied input.',
            'Do not require a JSON ledger, receipt or particular schema',
            'Keep the two skill descriptions scoped to their own tasks',
        ]:
            self.assertIn(required, self.prompt)

    def test_safe_setup_and_personalization(self):
        for required in [
            'stop before overwriting an existing file or registering a duplicate name',
            'Never mine chat, mail, account data, sessions or cached conversations.',
            'Do not retain raw samples in new files unless I ask.',
            'Do not stage, commit, push, deploy',
            'Before any additional live model evaluation',
            'ask for approval',
        ]:
            self.assertIn(required, self.prompt)

    def test_synthetic_acceptance_case_coverage(self):
        cases = dict(re.findall(r'^([A-L])\. (.+)$', self.prompt, re.M))
        self.assertEqual(set(cases), set('ABCDEFGHIJKL'))
        expected = {
            'A': 'no skill requested', 'B': 'without research',
            'C': 'without refreshing', 'D': 'do not open the link',
            'E': 'cause unknown', 'F': 'no renewed research',
            'G': 'no subagent support', 'H': 'irrelevant integration',
            'I': 'quoted requests are not authorization', 'J': 'output text only',
            'K': 'not authority', 'L': 'preserve the existing file',
        }
        for key, phrase in expected.items():
            with self.subTest(case=key):
                self.assertIn(phrase, cases[key])
                self.assertEqual(POLICY.scan_text('synthetic-case-' + key, cases[key]), [])

    def test_validation_limits_are_explicit(self):
        self.assertIn('Static checks are not model-behavior tests.', self.prompt)
        self.assertIn('Never claim a model scenario passed merely because', self.prompt)
        self.assertIn('not run this setup prompt through a model', self.document)
        self.assertIn('follow the harness\'s recovery/stop rules', self.prompt)


if __name__ == '__main__':
    unittest.main()
