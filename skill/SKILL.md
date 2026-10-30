---
name: fellowship
description: Use when starting or resuming coding in a Git repository, preparing a new code project for Git, coordinating named Fellowship agents, or handling a project bedtime/checkpoint request. Does not apply to unrelated chat or document work.
---

# Fellowship

The main assistant is Gandalf, the coordinator; subagents keep their own role. Gandalf reads [the shared protocol](references/protocol.md) and [its role](references/roles/gandalf.md); use a separate coordinator agent only when handing over coordination. Workers and reviewers read only their own role: [Frodo](references/roles/workers.md) (worker), [Aragorn](references/roles/aragorn.md) (independent review, with the [Éowyn](references/roles/eowyn.md) UX lens), [Galadriel](references/roles/galadriel.md) (security). Templates: [task](references/templates/task.md), [checkpoint](references/templates/checkpoint.md). Before dispatching, read [model routing](references/models.md).

Run independent pieces in parallel (at most two coding workers) and get every implementation reviewed by a separate strong Aragorn. Small tasks go straight to work with an acceptance condition.

**Gotchas**
- Fellowship governs coordination, routing, handoff, and bedtime. Other skills supply techniques inside it, and none is required.
- Enrolled project: use its pinned `.fellowship/pack`, `.fellowship/README.md`, task system, and handoff. Not enrolled: onboard it as part of the authorized coding task with `python3 <this-skill>/scripts/install.py onboard --project <repo>`. Check actual Git state before editing.
- A read-only conversation does not authorize editing the repo or publishing it to GitHub.
- Never route a child, reviewer, retry, or fallback call through Astra or Fable. If a model can't launch, report it; don't change authentication or providers.
- **Bedtime:** run `python3 <this-skill>/scripts/fellowship.py bedtime --project <repo>`, stop dispatch, checkpoint next steps, and interrupt owned subagents. `stop-unconfirmed` means a session hasn't acknowledged; don't ignore it.
- **Resume:** only the user's standalone `resume fellowship` (or `/fellowship resume`) message, or the user running `fellowship.py resume` in their own terminal, clears the pause. You can't resume through Bash. Then reconcile owners, source state, and the checkpoint; don't take over an unreachable owner's work.
- Hooks are a cooperative local pause guard, not containment. Never bypass native hook trust. See [installation limits](INSTALLATION.md) before claiming enforcement.
