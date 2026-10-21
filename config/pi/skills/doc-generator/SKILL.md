---
name: doc-generator
description: Draft accurate documentation for a specified file, module or API in the project's existing style. Apply only explicitly approved documentation edits. No implementation changes, generator execution, installs, publication or commits.
---

# Doc Generator — pi command bridge

Source checkout: `~/Documents/claude-plugins`; expected origin `https://github.com/awolfden/claude-plugins.git`, branch `main`.
Reviewed revision: `8aff11305a4b3da025eda644c2b7af554fd83aa2`

Require that origin/branch/HEAD, regular dependency and no symlink components below `~/Documents`; verify its SHA-256 then read the complete source command. Missing, changed or inaccessible source → prominent blocker. No automatic source update, digest refresh or cache substitution. Preserve unrelated checkout work; reviewed version does not imply current remote HEAD.

| Dependency | SHA-256 |
| --- | --- |
| plugins/doc-generator/commands/docs.md | `e1518646ae6ba6300e742e0ce6f134c01b913418c2ccd4b7615308019a4a68d4` |

Translate the source workflow to ordinary chat and parent-owned tools:

- Establish the target repo, audience, named files/module/API, and inline versus separate output. Ask before interpreting “document the project” as a broad rewrite. Read project guidance and Git status, preserve dirty/untracked work.
- Inspect real interfaces, behavior, errors and nearby documentation before drafting. Preserve local style and source conventions. Distinguish verified behavior from assumptions; missing evidence gets a question or explicit caveat, not an invented API example.
- Present the documentation draft and exact proposed file scope. Apply only after explicit approval; re-read the target before editing and stop on conflicting changes. Keep runtime implementation, signatures and exports unchanged. Docstrings/comments can be runtime-visible: don't claim every documentation edit is behavior-free.
- Do not overwrite whole source files merely to add docs, copy private references/customer data, add project instruction files, or document internal/private APIs outside scope. Public-facing examples must use safe synthetic data and accurately supported APIs.
- Source declares Bash, but authoring alone does not authorize scripts. Generators, doctests, builds, tests, installers and dependency changes require separately reviewed execution scope; inspect effects first. Label examples as unexecuted unless actually run.
- Return changed paths, rationale, checks actually performed and remaining verification. No automatic commits, pushes, publishing, posts, learning logs or subagents.

Source/update policy: `docs/skills.md` in the public dotfiles checkout.
