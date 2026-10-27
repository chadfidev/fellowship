# Model routing

The source `models.json` and native role files rendered from it determine routes. In a project snapshot, read `.fellowship/models.json`; in a native skill, read `models.json`. Record the actual provider, model ID, and supported effort in assignments. A role name never fixes a model permanently. Respect the user's selected main-session model and existing authentication/provider route.

| Profile | Codex preference | Claude Code preference | Use |
| --- | --- | --- | --- |
| strong | `gpt-6.1-sol` | available Opus, resolved through the native model selector | Bounded hard problems, important implementation, and independent review |
| economy | `gpt-6-luna` | available Haiku, resolved through the native model selector | Clear, bounded, readily checked work |
| coder | economy initially | economy initially | Ordinary Frodo/Sam work; replace this row after the user's coder benchmarks |
| medium | `gpt-6-luna` | `sonnet` | Medium-complexity worker task through a native invocation override |

Exact Claude versions and account availability are resolved at use time. These are preferences, not evidence of entitlement or permission to transfer subscription credentials between products. Use verified native subscription access. Paid API use, extra usage, or a different authentication route needs the applicable user authorization; never silently fall back to a billed API.

| Role | Default profile |
| --- | --- |
| Gandalf | economy; preserve the user's main-session selection |
| Elrond | economy; escalate consequential design |
| Bilbo | economy |
| Legolas | economy |
| Frodo / Sam | coder |
| Gimli | economy |
| Aragorn | strong |
| Galadriel | strong |
| Éowyn | strong |

Gandalf assigns strong workers for ambiguous behavior, cross-module changes, security, money, migrations, or data-loss risk. A tiny diff can still be important. Economy agents escalate missing requirements or consequential decisions rather than guessing. Keep the independent reviewer strong even when the worker is cheap or local.

The installed Codex defaults use high effort for strong, economy, and coder profiles. Prefer deliberate effort selection for task-specific overrides when the runtime supports them; effort values are not equivalent across providers. Do not override the user's explicit selection or restriction. If the desired model is unavailable, stop dispatch and ask for or use an already authorized alternative; record it. Avoid silent upgrades or degraded review.

**Astra and Fable are main-session-only choices when explicitly selected by the user.** Every subagent, helper call, reviewer, retry, and fallback must use another allowed model. When the parent uses either, set the allowed child model explicitly rather than inheriting it. Keep Luna and Sol at high reasoning. An unavailable allowed model is a blocker, not permission to substitute a model or provider.

Ordinary Codex coordination, planning, implementation, checks, and documentation use Luna/high. Escalate to Sol/high for independent review and bounded difficult problems: consequential architecture/shared interfaces, difficult debugging, persistence/migrations, canonical transactions/replay, and security. State the concrete reason. Claude uses Haiku for general work, Sonnet for medium complexity, and Opus for important work and review.

## Optional local worker

An already configured Pi/local worker is an optional peer to native Codex and Claude workers. Choose by task fit, privacy, capability, latency, cost, and coordination overhead. No local-first attempt, permanently staffed lane, or extra worker is required. This release installs no Pi adapter and never launches inference during setup or tests.

If selected, assign an isolated checkout or exclusive file ownership and a self-contained brief with acceptance checks. Run only one local Pi chat-model job at a time. Record the actual invocation, process/job identity, model, owned files, exit status and output; inspect the actual diff and checks before accepting its result. The same independent review applies. Report unavailability without silent routing changes. Track and stop task-owned local work honestly under bedtime; an unanswered stop remains unconfirmed.

## After benchmarks

The user selects a coder model. Update the source project's `coder` profile in `models.json`, rerun the installer, and explicitly refresh the desired project snapshots through onboarding. Record benchmark evidence and limitations. Other roles keep their assignments. Local candidates need demonstrated bounded task success and a supported native provider before assignment; no new local-model adapter is installed by this release. Preserve existing local models, services, and credentials.

Measure accepted tasks, first-pass verification, review rework, elapsed time, and actual reported usage. Compare successful outcomes rather than tokens per second alone. More agents are not automatically faster or cheaper.
