# Adoption design and implementation sequence

> Historical design, retained for provenance. This is not a current execution plan, review requirement, or permission to resume a pilot. The shared protocol and current installation guide govern the shipped workflow.

## Accepted intent

The user approved a portable operating kit, one coordinator, bounded task packets, independent strong-model review, current checkpoints, reusable onboarding, and the LOTR roster. The user checks observable outcomes. Bedtime means checkpoint promptly and stop; reviews and merges wait. Hermes is deferred. The coder profile will be revisited after the user's benchmarks.

This deliverable completes the behavior definitions and record templates. The phases below remain implementation work; they have not been installed, exercised across tools, or enforced by this Markdown pack.

## Phase 1 — native role loading and routing

Inspect installed versions, supported role formats, configuration ownership, and current permissions in Codex, Claude Code, OpenCode, and Pi. Preserve existing roles and configuration. Implement small native adapters pointing to this shared protocol and role text, with models resolved from `models.md`. Keep provider-specific model/effort handling native. Pi may need an existing extension or explicit session dispatch; do not advertise native subagents unless the actual installed capability proves it.

**Acceptance:** each tool can load an assigned persona with the same bounded contract; actual tool permissions match the intended write boundary; all assignments record the actual model. Unavailable models produce a visible dispatch block or an explicitly authorized alternative. Changing the coder profile changes new worker assignments without changing reviewer routing. Existing unrelated configurations remain intact.

## Phase 2 — safe project onboarding

Build a repeatable onboarding procedure for new and existing repos. Inspect repository instructions and test commands first. Add a short shared entrypoint and tool-specific references using supported native mechanisms. Respect nested instructions. Reuse the existing task/checkpoint layout rather than making parallel records. Pin the kit version in each project and update explicitly; do not silently mutate all repos when a global file changes.

New projects may use a template. Existing projects receive a scoped, reviewable change. A local folder needing version control may be initialized when authorized; publishing a GitHub repository, choosing visibility, enabling actions, and changing access remain explicit project decisions. Use each collaborator's own identity and credentials.

**Acceptance:** rerunning onboarding does not duplicate or overwrite instructions; instructions load in supported tools; an existing dirty repo and nested instructions are preserved; a collaborator can start from a clean clone without personal paths or secrets. Project-specific overrides and authorization boundaries are retained.

## Phase 3 — checkpoint, resume, and actual stop control

Implement a minimal project participant registry and native stop adapters. A registry records identity and ownership; it does not itself provide distributed exclusion. Reuse platform agent/process lifecycle APIs rather than kill-by-PID guesses. Serialize coordinator writes. Make shutdown bounded and idempotent; report unreachable participants or operations still draining. Enroll only controllable tools and scheduled jobs, and make enrolled automation honor persistent pause state.

Keep application services outside development shutdown unless separately authorized. Preserve WIP securely, including untracked owned files; do not equate a WIP commit with review approval. Recheck process identity and actual Git state during resume. Start with a single acknowledged coordinator, not an invented distributed scheduler.

**Acceptance:** bedtime during an edit, test, and review stops dispatch and leaves review/merge for resume; repeating it preserves work; an unreachable agent yields `stop-unconfirmed`; an unsafe operation is visibly draining; coordinator loss stops further assignments; another tool resumes the exact WIP; scheduled work cannot quietly restart the paused project. Shared processes and other people's files survive.

## Phase 4 — Agentic Wars pilot and enforced integration

Use its real project folder and latest execution boundary. Preserve existing dirty files, paused worktrees, save data, previews, hooks, and isolated verification tools. Do not resume the game's feature work under the guise of installing this kit. Reconcile the current handoff's historical instructions through a separately owned documentation change.

Select one authorized bounded task and exercise: tool A starts → bedtime checkpoints → tool B reconciles and resumes → Gimli verifies → independent Aragorn reviews the exact revision → integration follows existing project authority. Configure applicable CI/branch rules only after inspecting account/repository capabilities and authorization. Record verification that the rules actually apply; a local `.github` directory alone proves nothing about enforcement.

**Acceptance:** the task is reproducible from a clean clone, survives handoff without relying on private chat history, and cannot be declared accepted without required evidence. Review becomes stale after a relevant edit. The user can perform the observable acceptance journey. Game behavior and its real save are preserved.

## Scope choices and remaining decisions

- Starting concurrency: at most two coding workers; use specialists only when warranted.
- Dispatch: one acknowledged coordinator per project. True atomic multi-host claims are a later capability if needed.
- Merge policy: retain existing per-project authorization. A universal awake-time auto-merge grant has not been established here.
- Bedtime scope: the selected project and its enrolled participants. Fleet-wide shutdown requires explicit scope and working control adapters.
- Portability target: consistent contracts and evidence, with runtime-specific permissions; identical model performance is not promised.
- Deferred: Hermes, local-model delegation, a new dashboard, new infrastructure, automatic rollout into every existing repo, and deployment automation.

## Three-panel review

Review this behavior pack independently for (1) role boundaries and model routing, (2) coordination, handoff, and bedtime failure modes, and (3) portability, permissions, and adoption claims. Resolve blocking findings before handing it over. Record the reviewed file hashes and panel decisions separately so a later edit does not inherit an old approval.
