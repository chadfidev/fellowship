---
name: fellowship
description: Use when starting or resuming coding in a Git repository, preparing a new code project for Git, coordinating named Fellowship agents, or handling a project bedtime/checkpoint request. Does not apply to unrelated chat or document work.
---

# Fellowship

Use the user's actual repository and preserve its current execution boundary. Read [the shared protocol](references/protocol.md), then only the relevant [role](references/START-HERE.md). The main assistant is Gandalf; use a separate coordinator agent only when handing over coordination. Spawn independent bounded workers when useful, with at most two coding workers and a separate strong Aragorn for implementation review.

For an enrolled project, use its pinned `.fellowship/pack` contract, `.fellowship/README.md`, existing task system, and current handoff. Before editing, check actual Git state. If it is not enrolled, onboard it as part of the authorized coding task using `python3 <this-skill>/scripts/install.py onboard --project <repo>`; preserve existing instructions and report ownership conflicts. Starting a read-only conversation does not authorize modifying the repo or publishing it to GitHub.

Native role routing is generated from `models.json`. Ordinary Frodo/Sam use the coder profile; important work uses `frodo-important`/`sam-important`, the same personas with strong models. Aragorn remains strong. If a model cannot launch, disclose the block; no silent model/authentication fallback.

**Bedtime:** `python3 <this-skill>/scripts/fellowship.py bedtime --project <repo>`, stop new dispatch/integration, checkpoint rich next steps in the existing task/handoff, and interrupt reachable owned subagents through native controls. Leave review and merging for explicit resume. Read status with the helper. Registered sessions with unfinished tool calls or missing stop acknowledgments produce `stop-unconfirmed`; they are not safe to ignore. Application services and other projects are separate.

**Resume:** in a paused hooked chat, the user sends the standalone `resume fellowship` command (or supported `/fellowship resume`). Longer prose does not clear the flag, and an agent cannot self-resume through Bash; explain the required command if needed. The user may also run `python3 <this-skill>/scripts/fellowship.py resume --project <repo>` directly in their own terminal. After authorized resume, reconcile live owners, actual source state, current instructions and checkpoint. Do not automatically take over work from an unreachable owner.

**Compatibility:** Fellowship controls coordination/routing/handoff/bedtime; Superpowers supplies useful development techniques and Ponytail keeps implementation/staffing small. The approved packet is a dispatched worker's brief. Existing user approval carries forward; do not restart approved design or request routine confirmation again. Follow current user instructions and native policy when any skill disagrees. A persona never authorizes extra tools, publishing, or merge/deployment rights.

Hooks provide a cooperative local pause guard for enrolled sessions, not complete containment or remote shutdown. Existing sessions may need a new turn or restart to load them; Codex may require native hook trust. Never bypass that trust. Read [installation limits](INSTALLATION.md) before claiming runtime enforcement.
