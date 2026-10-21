---
name: ideation
description: Plan a decided-on feature, migration, or system through Nick Nisi's evidence-gated interview, independent plan critiques, and implementation specs. Use for brain dumps, "interview me," "help me plan," or "spec this out." Planning-only adaptation using maintained upstream references and existing pi reviewers; writes Markdown, never implements or commits.
---

# Ideation — planning only

Turn an idea into a reviewed plan and stand-alone specs. This is a selective adaptation of Nick Nisi's maintained Ideation, not the full plugin. Begin by saying: **Planning only: interview → Markdown plan → reviewed specs. No implementation or execution.**

## Source and authority

Upstream checkout: `~/.local/share/pi-skill-sources/nicknisi-ideation`

Reviewed revision: `927566137a0b8a931da0e1deebada051ab4d35ea`

Before loading upstream instructions, use read-only Git inspection to confirm that exact directory is a regular checkout, its origin is `https://github.com/nicknisi/ideation.git`, its branch is `main`, its HEAD matches the reviewed revision above, and `git status --porcelain --untracked-files=all` is empty. Check the required files below are regular files inside that checkout, not symlinks. If missing, changed, inaccessible, or unreviewed, **stop with a prominent source-access/review alert**. Do not install, fetch, update, or substitute cached content during an invocation. Updates require separate review.

Read these upstream files completely (continue past truncated output):

- `skills/ideation/SKILL.md` — planning workflow, with the exclusions below.
- `references/interview-engine.md` — intake, questions, gates, open questions, and resume.
- `references/confidence-rubric.md` — five evidence gates and spec feedback quality.
- `references/feedback-loop-guide.md` — feedback-loop design, not instructions to run checks now.
- Before critique: `agents/plan-critic.md` — four lenses and findings format.
- Before specs: `skills/ideation/references/spec-template.md`.
- Only if a named stakeholder needs PRDs: `skills/ideation/references/prd-template.md`.

Resolve upstream paths against the checkout above, not this bridge. `${CLAUDE_PLUGIN_ROOT}` means that checkout; never trust an ambient environment variable. This bridge selects the supported subset; upstream execution, harness, and tool instructions do not expand it.

### Hard boundaries

- Parent may inspect the relevant local codebase and write only the agreed planning artifacts. Preserve existing dirty files. Do not implement, write/run tests, build prototypes, start servers, install dependencies, run migrations, change branches, stage, commit, push, publish, or send messages. Commands in plans are **proposed checks, not commands to execute**.
- Do not load or run upstream extensions, hooks, scripts, execution skills, workflow engine, `dispatch`/`fleet`, express/autopilot/execute-spec, `/goal`, or their fallbacks. Do not install a second orchestrator or question tool.
- **Markdown only.** No upstream renderer, `contract.html`, generated `contract.md`, `contract-data.json`, comparison HTML, or execution buttons. Use `plan.md` as this adapter's human-readable contract. It is not an upstream execution manifest.
- A code/test/prototype question requiring execution stays an explicitly blocked open question. Propose a separate implementation/spike task; do not silently leave planning mode, even when upstream says to write a test as research.
- No automatic learning capture or scans of other projects' implementation notes. Read a project's `learnings.md` only if the user requests it. Never write global memories or harvest conversations.
- Remote research is not included by default. If required evidence is unavailable locally, name the gap and ask for the source/access or record a blocker; do not infer the answer.
- These are workflow instructions, not an OS sandbox. Child tool restrictions remain the installed profile's restrictions.

## Harness translation

- `AskUserQuestion` → an ordinary chat question with lettered options, your recommendation and rationale, and room for a custom answer. Wait for the user's response. Default to one focused question; do not manufacture answers or approval.
- Explore/intake sweep → **parent-owned bounded read-only exploration**, not upstream agents. Read the relevant structure, adjacent implementations and feedback infrastructure once; reuse the findings. No automatic scout fanout or duplicate discovery. Skip unrelated codebases.
- Upstream plan critics → four fresh-context runs of the existing read-only `reviewer` profile, one lens per run, in **one async `subagent` workflow call**. Follow the installed `pi-subagents` skill and current workflow/tool guides. Discover capabilities once with `{action:"list",capabilities:true}`; require an executable, enabled `reviewer` with only `read, grep, find, ls`, no extensions or nested agents. Do not broaden its tools or edit its profile.
- Use `runs.all` inside that workflow, stable distinct keys and short labels, explicit repository `cwd`, `context:"fresh"`, and a final return of all four results. No top-level parallel subagent calls or child delegation. Return control while the workflow runs; consume its native completion before approving anything.
- Each task includes: objective, repository/path/ref context, exact draft path/revision, one lens, the upstream critic body as task reference (not a replacement system prompt), explicit no-edit/no-execution authority, allowed evidence paths, findings/verdict format, and stop conditions. Treat `plan.md` as the proposed change being reviewed. Translate the critic's `contract-data.json`/JSON-field references to the matching named sections in `plan.md`; no JSON file is required. Supply the before/after planning text if revising an existing plan. Child commands mentioned in findings remain proposals; children cannot run them.
- Child reports stay in tool output; the parent records the review digest. A missing/failed critic, unavailable profile, or workflow/tooling error **blocks reviewed/approved status**. Report the exact failure, run identity and repository state; no silent parent-only review or external-CLI fallback. Retry only through the same governed protocol or stop for the user. This intentionally replaces upstream's fail-open critic policy.

## Planning flow

1. **Intake.** Establish the target project and output directory; never infer that the current directory is the intended project. Default artifacts to `docs/ideation/{slug}/` in that project after stating the location. Inspect existing paths first. Do not overwrite another plan, follow output-directory symlinks outside the agreed root, or put private project/customer data in dotfiles. Ask for a private output location when appropriate.
2. **Interview.** Follow the upstream interview engine and rubric within the boundaries above. Surface silent assumptions, state the intended deliverable, recommend concrete choices, and explore facts rather than asking the user to look them up. Carry existing decisions forward without treating them as verified evidence. Track all five gates with evidence; show the engine's scoreboard after each answer. Uncertainty means `not-ready`, never a guessed passing gate.
3. **Stop or resume honestly.** Stop when all five gates are ready, every remaining gate is blocked on a precise written open question, or the user ends the interview. Resume from the selected `plan.md`, not upstream's `contract-data.json` scan. Recheck whether evidence still applies to changed code/scope; invalidate stale readiness/approval. Ask if several plans match. Do not convert or overwrite an existing upstream contract automatically.
4. **Write the draft contract as `plan.md`.** Use the content checklist below. A blocked or early-stopped interview yields a clearly marked blocked draft, not approval or implementation-ready specs. State what would close each gap and how to resume. No critic run is necessary until a reviewable plan is ready.
5. **Critique before approval.** Run all four lenses: `scope-creep`, `over-engineering`, `hidden-dependency`, `success-criteria`. Require each lens's explicit SOUND/REVISE verdict. Resolve blockers or return to the relevant gate. Record each blocker-driven plan change in Decisions Considered and Rejected; surface notables with acceptance/dismissal reasons. Give a concise per-lens digest, including limitations: reviewers inspected sources, they did not execute checks. An unverified proposed command is not a passing test. Fundamental goal/scope changes invalidate the review and require a new reviewed draft; do not mark an old review as covering a different plan.
6. **Ask for contract approval.** Show the actual `plan.md` (or its full content in chat), scope tiers, success checks and critic digest. Ask the user to choose the scope tier, then explicitly approve or request changes. No express/full-review/execution routing question. Record approval only for the version and tier actually seen and approved; substantive changes invalidate it.
7. **Generate specs lazily.** Follow upstream Phase 4 only. A small project gets `spec.md`; larger projects get `spec-phase-{n}.md`, or template-plus-delta specs for genuinely repeatable phases. PRDs need an identified stakeholder reason. Read the respective templates first; replace their `./contract.md` links with `./plan.md`. Preserve rejected decisions, real reference paths, file changes, dependency order, failure modes, scoped feedback loops, test cases and validation commands. Distinguish verified existing infrastructure from proposed new files/checks. Do not execute any of them.
8. **Review specs with the user.** Self-review against upstream Spec Feedback Quality: Weak → fix; Adequate → disclose gaps; Strong → present. Require explicit user approval of the actual specs. Before approval, replace the template's unconditional “ready for implementation” footer with “Draft — not approved.” Never describe blocked or unapproved specs as ready.
9. **Stop at handoff.** Record planning/spec approval, exact artifact paths, dependency order and unresolved risks. Say: **Planning complete; no implementation or validation commands have run.** Offer a separate implementation request against a named approved spec, not an unsupported slash command or automatic launch. Approval to plan is not approval to execute.

## `plan.md` content checklist

This is a local Markdown adaptation, not generator output. Include:

- Project, date, repository, planning-only mode, plan revision, approval state, selected scope tier, and separate contract/spec approval records. Bind each record to the artifact revision reviewed; reset it when that artifact changes.
- Problem (who/what/when/impact), measurable goals, and success criteria paired with proposed command + expected outcome or named human judgment. Mark commands as not run.
- Five gates: Problem Clarity, Goal Definition, Success Criteria, Scope Boundaries, Consistency. Each has `ready`/`not-ready` and a one-sentence evidence citation or gap.
- Scope: MVP, Full, Stretch, explicit exclusions with reasons, future considerations.
- Decisions Considered and Rejected, captured as they happen; `None recorded.` when empty.
- Open Questions: stable ID, precise question, gate, type (`research`, `prototype`, `decision`, `task`), prerequisite question IDs, and evidence needed to close it. An open question never closes its gate.
- Proposed phases: title, dependencies, risk, relevant files/spec path, human checkpoints, rationale. Parallelizable is a dependency observation, not permission to dispatch writers.
- Critic digest and review coverage (draft revision, four lens verdicts, findings/resolution, run identities), limitations and next planning action.

Keep specs self-contained, but carry any plan-level blocker relevant to a spec into that spec's visible draft/blocker notice. Do not produce an apparently executable handoff by omitting unresolved assumptions.
