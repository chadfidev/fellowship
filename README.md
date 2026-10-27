# Fellowship

Describe a coding outcome in **Codex or Claude Code**. Fellowship handles proportionate clarification and planning, implementation, debugging, useful tests, independent review, and continuity. Small tasks proceed directly; existing approved briefs stay approved. No agent names, skill commands, Superpowers, or Ponytail installation are required for everyday use.

## Install

Requirements: **macOS or Linux, Python 3.11+, Git**, and your own authenticated Codex or Claude Code account. Native Windows is unsupported because the pause helper uses POSIX locking. There is no daemon or extra Python dependency.

Clone into your normal development folder, then choose the application you want configured:

```sh
git clone https://github.com/chadfidev/fellowship.git
cd fellowship
python3 -B -m unittest discover -s tests -v
python3 -B install.py install --app codex
```

For Claude Code instead:

```sh
python3 -B install.py install --app claude
```

For both, use `--app both`. Without `--app`, the installer chooses the sole existing app home; if the choice is ambiguous, it asks you to select one through the command. It never creates an unselected application's home. Defaults are `~/.codex` (or `CODEX_HOME`) and `~/.claude`; `--codex-home` and `--claude-home` support explicit alternative locations and disposable fixtures.

The installer adds independent copies under each selected home's `skills/fellowship/` and `agents/`, a narrow instruction block, native hooks, and an ownership receipt. Existing accounts, providers, main-model choices, permissions, unrelated instructions, hooks, and plugins are preserved. Review the source before installing. Native trust prompts still apply; in Codex, review new or changed hooks through `/hooks` when requested.

Open a **fresh chat in your project and describe the task**. Global instructions point to the installed skill for coding requests; the skill also describes its relevant activation scope. Unrelated chat and document work stay outside the coding workflow. Skill selection is model behavior, not a guarantee enforced by an installer. No inference runs during installation or fixture tests.

## Everyday work

The main assistant checks the actual project, preserves existing instructions and dirty work, and prepares enrollment on the first authorized coding task. New code projects can initialize Git first. There is no installation-time repository scan. Read-only conversations do not authorize enrollment, and enrollment does not resume paused feature work.

A small change needs an acceptance condition; multi-step work gets a short plan, and larger work gets a durable checkpoint. Bugs are reproduced and investigated before fixes. Meaningful behavior gets observable regression checks where practical. Appearance and interaction require browser/UI inspection when relevant. The assistant inspects current results and obtains one independent review of the exact proposed revision, returning fixes through the same review lifecycle.

Enrollment pins contracts in `.fellowship/`, adds native project agents and managed pointers in `AGENTS.md` and `CLAUDE.md`, and preserves existing files. Collaborators can commit the generated setup; personal settings, credentials, and pause state do not travel with it. To enroll or explicitly refresh a snapshot yourself:

```sh
python3 -B install.py onboard --project '/absolute/path/to/repo'
```

Roles are optional internal responsibilities, not a permanently staffed team. The main assistant coordinates; at most two concurrent coding workers use isolated checkouts, with independent acceptance review. Solo changes do not require a new worktree. See the [behavior contracts](skill/references/START-HERE.md).

## Models

[`models.json`](models.json) is the routing source. Ordinary Codex coordination and work use **Luna/high**; independent review and bounded hard problems use **Sol/high**, with the reason stated. Claude uses **Haiku** for general work, **Sonnet** for medium complexity through the native invocation override, and **Opus** for important work and review. Twelve native profiles per app cover the existing responsibilities; no model entitlement is implied.

The user's selected main-session model remains selected. **Astra and Fable are main-session-only choices** and are forbidden for all children, helpers, reviews, retries, and fallbacks; dispatch must select an allowed child model explicitly when needed. Unavailable models are reported without changing authentication or providers. An already configured Pi/local worker is optional, with the same ownership, checking, and independent review rules; Fellowship installs no Pi platform and launches no models during setup.

## Bedtime and continuation

Send **`bedtime`** as a standalone user message in an enrolled hooked chat. The assistant stops new assignments and integration, checkpoints promptly, preserves dirty work, and stops reachable owned participants. Review and merging wait for explicit resume.

The helper reports `paused` only when registered sessions have stopped and tracked calls have finished. Otherwise it reports `stop-unconfirmed` with unresolved participants. Local worktrees share state in the Git common directory. Dirty file contents stay in their checkout, so preserve that checkout and its current handoff.

Send **`resume fellowship`** as a standalone user message to continue. Ordinary prose does not clear the pause guard; an agent cannot self-resume through Bash. From your own terminal:

```sh
python3 -B skill/scripts/fellowship.py status --project /path/to/repo
python3 -B skill/scripts/fellowship.py bedtime --project /path/to/repo
python3 -B skill/scripts/fellowship.py resume --project /path/to/repo
```

These are cooperative local controls. Hooks cover supported loaded events, do not kill arbitrary processes, and do not control unrelated chats, remote machines, scheduled jobs, or application services. Native permissions and hook trust remain in force. See [capabilities and limits](skill/INSTALLATION.md).

## Update or uninstall

Update a clean source checkout, run its tests, then repeat the selected app's install command. Keep local routing edits in Git so they can be reconciled; modified managed files or instructions need deliberate reconciliation. Project snapshots refresh only through explicit `onboard`; running assignments retain their routing and boundaries.

```sh
git pull --ff-only
python3 -B -m unittest discover -s tests -v
python3 -B install.py install --app codex
```

To uninstall from a selected application:

```sh
python3 -B install.py uninstall --app codex
python3 -B install.py uninstall --app claude
```

Uninstall removes unchanged receipt-owned assets, its instruction block, and owned hooks. Edited instruction blocks or hooks stop uninstallation before changes so active pointers cannot dangle. Other independently edited managed files are retained and reported for reconciliation. Unrelated configuration and enrolled project snapshots remain; uninstall does not delete project work or pause/recovery evidence.

## Verification and license

Tests use disposable Git repositories and application homes. CI is configured for Python 3.11 on macOS and Linux; see the [verification record](docs/workflow-verification.md) for checks actually run in this change. Host-side activation and hook trust still need a fresh native session. Contributors should read [AGENTS.md](AGENTS.md).

[MIT](LICENSE). Adapted development practices retain the [Superpowers MIT notice](skill/references/SUPERPOWERS-LICENSE.txt); this is attribution, not a runtime dependency. Other separately installed skills are preserved. Fellowship is independent of OpenAI, Anthropic, and the owners of its fictional role names.
