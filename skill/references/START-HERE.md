# Fellowship: portable agent behavior pack

Behavior reference for the installed Codex/Claude setup

Gandalf coordinates; the Fellowship handles bounded assignments. The names identify responsibilities, not models or personalities. Communicate plainly: no fantasy dialogue is required.

This pack defines portable behavior. The current installation targets Codex and Claude Code only. An already configured local worker is optional under `models.md`; no Pi integration is installed. Read `../INSTALLATION.md` in a native skill installation, or the project's `.fellowship/README.md` in an enrolled repo, for implemented capabilities and limits. The approved adoption design remains historical. No distributed lock service or remote process supervisor is implemented.

## Read the smallest useful part

- For every participant: [protocol.md](protocol.md).
- For model selection intent: [models.md](models.md); edit the source project's `models.json` for actual routing.
- For an assignment: the relevant role below and [task.md](templates/task.md).
- For returning to a project: [checkpoint.md](templates/checkpoint.md).
- For installed behavior and its limits: [../INSTALLATION.md](../INSTALLATION.md) in the native skill, or the project's `.fellowship/README.md`.

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
- **Change coder model:** update the source `coder` profile in `models.json`, reinstall, and explicitly refresh selected project snapshots. Verify actual availability before new assignments. Running assignments keep their recorded routing unless deliberately stopped and reassigned.

The user evaluates observable outcomes. Agents provide implementation, verification, and review evidence. A passed automated check or another agent's approval does not establish that the user accepts the experience.

## First use

Describe the coding outcome in a fresh project chat. The main assistant prepares enrollment during authorized work, chooses the smallest useful plan, and returns checked results with independent review. Existing paused work and product/deployment decisions remain at their current boundaries.
