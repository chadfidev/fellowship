# Fellowship

A shared workflow for coding agents in **Codex and Claude Code**: one coordinator, small verifiable tasks, independent review, and a `bedtime` command that checkpoints work and stops new supported tool activity.

Fellowship installs native agent profiles and a reusable skill into each application. It pins a copy of its contracts into projects so collaborators can follow the same workflow using their own tools and accounts. No daemon or extra Python package is installed.

## Install on another machine

Requirements: **macOS or Linux, Python 3.11+, Git**, and the Codex/Claude Code applications you intend to use. Native Windows is not supported by the current POSIX locking implementation. Use your own authenticated accounts; no credentials or subscriptions are included.

Clone into your normal development folder. For example:

```sh
mkdir -p ~/Development
cd ~/Development
git clone https://github.com/chadfidev/fellowship.git
cd fellowship
python3 -B -m unittest discover -s tests -v
python3 install.py install
```

The `install` command configures **both** application homes, even if only one application is currently installed. Defaults are `~/.codex` (or `CODEX_HOME`) and `~/.claude`. Override locations when needed:

```sh
python3 install.py install --codex-home /path/to/codex-home --claude-home /path/to/claude-home
```

The installer appends managed instruction/hook entries and preserves unrelated settings, agents and plugins. Ownership receipts prevent overwriting independently changed managed files. Inspect the repository before running it. Native application trust and approval prompts still apply; Fellowship does not approve its own hooks.

Open a **fresh chat** in your project after installation. Global instructions tell the assistant to use Fellowship for coding in Git projects, including newly authorized projects intended for Git. Opening a repository alone does not run an installer or launch agents. Project instructions and native policies still apply.

## Enroll a project

From this source checkout, use the actual project directory:

```sh
python3 install.py onboard --project '/absolute/path/to/repo'
```

The project must already be a Git repository. Enrollment creates `.fellowship/`, native profiles under `.codex/agents/` and `.claude/agents/`, and managed pointers in `AGENTS.md` and `CLAUDE.md`. When needed, it adds narrow ignore exceptions for generated Claude profiles while keeping private Claude state ignored. Review and commit the generated project setup so collaborators receive it. Existing source and dirty work are preserved; enrollment grants no permission to resume a paused feature or publish its files.

The assistant is instructed to enroll a project as part of authorized coding work when needed. You can also run the command explicitly. Nothing automatically scans or modifies all repositories.

## Roles and models

| Agent | Job | Profile |
| --- | --- | --- |
| Gandalf | Main assistant and coordinator | Strong |
| Elrond | Planning and design | Strong |
| Bilbo | Small task briefs and handoffs | Economy |
| Legolas | Focused scouting and research | Economy |
| Frodo / Sam | Implementation; at most two concurrent coding workers | Coder |
| Gimli | Build and verification | Economy |
| Aragorn | Independent implementation review | Strong |
| Galadriel | Security review | Strong |
| Eowyn | User experience and accessibility | Strong |

Frodo and Sam also have `-important` variants that use the strong profile: **12 native profiles per application**. Roles are available when useful; they are not a continuously running swarm. The main assistant is already Gandalf.

[`models.json`](models.json) controls routing. Defaults are Sol 6.1 / Opus for strong work and GPT-6 Luna / Haiku for economy and ordinary coding. All Codex profiles default to high reasoning effort. These are configurable defaults, not guarantees that an account has those models. Set available native model identifiers before installing; unavailable models must be reported rather than silently replaced or billed through another authentication route. This release retains an explicit Astra restriction in its routing policy.

To change your coder after benchmarks, edit the source `coder` profile, rerun `install`, and explicitly rerun `onboard` for each project snapshot you want refreshed. Reviewers stay strong. Running assignments retain their recorded routing.

## Bedtime and resume

Send the standalone user message **`bedtime`** in an enrolled hooked chat. Gandalf stops dispatch/integration, preserves dirty work and checkpoint metadata, records next steps, and stops reachable owned agents. Review and merging wait.

The local helper reports `paused` only when registered participants have acknowledged stopping and no tracked tool calls remain in flight. Otherwise it reports `stop-unconfirmed`. Local Git worktrees share state in the Git common directory; it is not committed or sent to collaborators.

Send **`resume fellowship`** as a standalone user message to explicitly resume. Longer prose does not clear the pause flag, and an agent cannot self-resume through Bash. From your own terminal you can inspect or control an enrolled checkout:

```sh
python3 /path/to/fellowship/skill/scripts/fellowship.py status --project /path/to/repo
python3 /path/to/fellowship/skill/scripts/fellowship.py bedtime --project /path/to/repo
python3 /path/to/fellowship/skill/scripts/fellowship.py resume --project /path/to/repo
```

Checkpoints record revision/status metadata; dirty file contents stay in their checkout. Preserve that checkout and the project's handoff. Resume reconciles live owners, current instructions and actual Git state before continuing the authorized scope.

## Share with other people's agents

Share this repository link and commit each project's generated setup. Each person installs their own trusted native hooks and uses their own credentials. Project-local profiles/contracts travel with the project; personal application configuration and pause state do not.

Keep one acknowledged Gandalf per project. Assign independently verifiable outcomes with an owner, base revision, permitted files, acceptance checks and stopping conditions. Concurrent coding workers use separate worktrees or clones and submit branches/PRs. Review the exact implementation revision independently before integration. Another agent may take over coordination only after reconciling active owners; stale-looking records do not prove an owner stopped.

This provides shared contracts and local cooperative controls, **not distributed task locks or cross-machine shutdown**. Native Codex roles inherit their parent sandbox; a read-only persona is not a separate security boundary. Hooks cover supported loaded event/tool paths and do not kill arbitrary processes or manage application services. See [capabilities and limits](skill/INSTALLATION.md).

Superpowers and Ponytail are optional, separately installed tools. When present, Fellowship governs coordination/routing/handoffs/bedtime, Superpowers supplies task-relevant techniques inside the approved packet, and Ponytail keeps changes and staffing small. Existing user approvals carry forward. Neither plugin is bundled or disabled by this repository. OpenCode, Pi, Hermes and local-model adapters are outside this release.

## Update and contribute

Keep your chosen routing changes in a local commit so Git can reconcile upstream updates; pull when your checkout is clean:

```sh
git pull --ff-only
python3 -B -m unittest discover -s tests -v
python3 install.py install
python3 install.py onboard --project '/absolute/path/to/repo'
```

If Git reports divergence or an installer reports a modified managed file, reconcile it deliberately; preserve local work. Project snapshots update only when explicitly refreshed.

Contributors: read [AGENTS.md](AGENTS.md), keep changes bounded, and run the standard-library test suite above. CI runs the fixture suite on macOS and Linux. Tests exercise disposable repositories and application homes, not real credentials or game saves. [Behavior contracts](skill/references/START-HERE.md) and [installation limits](skill/INSTALLATION.md) describe the shipped workflow; [the adoption design](skill/references/adoption-plan.md) is historical design, not a claim that its deferred phases are implemented.

## License

[MIT](LICENSE). Fellowship is an independent project and is not affiliated with OpenAI, Anthropic or the owners of the fictional character names. The license covers this repository's original code and documentation, not third-party names, branding or separately installed plugins.
