# Installed capabilities and limits

Codex and Claude Code receive independent copies of this skill and native role files. Their existing settings, instructions, hooks, agents, and permissions are preserved. OpenCode and Pi are untouched.

The source project's `models.json` is authoritative. Change the coder profile there, then rerun its installer for the approved applications and enrolled project. Running agents retain their recorded routing; new agents load the regenerated configuration. Project snapshots update explicitly, not silently.

Native SessionStart/UserPromptSubmit/SubagentStart/Stop hooks register enrolled local sessions. Supported PreToolUse paths check the shared pause flag. Bedtime is recognized as an exact standalone `bedtime`, `/bedtime`, or `/fellowship bedtime` prompt; prose mentioning bedtime does not trigger it. A standalone user prompt `resume fellowship` (or supported `/fellowship resume`) clears the flag. Longer prose does not implicitly resume; an agent must explain the exact command rather than self-resume through Bash. Direct terminal use of the resume helper is available to the user. Natural-language stop requests can still be handled by Gandalf through the bedtime helper before pausing.

While paused, status/checkpoint shell commands may use the installed helper or the exact project-local helper with matching trusted bytes. A modified or older project helper is blocked; use the installed helper or explicitly refresh the project's owned snapshot. Shell expansion/operators remain blocked in these command exceptions. Claude terminal failure/permission-denial events clear only their matching tool calls, and child tool activity is attributed through its native agent identity.

State lives in the local Git common directory under `fellowship/`, so cooperating local worktrees share the flag. It contains metadata and Git status, not copies of source, credentials, or application saves. The helper preserves dirty/untracked work in place and captures a mechanical checkpoint. The agent must also record task intent and next steps in the project's existing handoff/task records. Missing acknowledgments remain unconfirmed; stale rows are not automatically cleared.

Hooks do not kill processes, control remote machines, freeze application time, or guarantee interception of every tool path. In-flight tool calls are tracked until their completion event arrives; native Stop/SessionEnd alone does not clear unfinished tool calls. Native trust/managed policy and bypassed or unsupported hook paths may prevent enforcement. Verify actual hook loading in each client. Nothing modifies native approval policy, hook trust databases, or subscription authentication.

Codex role files inherit the parent's permissions; they cannot impose a separate read-only sandbox. Reviewer non-authorship is a behavior rule there. Claude read-only roles have a native file-reading tool allowlist; checks needing execution go to Gimli or the coordinator. Neither provider's roles gain broader permissions than the parent.

Use one acknowledged coordinator per project. This is local cooperative coordination, not atomic distributed task claiming. Other people's agents use their own identities and credentials, with branches/PRs and explicit assignment acknowledgment. Enrolling a repo does not grant merge/deploy authority or turn on CI protections.
