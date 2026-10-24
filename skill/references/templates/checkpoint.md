# Current project checkpoint

Replace the current checkpoint atomically through the project's established mechanism after reconciling peers. Keep historical reports elsewhere. This template is a record, not a cross-host locking mechanism.

- Project/repository and checkpoint UTC:
- Development state: active / stopping / paused / stop-unconfirmed:
- Coordinator identity; ownership transfer acknowledgment:
- Latest governing user instruction and source:
- Current authorized scope and explicit execution boundary:
- Actual integration branch/base/head and dirty paths:
- Current routing-policy version; any unavailable models:

## Tasks

| Task | Owner/session/tool | State | Worktree/branch and base/head | Owned WIP paths | Verified/reviewed revision | Next action |
| --- | --- | --- | --- | --- | --- | --- |

## Participants and processes

| Participant or owned process | Task and ownership evidence | Stop state and acknowledgment UTC | Retained artifacts | Safe stop/restart or recovery instructions |
| --- | --- | --- | --- | --- |

Use `stopped`, `draining`, or `unreachable` for development participants. Record retained user previews and application services separately; they need not be stopped to pause development. Identify every unconfirmed participant or operation. A stale PID or previous acknowledgment is not current proof after a restart.

## Decisions and evidence

- Current approved decisions and source:
- Coordinator choices and rationale:
- Proposals awaiting product decisions:
- Relevant passed/failed/not-run checks with exact revisions and evidence:
- Independent review verdicts with exact base/head and unresolved objections:
- Data/recovery boundaries and preserved material:
- Cleanup performed, intentionally retained material, and anything blocked:

## Resume

1. Confirm the user's explicit resume request and its scope.
2. Read project instructions and this current checkpoint; inspect actual Git/process state.
3. Reconcile live owners and record any acknowledged coordinator transfer.
4. Resolve contradictions; invalidate checks/reviews affected by changed source or base.
5. Continue the next authorized task; keep unrelated plans and application behavior unchanged.
