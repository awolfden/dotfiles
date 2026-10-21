#!/usr/bin/env python3
"""Offline publication guard. Never prints matching values or reads credential stores."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_RULES_PATH = Path.home() / '.config/dotfiles-publication/denylist.json'
RULES = {
    'private-key': r'-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----',
    'provider-token': r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|xox[baprs]-[A-Za-z0-9-]{16,}|sk-(?:proj-|ant-)?[A-Za-z0-9_-]{20,}|AKIA[A-Z0-9]{16}|AIza[A-Za-z0-9_-]{30,})\b',
    'jwt': r'\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b',
    'credential-url': r'[a-z][a-z0-9+.-]*://[^\s/:@]+:[^\s/@]+@',
    'machine-home': r'/Users/[A-Za-z][A-Za-z0-9_-]+',
    'secret-assignment': r'''(?i)(?:client_secret|access_token|refresh_token|api_key|password)\s*["']?\s*[:=]\s*["']([A-Za-z0-9_+/=.-]{16,})["']''',
}
EMAIL = re.compile(r'\b[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b')


def load_private_rules():
    """Trusted local regexes; never load organization vocabulary from the repo."""
    path = PRIVATE_RULES_PATH
    if path.is_symlink() or path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Private denylist must be a regular file outside the repository')
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_size > 65536:
        raise ValueError('Invalid private denylist file')
    if os.name == 'posix' and (info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077):
        raise ValueError('Private denylist must be owner-only')
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or set(data) != {'version', 'patterns'} or data['version'] != 1:
        raise ValueError('Invalid private denylist schema')
    patterns = data['patterns']
    if not isinstance(patterns, list) or len(patterns) > 256:
        raise ValueError('Invalid private pattern list')
    rules = {}
    for i, pattern in enumerate(patterns, 1):
        if not isinstance(pattern, str) or not pattern or len(pattern) > 4096:
            raise ValueError('Invalid private pattern')
        try:
            rules[f'private-rule-{i}'] = re.compile(pattern)
        except re.error:
            raise ValueError('Invalid private pattern syntax') from None
    return rules


def scan_text(label, text, private_rules=None):
    problems = []
    rules = {**RULES, **(private_rules or {})}
    for number, line in enumerate(text.splitlines(), 1):
        for rule, pattern in rules.items():
            if re.search(pattern, line):
                problems.append(f'{label}:{number}: {rule}')
        for match in EMAIL.finditer(line):
            domain = match.group(1).lower()
            if domain not in {'example.com', 'example.org', 'example.test'} and not domain.endswith('.users.noreply.github.com') and domain != 'users.noreply.github.com':
                problems.append(f'{label}:{number}: personal-or-work-email')
    return problems


def git(*args):
    return subprocess.run(['git', '--no-pager', '-C', str(ROOT), *args],
                          capture_output=True, timeout=60, check=True).stdout


def scan_bytes(label, data, private_rules=None):
    try:
        return scan_text(label, data.decode('utf8'), private_rules)
    except UnicodeDecodeError:
        return [f'{label}: binary content requires separate review']


def allowed_paths():
    return {line[2:] for line in (ROOT / '.gitignore').read_text().splitlines()
            if line.startswith('!/') and not line.endswith('/')}


def scan_worktree(allowed, rules):
    problems = []
    # Include ignored extras; never follow symlinks into private data.
    for path in ROOT.rglob('*'):
        relative = path.relative_to(ROOT).as_posix()
        if relative == '.git' or relative.startswith('.git/'):
            continue
        if path.is_symlink():
            problems.append(f'{relative}: symlinks are not publishable')
        elif path.is_file():
            if relative not in allowed:
                problems.append(f'{relative}: file outside publication allowlist')
            else:
                problems.extend(scan_bytes(relative, path.read_bytes(), rules))
    for relative in allowed:
        if not (ROOT / relative).is_file() or (ROOT / relative).is_symlink():
            problems.append(f'{relative}: missing/nonregular approved file')
    for raw in git('ls-files', '-z').split(b'\0'):
        if raw and raw.decode() not in allowed:
            problems.append(f'{raw.decode()}: tracked path outside allowlist')
    return problems


def scan_history(allowed, rules):
    problems = []
    if git('status', '--porcelain').strip():
        problems.append('Release requires a clean, committed working tree')
    revisions = git('rev-list', '--all').decode().splitlines()
    if not revisions:
        problems.append('Release requires committed public history')
    seen = set()
    for revision in revisions:
        metadata = git('show', '-s', '--format=%an%n%ae%n%cn%n%ce%n%B', revision)
        problems.extend(scan_bytes('commit/' + revision[:12], metadata, rules))
        for row in git('ls-tree', '-rz', revision).split(b'\0'):
            if not row:
                continue
            meta, raw_path = row.split(b'\t', 1)
            mode, kind, oid = meta.decode().split()
            name = raw_path.decode()
            if name not in allowed or mode not in {'100644', '100755'} or kind != 'blob':
                problems.append(f'history/{revision[:12]}/{name}: unapproved path or mode')
            if kind == 'blob' and (oid, name) not in seen:
                seen.add((oid, name))
                problems.extend(scan_bytes(f'history/{oid[:12]}/{name}', git('cat-file', 'blob', oid), rules))
    problems.extend(scan_bytes('ref-metadata', git('for-each-ref', '--format=%(contents)%0a%(taggeremail)'), rules))
    return problems


def check(release=False, warnings=None):
    problems = []
    rules = {}
    try:
        rules = load_private_rules()
    except FileNotFoundError:
        if release:
            problems.append('Private denylist missing; release requires explicit local policy')
        elif warnings is not None:
            warnings.append('Private denylist missing; checking generic rules only')
    except (OSError, ValueError):
        problems.append('Private denylist unreadable, unsafe or invalid; check refused')
    allowed = allowed_paths()
    if not allowed:
        return problems + ['Empty publication allowlist']
    problems.extend(scan_worktree(allowed, rules))
    if release:
        problems.extend(scan_history(allowed, rules))
        scanner = shutil.which('gitleaks')
        if not scanner:
            problems.append('Dedicated scanner missing: install reviewed Gitleaks v8+; release refused')
        elif not problems:
            env = {k: v for k, v in os.environ.items()
                   if k not in {'GITLEAKS_CONFIG', 'GITLEAKS_CONFIG_TOML'}}
            result = subprocess.run([scanner, 'git', '--redact=100', '--no-banner',
                                     '--ignore-gitleaks-allow', '--log-level', 'error',
                                     '--log-opts=--all', str(ROOT)], cwd=ROOT, env=env,
                                    capture_output=True, timeout=180)
            if result.returncode:
                problems.append('Gitleaks failed or found a secret; release refused (raw output suppressed)')
    return sorted(set(problems))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', action='store_true', help='Require private policy, clean full history and Gitleaks')
    args = parser.parse_args()
    warnings = []
    try:
        problems = check(args.release, warnings)
    except (OSError, ValueError, subprocess.SubprocessError):
        problems = ['Publication check could not complete; fail closed']
    for warning in warnings:
        print('WARN:', warning)
    for problem in problems:
        print('FAIL:', problem)
    if not problems:
        print('PASS:', 'publication checks including private policy and Gitleaks' if args.release else 'local content policy only; NOT publication approval')
    return bool(problems)


if __name__ == '__main__':
    sys.exit(main())
