# Skill sources and local dependencies

This checkout contains eight locally maintained bridges, not copies of entire upstream plugin distributions. The bridges state their source roots, reviewed revisions and file digests where applicable. Read the source gate before using a skill. Missing or changed sources must fail visibly; do not update hashes blindly or install dependencies during invocation.

| Bridges | Existing source expected |
| --- | --- |
| Tighten Prose, Handoff, Link Reader | `~/.local/share/pi-skill-sources/nicknisi-claude-plugins`, public `nicknisi/claude-plugins` repository |
| Ideation | `~/.local/share/pi-skill-sources/nicknisi-ideation`, public `nicknisi/ideation` repository |
| Commit Helper, Doc Generator, Test Runner, Thermo-Nuclear Review | `~/Documents/claude-plugins`, public `awolfden/claude-plugins` repository |

For a deliberate update: verify the exact source directory, origin, branch and current status; review the selected files and all new references; preserve unrelated work; advance only the approved source; then update revision/hash checkpoints after review. No automatic learning, background source updates, marketplace installation or copying private source material into dotfiles.

The Thermo-Nuclear bridge incorporates a public MIT-licensed security methodology with its original notice and source permalinks. Other upstream methods remain external; possession of an upstream file does not authorize redistribution of unrelated assets.

Additional shared skills under `~/.agents/skills`, generated terminal integrations, downloaded pi packages and work-specific bridges remain separately managed. Their contents, workstation inventory and private restoration instructions are intentionally not included here. This public checkout alone does not reproduce every local capability.

Discovery does not prove behavior. Source gates remain the runtime responsibility of each bridge; the publication checker only checks this repository's content and history, not private source access or model quality.
