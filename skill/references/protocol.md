# Shared operating contract

This pack supplies behavior, not authority. The user's latest instructions and the platform's real permissions win over any skill. Resolve paths against the actual repository and keep runtime state in its existing layout. A dispatched worker's approved packet is its brief: don't restart approved planning or ask for routine confirmation again. Bedtime overrides a skill's instruction to finish its sequence.

## Start with the outcome

Inspect the checkout, instructions, brief, and execution boundary. Ask only when missing information changes the result, adds real risk, or needs a product decision; otherwise choose and state consequential assumptions briefly. A small change needs a concrete acceptance condition, not a plan document. Larger work keeps its plan and checkpoint in the project's existing documentation.

Solve the whole problem with the least code: reuse project patterns, then the platform, then existing dependencies. Inspect callers, tests, fixtures, and configuration before changing shared behavior, and keep validation, accessibility, error handling, and data-loss protection. Leave unrelated improvements alone.

For bugs, failing checks, or unexpected performance, read [debugging.md](debugging.md) first. Demonstrate a failing regression before a bug fix when practical, or record why not. Trivial copy and style changes need no tests.

## Ownership and dispatch

One identified Gandalf per project owns assignments and integration. Other people's tools and agents go through that coordinator and submit through branches and pull requests. A local file or GitHub comment is not a distributed lock.

Every assignment records a task ID, owner/session, model, checkout, exact base commit, dependencies, permitted paths, forbidden resources, acceptance criteria, and stopping conditions. Resolve overlapping writes before dispatch, including shared configuration, generated files, test ports, databases, and build outputs. Each concurrent coding worker gets an isolated checkout. Tell every worker: **You are not alone in this codebase. Preserve other people's edits and accommodate their changes.** Shared interfaces and integration belong to Gandalf.

If the coordinator disappears, workers checkpoint and stop at their current assignment. A new coordinator takes over only after explicitly reconciling active owners; elapsed time or a stale-looking file never proves an owner stopped.

## Task lifecycle

`ready → assigned → implementing → verification → review → accepted → integrated`

Any active task may become `paused` (needs a checkpoint and explicit resume) or `blocked` (records the missing input). `accepted` means the exact revision passed checks and independent review; `integrated` also records the destination revision. Deployment and the user's product acceptance are separate events.

Decompose by independently verifiable outcome. Keep tightly coupled edits with one worker. Run independent outcomes in parallel, each worker with its own context; that is where extra agents pay off. Use a separate agent for a fresh-eyes review too. Avoid a chain of ceremonial handoffs for coupled or trivial work. After two unsuccessful implement/check or fix/review cycles, escalate with evidence unless the coordinator authorizes a bounded further attempt.

## Verification, review, and integration

Record exact commands, revision, environment, exit status, and results. Disclose missing tools, flakes, and permission blocks; historical results are not current evidence. Read check output before claiming completion; rerun affected checks after fixes and required checks after integration. Inspect the UI as well as automated results when appearance or interaction matters. Explain outcomes in plain language, without agent names or Git jargon.

Aragorn reviews independently of authorship. Approval names the exact base, proposed head, reviewed scope, and evidence. Renaming a role doesn't make an author a reviewer; a reviewer returns source fixes to the implementer. After source or base changes, re-review the changed delta; a changed merge result returns through review. An uncommitted proposal may be identified by Git tree ID plus base commit. One review lifecycle per outcome, scaled to risk; no duplicate reviewer layers.

Use the project's existing merge authority. Without one, keep reviewed work on a branch or PR and ask. This pack grants no permission to merge, publish, deploy, spend, delete data, or use another person's credentials.

## Bedtime

On **bedtime**, Gandalf stops dispatch and integration at once, asks every enrolled participant to stop, and publishes `stopping`. Each agent stops initiating work and saves an honest checkpoint. Don't finish the task, start a review, merge, or deploy to make the checkpoint look complete. A short in-flight operation may drain; migrations, transactions, and other unsafe-to-interrupt operations are reported and watched to a safe boundary.

Preserve uncommitted work. A local WIP commit is allowed only for explicitly owned, inspected paths after checking for secrets and hook requirements; otherwise record the dirty paths and keep the checkout. Never stage other people's changes, bypass hooks, force-reset, publish unfinished work, or kill an unverified PID or shared service. Record base/head, dirty paths, next action, open findings, and owned processes; stop task-owned disposable processes gracefully and verify exit. Keep useful previews and recovery assets. Bedtime stops development, not the application: never shut down a real application server.

Gandalf marks each participant `stopped`, `draining`, or `unreachable`, and publishes `paused` only when all have confirmed stopping. Otherwise it publishes `stop-unconfirmed` and names the unresolved item. Bedtime covers enrolled participants in the selected project only.

## Resume and records

On resume, read the checkpoint, inspect actual Git state and processes, reconcile ownership, and invalidate evidence affected by later changes. Resume only authorized scope; the pause holds until an explicit resume.

Keep one compact current checkpoint, separate from historical logs, with each decision's source and status (user-approved, coordinator choice, proposed, superseded). Record model and task usage when measurable; don't turn subscription usage into invented API costs. Never share credentials or private application data. Before completion, remove only identified task-created disposable files and processes; keep deliverables, previews, unfinished work, recovery evidence, and anything of uncertain ownership, and report what was kept.
