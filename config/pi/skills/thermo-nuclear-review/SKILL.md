---
name: thermo-nuclear-review
description: Perform a rigorous structural and security code review covering complexity, maintainability, type clarity, trust boundaries, auth, injection and state integrity. Use for Thermo-Nuclear Review or a code-quality/security audit of a specified diff, PR or file. Read-only findings; no fixes, tests, exploit execution, commits or posts.
---

# Thermo-Nuclear Review — pi bridge

## Reviewed source gate

Source checkout: `~/Documents/claude-plugins`; expected origin `https://github.com/awolfden/claude-plugins.git`, branch `main`.
Reviewed revision: `8aff11305a4b3da025eda644c2b7af554fd83aa2`

Require the expected origin/branch/HEAD and regular non-symlink dependency paths, including path components below `~/Documents`. Verify all hashes below before reading the complete command and rubric. Missing, changed or inaccessible source is a blocker: report it, never auto-update, use a cache or refresh digests. Unrelated untracked files outside the selected plugin are preserved, not a reason to clean the checkout. Reviewed bytes, not remote freshness, are guaranteed.

| Dependency | SHA-256 |
| --- | --- |
| plugins/code-quality/commands/thermo-nuclear-review.md | `31d02d034e72b7f1680c18a97649c96c8e787f701e24b43bacb65a183356d349` |
| plugins/code-quality/skills/thermo-nuclear-review/SKILL.md | `ab89ac95d7c8f5c910589fc2c2427afb2fa5474633c82f80765b278b397ae5c4` |

## Pi execution contract

- Establish the exact target repository and scope: staged, unstaged/worktree, commit range, file, or PR. Ask if ambiguous. State the baseline and reviewed revision; staged review does not cover unstaged/untracked work. A file audit is not a regression review.
- Parent owns read-only Git/PR retrieval. Use diff commands with external diff/text conversion disabled; do not run project code, hooks, builds, tests or linters. Never stage, checkout, stash, reset, fix, commit, push or post GitHub reviews/comments. Reading a PR does not authorize checking it out into the user's dirty tree.
- For PRs, establish owner/repo/number and exact head/base IDs, use existing authenticated read-only access, and inspect complete pagination/truncation and needed file context at that head. Recheck head before finalizing; changed head invalidates the review. Missing access → stop, not a credential/CLI-install fallback.
- Translate questions into ordinary chat. Source tool grants do not expand pi profiles. Apply the complete source rubric: understand the whole change and intent, challenge the design, identify structural regression and show concrete simpler alternatives. Adapt type checks to the actual language; mark inapplicable checks rather than forcing TypeScript rules.
- Keep structural concerns distinct from correctness/security defects. Line-count thresholds, magic values and style are investigation signals, not automatic high-severity bugs. Explain a concrete maintenance cost and behavior-preserving alternative before recommending structural changes. Respect justified exceptions and avoid refactoring unrelated code merely to satisfy a metric.
- For diff findings, demonstrate the issue is introduced or made reachable by the selected change; label pre-existing issues separately. Cite actual file/line evidence, consequences and a feasible fix. Be direct, not insulting or speculative. Never manufacture findings to satisfy the aggressive name.
- An explicitly requested independent pass uses the existing read-only reviewer through the governed pi subagent workflow, with the rubric path and minimized evidence supplied by the parent. No automatic fanout, shell/MCP grants or nested delegation. Required review failure blocks a claim of independent validation; never silently switch to CLI execution.

## Integrated security pass

Apply this pass alongside the structural rubric on every Thermo-Nuclear Review. A security-only request may focus this pass; report that structural review was not performed. Scale depth to the target's risk without claiming broader coverage than inspected. This is static code review, not a penetration test or an authorization to run attack payloads.

### 1. Build context before hunting vulnerabilities

Map the scoped change's entry points, actors, storage, interacting services and sensitive sinks. Trace meaningful flows from entry to sink through functions, data structures and relevant callers/callees; mark attacker-controlled inputs and transformations. Read unchanged dependencies as needed to understand reachability and defenses, but keep findings tied to the selected scope. Name inaccessible dependencies as coverage gaps rather than silently expanding to unrelated systems.

Build the model from code at the reviewed revision, not remembered vulnerabilities, future commits or prior reports. Revise assumptions when contradicted; use explicit unknowns instead of inventing context.

### 2. State the threat model and required bindings

For each sensitive operation, identify what must remain bound:

**credential ↔ tenant/scope ↔ actor/session ↔ target/resource ↔ action/intent ↔ time/state**

Name the source of truth for each component (database record, verified signed token, server session, configuration), where each binding is enforced, and what the attacker controls. Identify protected data/actions, required permissions, and the additional capability an exploit would grant. Preconditions that already grant that capability do not establish a meaningful vulnerability.

### 3. Generate grounded hypotheses

Construct the smallest counterexample for a missing or weakened binding. Check relevant classes without manufacturing a fixed number of findings:

- **Authentication/authorization:** middleware bypass via alternate handlers; UI-only permissions; unverified token signatures/claims; session reuse across tenants; administrative endpoints relying on obscurity.
- **IDOR/access control:** attacker-obtainable identifiers without ownership checks; missing per-item checks in bulk operations; related-object leaks through REST/GraphQL. Establish how an attacker obtains identifiers—do not assume an unguessable ID is known.
- **Injection/data flow:** untrusted input reaching SQL, command, template or deserialization sinks; path traversal; SSRF via controllable URLs. Inspect actual parameterization, encoding, normalization and destination restrictions, not just function names.
- **Trust boundaries:** client-controlled prices, quantities or privileges; mixing signed and unsigned claims; exposed internal/debug routes; different sources of truth across legacy, feature-flagged and administrative paths.
- **State/concurrency:** check-then-act races, double spending, invalid state transitions, replay/expiry gaps, and parallel paths that evade limits. Check transactions, atomic updates, locks and idempotency rather than assuming they are absent.

### 4. Challenge each hypothesis through the complete path

Trace every precondition and enforcement point. Compare the actor/tenant/resource validated with the actor/tenant/resource actually used; consider mix-and-match inputs and alternate paths. Inspect framework middleware and downstream defenses before concluding that a local missing check is exploitable. Record why hypotheses were refuted or remain unresolved.

“Test” here means static counterexample analysis only. Do not run project code, scanners, test suites, payloads or network probes, create exploit files, or access real secrets/customer records. Runtime-dependent claims remain unverified and include the specific evidence or separately authorized test needed to resolve them.

### 5. Validate impact and scope

Recheck the full chain, plausible attacker access, affected endpoints/operations, incidental mitigations, and whether a lower-impact primitive chains into a material issue. Distinguish durable controls from brittle/non-obvious defenses. For a diff, prove introduction or newly enabled reachability; label pre-existing issues separately.

Prioritize high/critical risks, but do not suppress a substantiated lower-severity defect merely to imitate the upstream severity filter. Keep lower-severity findings separate from the high-impact summary. No unsupported severity escalation and no forced definitive verdict when evidence is missing. Self-challenge is not independent review; the optional governed reviewer contract above remains unchanged.

### 6. Report security findings distinctly

Add a **Security Analysis** section containing threat model, inspected flows, findings and unresolved validation gaps. Each finding includes:

- Severity and evidence status: **code-supported; not runtime-tested**, or **unverified hypothesis** (the latter belongs under gaps, not confirmed findings).
- Exact file/line evidence, affected operations/endpoints, attacker permissions and obtainable inputs.
- Minimal exploit sequence and the new access/state change it enables; use short annotated code excerpts only where they clarify the proof, never real credentials.
- Relevant defenses, preconditions, impact, and a concrete remediation direction consistent with the structural review's recommendations.

If none are supported, say “No substantiated security findings within the inspected scope,” not “secure” or “proved safe.” Missing security-critical context blocks an unqualified approval. Identify potential maintainers from scoped Git history only if requested; authorship is not blame.

## Combined report

Retain the source's assessment, structural concerns, type-safety, size-check, recommendation and suggested-refactoring sections, adding Security Analysis. Lead the overall assessment with material correctness/security blockers; keep structural debt, lower-severity defects and hypotheses distinct. Include coverage, exact scope, uncertainty and tests not run. Approval is advisory—not merge authority. Chat output by default; no raw private diff dumps saved in dotfiles. Source/update policy: `docs/skills.md` in the public dotfiles checkout.

## Security-method provenance and license

Locally incorporated from Nick Nisi's `security-audit` skill and its `security-auditor` agent at reviewed revision `7cd24d602e2c6b897a0a4968b017211ac501ffa8`:

- https://github.com/nicknisi/claude-plugins/blob/7cd24d602e2c6b897a0a4968b017211ac501ffa8/plugins/essentials/skills/security-audit/SKILL.md
- https://github.com/nicknisi/claude-plugins/blob/7cd24d602e2c6b897a0a4968b017211ac501ffa8/plugins/essentials/agents/security-auditor.md

The launcher itself supplies context and delegates; the substantive methodology lives in the agent. This incorporation retains its six phases and invariant-binding analysis, but uses the existing pi scope/orchestration contract: no executable prompt interpolation, assumed `main` baseline, automatic agent launch, mandatory Opus, unsupported exploitability certification, or blanket suppression of lower-severity defects. No new runtime dependency on that checkout. Existing structural-source gates remain unchanged.

### Upstream MIT notice

Copyright (c) 2025 Nick Nisi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
