# Shared operating contract

Read this contract and only the role and project context needed for the assignment. Resolve all paths against the actual repository; keep runtime state in that project's existing layout. Use the user's latest instructions and the platform's real permissions. This pack supplies behavior, not additional authority.

Fellowship governs coordination, model routing, handoff, and bedtime. A dispatched worker's approved packet is its brief. Preserve existing user approval instead of restarting approved planning or requesting routine confirmation again. Current user instructions and native managed policy prevail over any skill disagreement. Bedtime takes precedence over a skill's normal instruction to finish its sequence.

## Start with the outcome

Inspect the current checkout, instructions, approved brief, and execution boundary. Ask only when missing information materially changes the result, introduces meaningful risk, or requires a product decision. Make sensible routine choices and state consequential assumptions briefly. A clear request proceeds directly; an approved brief stays approved.

For a small change, identify a concrete acceptance condition and implement it directly. For multi-step work, keep a short plan; for larger work, save the plan and current checkpoint in the project's existing documentation. Decompose by independently verifiable outcome. Keep task records in that existing system; the task template is a checklist for delegation, not a compulsory document for every edit.

Solve the complete requested problem with the least code: reuse the project's patterns, then the standard library or platform, then existing dependencies. Inspect affected callers, tests, fixtures, configuration, and exports before changing shared behavior. Preserve validation, accessibility, error handling, and protections against data loss. Add a dependency or abstraction only when the required outcome needs it. Leave unrelated improvements alone.

For bugs, failing checks, or unexpected performance, read [debugging.md](debugging.md) before proposing a fix. For bugs and meaningful new behavior, demonstrate a failing regression before the fix when practical, then verify observable behavior. Trivial copy and style changes need no artificial tests. Record any reason a regression cannot be reproduced.

## Ownership and dispatch

One explicitly identified Gandalf owns assignments and integration per project. Other tools and other people's agents request or accept assignments through that coordinator and submit their results through branches and pull requests. A local document or GitHub comment is not an atomic distributed lock.

Every assignment records a stable task ID, owner/session identity, current model, checkout/worktree, exact base commit, dependencies, permitted paths, forbidden resources, acceptance criteria, and stopping conditions. Gandalf grants ownership before work starts. Workers acknowledge it. Resolve overlapping writes before dispatch, including shared configuration, generated files, test ports, databases, and build outputs.

Give each concurrent coding worker an isolated checkout/worktree. Isolation does not remove the need to coordinate overlapping files. Tell every worker: **You are not alone in this codebase. Preserve other people's edits and accommodate their changes.** Shared interfaces and integration belong to Gandalf. Use bounded context, with source references rather than the whole parent conversation where supported.

If a coordinator disappears, workers checkpoint and stop at their current bounded assignment. Another coordinator takes over only after explicitly reconciling active owners; elapsed time or a stale-looking file never proves an owner has stopped. Multiple hosts need an acknowledged ownership transfer or a future service providing atomic claims; this pack does not claim to implement one.

## Task lifecycle

`ready → assigned → implementing → verification → review → accepted → integrated`

Any active task may become `paused` or `blocked`. Paused tasks need a checkpoint and explicit resume; blocked tasks record the missing input or capability. `accepted` means the exact revision has satisfied technical checks and independent review. `integrated` additionally records the destination revision. Deployment and the user's product acceptance are separate events.

Decompose by independently verifiable outcome, not number of edits. Keep tightly coupled edits with one worker. Run independent outcomes in parallel, each worker with its own context; that is where extra agents pay off. Use a separate agent for a fresh-eyes review too. Avoid a chain of ceremonial handoffs for coupled or trivial work. For retrying work, the default is two unsuccessful implement/check or fix/review cycles, then escalation with evidence; the coordinator may authorize a specifically bounded further attempt.

## Verification, review, and integration

Workers run relevant checks and record exact commands, revision, environment, exit status, and meaningful results. Missing tools, flaky outcomes, or permission blocks are disclosed; historical results do not become current evidence. Gandalf may reproduce checks independently. Tests should prove required behavior, including a failing regression before a bug fix where feasible.

Inspect check output before claiming completion. When appearance or interaction matters, inspect the browser/UI as well as automated results. Repeat affected checks after fixes; repeat expensive unchanged checks only for a concrete unresolved concern. Explain what works, what was checked, and material limitations in ordinary language, without requiring users to learn agent names or Git terminology.

Aragorn reviews implementation and requirements independently of authorship. Approval names the exact base, proposed head, reviewed diff scope, and evidence. An author cannot approve their own change by renaming their role. A reviewer may inspect and run checks but returns source changes to the implementer. After relevant source or base changes, repeat affected checks and review of the exact proposed revision. After integration, run required integration checks; a changed merge result returns through review.

Use this single independent review lifecycle for the complete outcome, scaled to its risk. Review fixes as a changed delta against the prior reviewed revision; preserve the unchanged review evidence. Do not add duplicate reviewer layers or require a chain of specialist agents for routine work. An uncommitted proposal may use an immutable Git tree ID plus its base commit, covering all proposed source and tests, rather than implying dirty files were reviewed at HEAD.

Use existing project merge authority. Where no authority exists, preserve reviewed work in a branch or PR and request the required decision. This pack grants no blanket permission to merge, publish, deploy, spend, delete data, or access another person's credentials. Branch rules, CI, sandboxes, and access controls enforce boundaries where available; prompts alone do not.

## Bedtime

On **bedtime**, Gandalf stops new dispatch and integration immediately, requests all enrolled participants stop, and publishes `stopping`. Each reachable agent promptly stops initiating work and saves an honest checkpoint. An agent does not finish its planned task, start a review, merge, or deploy merely to make the checkpoint look complete. A short in-flight operation may drain safely; migrations, transactions, and other operations unsafe to interrupt are reported explicitly and monitored to a safe boundary.

Preserve uncommitted work and recovery material. A local WIP commit is permitted only for explicitly owned, inspected paths after checking for secrets and project hook requirements; otherwise record the dirty paths and retain the checkout. Do not stage other people's changes, bypass hooks, force-reset, or publish unfinished work as part of stopping. Never kill an unverified PID or a shared service.

Record exact base/head, dirty paths, next action, unresolved findings, and owned processes/previews. Stop identified task-owned disposable processes gracefully and verify exit. Retain useful user previews and necessary recovery assets, with stop/restart instructions. Stopping development does not change application behavior, pause a game clock, or authorize shutting down a real application server.

Gandalf records each participant as `stopped`, `draining`, or `unreachable`. Publish `paused` only when every enrolled development participant has acknowledged stopping or its stopped state has otherwise been verified. Publish `stop-unconfirmed` when any participant or unsafe in-flight operation remains unconfirmed; give the user the exact unresolved item. The command covers enrolled participants in the selected project unless the user explicitly requests a wider scope. It cannot promise control over unrelated chats, machines, tools, or scheduled jobs.

## Resume and records

On resume, read the current checkpoint, inspect actual Git state and relevant processes, reconcile ownership, and invalidate evidence affected by later changes. Resume only authorized scope. Retain the bedtime pause until an explicit resume request; scheduled jobs must consult and honor the pause once their adapters implement it.

Keep one compact current checkpoint, separate from historical logs. Gandalf records decisions with their source and status: user-approved, coordinator choice, proposed, or superseded. Preserve the original instructions and existing work during adoption. Share reproducible setup instructions, never credentials or private application data. Record model and task usage when measurable; do not translate subscription usage into invented API costs.

Before completion, remove only identified task-created disposable files and stop verified task-owned temporary processes. Keep final deliverables, useful previews, unfinished work, necessary recovery evidence, and anything whose ownership is uncertain. Report retained material and blocked cleanup accurately.
