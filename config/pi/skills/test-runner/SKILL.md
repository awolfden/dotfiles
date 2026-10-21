---
name: test-runner
description: Select and run relevant existing project tests for an explicit change scope, then analyze failures without applying fixes. Inspect commands and effects before execution; no automatic installs, snapshot updates, remote mutations or commits.
---

# Test Runner — pi command bridge

Source checkout: `~/Documents/claude-plugins`; expected origin `https://github.com/awolfden/claude-plugins.git`, branch `main`.
Reviewed revision: `8aff11305a4b3da025eda644c2b7af554fd83aa2`

Require that origin/branch/HEAD, regular dependency and no symlink components below `~/Documents`; verify the hash before reading the complete command. Missing, changed or inaccessible source → stop visibly; no cache fallback, source update or digest refresh. Preserve unrelated checkout work. This is a reviewed local version, not a latest-upstream claim.

| Dependency | SHA-256 |
| --- | --- |
| plugins/test-runner/commands/test.md | `1070bbbc796548e5bfeea54ffe93018f8239c2fe44b8faf5ba0fbd15bf5e5777` |

Apply the source's framework detection, test mapping and failure analysis through parent-owned tools, with these boundaries:

- Establish target repository, local instructions and explicit baseline/files/pattern. Do not conflate staged, unstaged and recent-commit scopes. Preserve existing dirty work.
- Inspect actual package scripts, test configuration, setup/teardown and known effects. Prefer installed project tooling and documented commands; sample `npx` recipes are not installation authority. Missing dependencies → explain the blocker; no downloads or lockfile changes.
- Before execution, identify the exact command and permitted effects. A user's explicit test request can authorize ordinary local test artifacts, not network services, paid APIs, production/shared databases, deployment, destructive cleanup, credential reads or unexpected data writes. Ask before those effects; refuse dangerous validation shortcuts. Do not run untrusted code merely because a script is named test.
- Run a bounded, non-watch selection first with an appropriate timeout; record exit status and relevant redacted output. A timeout/interruption is not a test failure diagnosis or pass. Do not kill unrelated user processes.
- Explain failures against inspected evidence; separate likely cause from verified cause, existing failures from regressions, and skipped/blocked/unexecuted checks from passes. Never fabricate coverage or suite totals.
- Fixes, generated snapshots, fixture changes, dependency changes and broader suites need separately agreed scope. Suggest fixes, do not apply them automatically. No staging, commits, pushes, remote posts or automatic delegation.

Use the source's results/failures/next-steps format. Name exactly what ran, what did not, and any artifacts/effects. Passing selected tests does not certify the whole suite. Do not dump secrets or customer payloads into the report. Source/update policy: `docs/skills.md` in the public dotfiles checkout.
