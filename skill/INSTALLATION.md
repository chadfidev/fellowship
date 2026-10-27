# Installed capabilities and limits

Each selected application receives an independent copy of the skill and native role files. Use `install.py install --app codex`, `--app claude`, or explicitly `--app both`; unselected application homes are not created. Their existing settings, instructions, hooks, agents, and permissions are preserved. OpenCode and Pi are untouched. No model is launched for installation or fixture tests.

The installer appends a coding-specific pointer in the native global instruction file. It points to the installed copy under that application's `skills/fellowship/`; activation does not rely solely on a discoverable skill command. The assistant enrolls a project only during authorized coding work. Skill selection and compliance remain model behavior, so installation alone cannot prove every natural-language prompt will invoke it. Unrelated chat/document tasks do not require the workflow. Native hook tests use event fixtures rather than live model inference.

The source project's `models.json` is authoritative. Change the coder profile there, then rerun its installer for the approved applications and enrolled project. Running agents retain their recorded routing; new agents load the regenerated configuration. Project snapshots update explicitly, not silently.

Repeat install to update unchanged owned assets. Ownership conflicts require reconciliation rather than overwriting user edits. `install.py uninstall --app <host>` removes unchanged receipt-owned files, the owned instruction block and hooks while retaining independently modified files and enrolled project snapshots. Edited active instruction blocks or hooks stop uninstallation before mutation so pointers cannot dangle. Read its preservation report before removing any remaining files yourself. It never uninstalls other plugins or removes account configuration.

Native SessionStart/UserPromptSubmit/SubagentStart/Stop hooks register enrolled local sessions. Supported PreToolUse paths check the shared pause flag. Bedtime is recognized as an exact standalone `bedtime`, `/bedtime`, or `/fellowship bedtime` prompt; prose mentioning bedtime does not trigger it. A standalone user prompt `resume fellowship` (or supported `/fellowship resume`) clears the flag. Longer prose does not implicitly resume; an agent must explain the exact command rather than self-resume through Bash. Direct terminal use of the resume helper is available to the user. Natural-language stop requests can still be handled by Gandalf through the bedtime helper before pausing.

While paused, status/checkpoint shell commands may use the installed helper or the exact project-local helper with matching trusted bytes. A modified or older project helper is blocked; use the installed helper or explicitly refresh the project's owned snapshot. Shell expansion/operators remain blocked in these command exceptions. Claude terminal failure/permission-denial events clear only their matching tool calls, and child tool activity is attributed through its native agent identity.

State lives in the local Git common directory under `fellowship/`, so cooperating local worktrees share the flag. It contains metadata and Git status, not copies of source, credentials, or application saves. The helper preserves dirty/untracked work in place and captures a mechanical checkpoint. The agent must also record task intent and next steps in the project's existing handoff/task records. Missing acknowledgments remain unconfirmed; stale rows are not automatically cleared.

Hooks do not kill processes, control remote machines, freeze application time, or guarantee interception of every tool path. In-flight tool calls are tracked until their completion event arrives; native Stop/SessionEnd alone does not clear unfinished tool calls. Native trust/managed policy and bypassed or unsupported hook paths may prevent enforcement. Verify actual hook loading in each client. Nothing modifies native approval policy, hook trust databases, or subscription authentication.

Codex role files inherit the parent's permissions; they cannot impose a separate read-only sandbox. Reviewer non-authorship is a behavior rule there. Claude read-only roles have a native file-reading tool allowlist; checks needing execution go to Gimli or the coordinator. Neither provider's roles gain broader permissions than the parent.

Use one acknowledged coordinator per project. This is local cooperative coordination, not atomic distributed task claiming. Other people's agents use their own identities and credentials, with branches/PRs and explicit assignment acknowledgment. Enrolling a repo does not grant merge/deploy authority or turn on CI protections.

## Native references checked for this release

The current official documentation supports narrow implicit skill selection, native agent files with explicit model overrides, and lifecycle hooks with native permissions. The existing thin integrations remain sufficient; no competing plugin orchestrator is added.

- [Codex skills](https://developers.openai.com/codex/skills): description-based implicit selection and current discovery locations. Fellowship's app-specific copy is reached by its global instruction pointer.
- [Codex subagents](https://developers.openai.com/codex/subagents): native TOML agents, model/reasoning fields, and inherited permissions.
- [Codex hooks](https://developers.openai.com/codex/hooks): `hooks.json`, lifecycle events, and review/trust of changed hooks.
- [Claude skills](https://code.claude.com/docs/en/skills), [subagents](https://code.claude.com/docs/en/sub-agents), and [hooks](https://code.claude.com/docs/en/hooks): personal skill/agent paths, native model aliases and invocation overrides, event payloads, and permission boundaries.

These documentation checks do not establish account entitlement or replace a fresh host session's loading/trust checks. Native macOS fixtures are run locally; Linux remains in the supported platform scope and CI matrix, without a claim that this session ran a Linux host.
