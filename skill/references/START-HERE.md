# Fellowship: portable agent behavior pack

Version 0.2 · October 24, 2026 · Behavior reference for the installed Codex/Claude setup

Gandalf coordinates; the Fellowship handles bounded assignments. The names identify responsibilities, not models or personalities. Communicate plainly: no fantasy dialogue is required.

This pack defines portable behavior. The current installation targets Codex and Claude Code only; OpenCode and Pi remain untouched. Read `../INSTALLATION.md` in a native skill installation, or the project's `.fellowship/README.md` in an enrolled repo, for implemented capabilities and limits. The approved adoption design remains a design reference, not a live status report. No distributed lock service or remote process supervisor is implemented.

## Read the smallest useful part

- For every participant: [protocol.md](protocol.md).
- For model selection: [models.md](models.md), the single routing source.
- For an assignment: the relevant role below and [task.md](templates/task.md).
- For returning to a project: [checkpoint.md](templates/checkpoint.md).
- For installing and proving this across tools: [adoption-plan.md](adoption-plan.md).

| Agent | Responsibility | Load when |
| --- | --- | --- |
| [Gandalf](roles/gandalf.md) | Coordinator and integration owner | Owning the user request or project dispatch |
| [Elrond](roles/elrond.md) | Planner and architecture owner | Work needs design, interface decisions, or dependency planning |
| [Bilbo](roles/bilbo.md) | Task writer and chronicler | Approved decisions need bounded briefs or current handoff records |
| [Legolas](roles/legolas.md) | Scout and researcher | A focused question needs code or primary-source investigation |
| [Frodo and Sam](roles/workers.md) | Implementation workers; identical contract, separate assignments | Changing source within an assigned boundary |
| [Gimli](roles/gimli.md) | Build and verification operator | Running checks and producing reproducible evidence |
| [Aragorn](roles/aragorn.md) | Independent implementation reviewer | A proposed revision is ready for technical acceptance |
| [Galadriel](roles/galadriel.md) | Security specialist | Security-sensitive boundaries or a requested security review need scrutiny |
| [Éowyn](roles/eowyn.md) | User experience and accessibility specialist | User journeys, interaction design, or accessibility need assessment |

These are nine responsibilities across ten names. They are available roles, not ten continuously running agents. Gandalf handles small planning and documentation work directly; a separate Aragorn remains the review boundary for implementation. Start with at most two coding workers. Reader-only agents can run together when platform capacity permits.

## User controls

- **Bedtime:** checkpoint promptly and stop development work; leave review, merging, and new tasks for later.
- **Resume:** reconcile the current checkout, ownership, and checkpoint before continuing the authorized scope.
- **Change coder model:** update the worker routing in `models.md`, verify actual availability, then use it for new assignments. Running assignments keep their recorded routing unless deliberately stopped and reassigned.

The user evaluates observable outcomes. Agents provide implementation, verification, and review evidence. A passed automated check or another agent's approval does not establish that the user accepts the experience.

## Suggested first pilot

Use Agentic Wars' existing instructions, checks, worktrees, and current execution boundary. Do not resume its feature work merely because this pack exists. First prove a small authorized task can move between two tools, survive bedtime, and receive an independent review. Preserve the game's save and running-service decisions separately.
