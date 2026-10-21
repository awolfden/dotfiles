# Dotfiles

Public workstation configuration with private machine/work settings kept separately. This is a selected personal setup, not a universal installer. Never copy an entire agent home directory into this checkout.

## Public vs local

| Public, versioned here | Local, outside this repository |
| --- | --- |
| Shell, terminal and window-manager preferences | `~/.zshrc.local`, `~/.zshenv.local` |
| Generic Git behavior | `~/.gitconfig-local` for identity and conditional includes |
| Selected pi settings, agents, skills and extension source | Work-specific skills/agents in pi's local discovery directories |
| Public MCP service definitions | `~/.pi/agent/mcp.json` for private MCP definitions |
| Synthetic tests and publication checks | OAuth/Keychain credentials, sessions, caches and private artifacts |

The public MCP file is linked at `~/.config/mcp/mcp.json`. The adapter's native higher-priority `~/.pi/agent/mcp.json` supplies local servers; no custom JSON merger is required. Keep server names stable when moving definitions so existing OAuth bindings continue to work. Public URLs do not grant access; authorize services separately.

## Adoption

Review every file before use. Back up existing destinations and create individual links to the chosen files; do not replace `~/.pi` wholesale. This repository intentionally has no automatic installer.

- `config/shell/{zshrc,zshenv,zsh_aliases}` → the matching dot-prefixed home files.
- `config/git/config` → `~/.gitconfig`; set identity in `~/.gitconfig-local` separately. `user.useConfigOnly` prevents Git from guessing it.
- `config/mcp/mcp.json` → `~/.config/mcp/mcp.json`.
- `config/pi/settings.json` → `~/.pi/agent/settings.json`.
- Individually link selected `config/pi/agents/*.md` and skill files into pi's matching discovery directories.
- `config/pi/extensions/notify.ts` → `~/.pi/agent/extensions/notify.ts`.
- `config/pi/extensions/gmail-readonly/` → `~/.pi/agent/extensions/gmail-readonly/`.
- `config/pi/subagents/config.json` → `~/.pi/agent/extensions/subagent/config.json`.
- Optional terminal/window-manager settings have their own `config/` directories; review shortcuts and startup behavior before linking.

Pi packages run code with user permissions. Settings select an unpinned MCP adapter, pinned subagents package and a Git skill package. Source selection is not a full dependency lock. Provider/model availability varies; do not install, upgrade or authenticate merely to validate this checkout. `lastChangelogVersion` is harmless generated UI state, not a version pin or secret.

Private local files are trusted executable configuration where applicable. Keep permissions restrictive and credentials in supported credential stores rather than shell literals. Gmail's extension source is public, but Google Desktop client files and tokens must remain outside this repository; setup uses `/gmail-setup` and macOS Keychain. It does not grant send/modify tools.

## Shareable setup prompts

[Personal research and voice workflow](docs/prompts/personal-research-and-voice.md)
is a copy-paste setup request for creating separate investigation and writing
skills in an existing agent harness. The writing skill uses available context
without starting research or re-verifying facts. Personalization stays private;
no writing samples means a clearly marked starter profile. This is a recipe,
not an installer, and has not been validated through a live one-shot model trial.

## Checks

```sh
python3 -B bootstrap/publication_check.py
python3 -B bootstrap/test_publication.py
python3 -B bootstrap/test_research_voice_prompt.py
node --test bootstrap/test-notify.mjs bootstrap/test-gmail-readonly.mjs
```

The first command checks the exact file allowlist, generic secret patterns and an optional private denylist. It does not read account settings or credentials. A missing private denylist warns in local mode; a malformed, unsafe or unreadable one fails. This check is **not** publication approval.

### Private publication policy

Organization names, internal hostnames and private workflow names must not be
embedded in this public checker or its fixtures. Store your own regex patterns
in `~/.config/dotfiles-publication/denylist.json`, outside this checkout. Use a
regular file, at most 64 KiB, owned by you and mode `0600` on POSIX (directory
`0700` recommended). Symlinks and paths resolving inside the repo are rejected.
The trusted local policy accepts up to 256 nonempty regexes of at most 4096
characters each. Invalid regexes fail without printing their contents.

Example shape, using **synthetic names only**:

```json
{"version": 1, "patterns": ["gateway\\.internal\\.example\\.test", "example-internal-marketplace"]}
```

JSON requires each regex backslash to be escaped, as shown in the example above,
to match literal dots. Replace the synthetic entries with your private terms,
not in this repository. If you deliberately have no additional terms, use
`{"version": 1, "patterns": []}` as an explicit choice. A missing policy always
blocks `--release`. Matches report only numbered rule IDs, never the pattern or
matched value. This is a trusted local configuration, not downloaded policy.

Before any public push, install a separately reviewed Gitleaks v8+ executable and run:

```sh
python3 -B bootstrap/publication_check.py --release
```

Release checks require the private policy and a clean committed tree, inspect all reachable commit trees and metadata with both rule sets, and run Gitleaks with redacted output. Scanner-config environment overrides and inline allow-comments are not honored by the release command. Missing scanner, findings or execution errors refuse release. No command downloads tools or uploads scan contents. Heuristics and scanners can miss secrets; manually review the exact content, third-party rights and intended audience as well.

An optional `.githooks/pre-push` runs the release check and restricts publication to `main`. Enable deliberately with `git config --local core.hooksPath .githooks`. Hooks are bypassable and do not protect GitHub uploads from other clients. Enable GitHub secret scanning/push protection when creating the repository; do not rely on CI to catch a secret after publication.

## History and identity

Publish only a fresh, reviewed history. Removing a private file in a later commit does not remove earlier versions. Do not add a remote or push an older mixed/private repository as this project's history. Use a GitHub no-reply author/committer email for public commits if you do not want to publish your mailbox address. The release check also inspects author/committer and tag metadata.

Existing license notices in copied components must remain intact. No blanket license is granted here for third-party or private sources. See [skill source notes](docs/skills.md) and [extension provenance and notices](docs/extensions.md).
