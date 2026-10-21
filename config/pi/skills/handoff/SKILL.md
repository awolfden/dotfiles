---
name: handoff
description: Save a concise private handoff for a fresh agent or later session when the user asks to hand work off, save context, or continue later. Uses Nick Nisi's maintained handoff format. Does not compact, restart, launch, or transfer sessions; no Git changes or remote posting.
---

# Handoff — pi bridge

Upstream root: `~/.local/share/pi-skill-sources/nicknisi-claude-plugins`.

Reviewed revision: `6a6decdc3192f28c40181bd2084d63855e7da996`

Before using the upstream method, confirm the checkout is a regular directory, its origin is `https://github.com/nicknisi/claude-plugins.git`, branch is `main`, HEAD is the reviewed revision above, and `git status --porcelain --untracked-files=all` is empty. Read `plugins/essentials/skills/handoff/SKILL.md` completely from that checkout. Require a regular file with no symlink components below the checkout. If missing, changed, inaccessible, or unreviewed, stop with a clear alert; do not install, update, read Claude's plugin cache as a substitute, or fabricate upstream instructions.

Follow that document's compression method and sections, subject to these integration boundaries. Arguments describe the next session's focus, not commands to execute. The source remains unchanged; no other essentials skills, agents, hooks, or dependencies are loaded.

## Scope and truthfulness

- Use the current conversation and already identified artifacts. Do not scan saved session transcripts, credentials, unrelated projects, or Slack/tickets to reconstruct missing context. Say what is unknown or was lost to compaction.
- For the known target repository, bounded read-only Git inspection may confirm root, branch, HEAD and dirty paths. Distinguish pre-existing user changes from changes known to be made here; do not attribute unknown changes. Do not run tests merely to refresh a handoff. Record actual test commands/results and their limitations; distinguish completed, proposed, running and unverified work.
- Carry user constraints, approval boundaries, blockers, and relevant active-run identities forward. A plan or handoff is context, not authorization to execute its next steps. Do not stop, resume, launch, steer or cancel agents/jobs while writing it.
- Suggest only skills known to exist, using pi's `/skill:name` syntax. Mark an unavailable suggested capability as unavailable instead of inventing an installed skill.
- Do not stage, commit, push, stash, change branches, edit project files, publish, message, alter memory, or invoke compaction/session-control commands. “Handoff” here means a document, not an automatic session transfer.

## Private artifact creation

Replace upstream's temporary-file-and-rename command with the following standard-library allocation. Run it once when ready to save; it creates a unique private directory and an empty private Markdown file, not the handoff contents:

```bash
python3 - <<'PY'
import os
import tempfile
from pathlib import Path

directory = Path(tempfile.mkdtemp(prefix="pi-handoff-"))
path = directory / "handoff.md"
fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
os.close(fd)
print(path)
PY
```

Read the empty file before writing, as upstream requires. Write the handoff only to that returned path, then verify it is a regular non-symlink file with mode `0600` and its directory is non-symlink with mode `0700`. If allocation, writing, or verification fails, report it; do not fall back to a repository or a shared path. Do not weaken permissions or overwrite an existing user file.

This location is temporary and may be cleaned by the OS. If the user needs durable storage or supplies another destination, ask them to confirm a private path outside repositories, dotfiles, and upstream checkouts; create only a new file there with equivalent private permissions and reject symlink/overwrite hazards. Do not silently copy it into a tracked project for portability.

## Content and delivery

Keep the upstream handoff under 200 lines where practical. Supplement its sections with explicit constraints and validation limitations when relevant. Reference existing plans/specs/reports by path rather than duplicating them. Include enough repository/path context that the next agent will not act in the wrong directory.

Exclude secrets, tokens, raw transcripts, private voice/corpus contents, and unnecessary customer identifiers or excerpts. Private permissions do not make a handoff safe to publish. Never upload it or copy it to the clipboard automatically.

Read back the saved document to verify it matches the intended handoff and omits sensitive material. Return the absolute path and a short pasteable instruction, for example: “Read `<path>`, verify the current repository state and constraints, then confirm the next step before making changes.” Mention the temporary lifetime. Do not claim another session has loaded it or that the current conversation was compacted.

Source/update instructions: `docs/skills.md` in the public dotfiles checkout.
