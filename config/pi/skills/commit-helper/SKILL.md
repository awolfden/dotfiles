---
name: commit-helper
description: Draft a conventional commit message from a verified staged diff and the repository's conventions. Draft-only; never stages, commits, amends, runs hooks or pushes. Use for commit-message preparation, not automatic Git operations.
---

# Commit Helper — draft-only pi bridge

Source checkout: `~/Documents/claude-plugins`; expected origin `https://github.com/awolfden/claude-plugins.git`, branch `main`.
Reviewed revision: `8aff11305a4b3da025eda644c2b7af554fd83aa2`

Require that origin/branch/HEAD and regular non-symlink dependency paths, including components below `~/Documents`; verify the hash then read the complete command. Stop prominently on missing, changed or inaccessible source. Never update it, refresh hashes or substitute a cache. Preserve unrelated checkout files; this gate does not claim remote freshness.

| Dependency | SHA-256 |
| --- | --- |
| plugins/commit-helper/commands/commit.md | `bc9dd170a75e9ad01365f7f93510a36ba96201c139873652413fdfcafeb1a9bd` |

Retain upstream's staged-change analysis, conventional types, project-style matching and message presentation. Override its final commit step: **this skill only drafts**. Approving wording does not authorize a Git mutation, hooks or publication.

1. Confirm the target repo and read applicable instructions. Inspect status and staged filenames before content; warn by path about likely secret/credential files and pause rather than printing them. Never read auth/env files for this task.
2. Read the selected staged diff using Git with external diff/text conversion disabled, plus recent subjects for style. Don't absorb unstaged/untracked changes into the message, stage files, or change the index. If nothing is staged, ask the user to select/stage changes; do not do it for them.
3. Ground claims in the diff. Do not infer that a test passed, bug was reproduced, security issue resolved or ticket closed without evidence. Confirm issue references and intentional breaking changes; don't invent closing footers or co-author attribution.
4. Use project subject rules first; absent those, aim for 50 characters with 72 as a ceiling, imperative lowercase subject after type/scope, no trailing period. Prefer truthful clarity to arbitrary abbreviation. Explain why in the body rather than listing every changed line.
5. Present a copyable proposed message and scope/verification caveats. If the staged diff changes, invalidate the old draft and reassess. A subsequent request to actually commit is a separate task requiring exact repo/index/message approval and hook-effect review, outside this skill.

No tests, fixes, staging, commits, amends, signing changes, hook execution/bypass, retries, pushes or PR posts. No automatic subagent dispatch. Source/update policy: `docs/skills.md` in the public dotfiles checkout.
