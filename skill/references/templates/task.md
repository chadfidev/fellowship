# Task packet

Copy into the project's existing task system. Resolve every required field before assignment; use an explicit `none` or `not yet available` where accurate.

## Assignment

- Task ID and independently verifiable outcome:
- Status and last-updated UTC:
- Coordinator identity/contact mechanism:
- Owner: person/account, tool, agent/session ID, persona:
- Model: provider, exact model ID, supported effort, routing policy version:
- Repository, branch/worktree, exact base commit:
- Approved scope and source of authorization:
- Dependencies and their accepted revisions:
- Owned paths/resources; overlapping ownership resolved by:
- Shared interfaces/contracts and relevant context references:
- Forbidden/out-of-scope resources, including real data and shared services:
- Product questions requiring a decision:
- Stop condition and retry bound:

## Acceptance

- Observable outcome and regression/edge cases:
- Required verification commands and expected behavior:
- Isolated build/test ports, data, outputs, and process ownership:
- Required review(s), independence, and reviewer identity when assigned:
- Existing merge/deploy authority and required checks, or `not authorized`:

## Worker result

- Actual base and proposed exact head; dirty owned paths:
- Behavior delivered and diff scope:
- Checks: command, revision/environment, exit status, result, evidence location:
- Checks not run, failures, and limitations:
- Blockers, disputed decisions, next action:
- Owned processes/previews and cleanup/recovery material:

## Review and integration

- Reviewer/session/model; independence from implementation:
- Verdict; reviewed base/head and diff scope:
- Evidence inspected or rerun; blocking and nonblocking findings:
- Resolution and exact rereviewed revision after fixes:
- Integration destination revision and fresh required integration checks:
- User-observable acceptance: pending/accepted with evidence:

On bedtime, use the checkpoint's participant and WIP fields; a partially filled result remains paused, not accepted. Generated security patches additionally require the security provenance fields defined in `../roles/galadriel.md`.
