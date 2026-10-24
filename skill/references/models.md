# Model routing

This describes the approved routing intent. The installed machine-readable `models.json` and the native role files rendered from it determine actual routes; the preference table below is the original v0.1 baseline, not a second editable configuration. In a project snapshot, read `.fellowship/models.json`; in a native skill, read `../models.json`. Record the actual provider, model ID, and supported effort in each task. A role name never fixes a model permanently.

| Profile | Codex preference | Claude Code preference | Use |
| --- | --- | --- | --- |
| strong | `gpt-6.1-sol` | available Opus, resolved through the native model selector | Decisions, important implementation, and independent review |
| economy | `gpt-6-luna` | available Haiku, resolved through the native model selector | Clear, bounded, readily checked work |
| coder | economy initially | economy initially | Ordinary Frodo/Sam work; replace this row after the user's coder benchmarks |

Exact Claude versions and account availability are resolved at use time. These are preferences, not evidence of entitlement or permission to transfer subscription credentials between products. Use verified native subscription access. Paid API use, extra usage, or a different authentication route needs the applicable user authorization; never silently fall back to a billed API.

| Role | Default profile |
| --- | --- |
| Gandalf | strong |
| Elrond | strong |
| Bilbo | economy |
| Legolas | economy |
| Frodo / Sam | coder |
| Gimli | economy |
| Aragorn | strong |
| Galadriel | strong |
| Éowyn | strong |

Gandalf assigns strong workers for ambiguous behavior, cross-module changes, security, money, migrations, or data-loss risk. A tiny diff can still be important. Economy agents escalate missing requirements or consequential decisions rather than guessing. Keep the independent reviewer strong even when the worker is cheap or local.

Prefer deliberate effort selection: medium for clear implementation and bounded review, high for consequential design or difficult review, when the runtime supports those values. This is a coordinator default, not a claim that effort values are equivalent across providers. Do not override the user's explicit selection or restriction. If the desired model is unavailable, stop dispatch and ask for or use an already authorized alternative; record it. Avoid silent upgrades or degraded review.

**Astra remains prohibited unless the user explicitly selects it as the active Codex model for the current work.** Task importance, historical use, and fallback needs do not grant that selection.

## After benchmarks

The user selects a coder model. Update the source project's `coder` profile in `models.json`, rerun the installer, and explicitly refresh the desired project snapshots through onboarding. Record benchmark evidence and limitations. Other roles keep their assignments. Local candidates need demonstrated bounded task success and a supported native provider before assignment; no new local-model adapter is installed by this release. Preserve existing local models, services, and credentials.

Measure accepted tasks, first-pass verification, review rework, elapsed time, and actual reported usage. Compare successful outcomes rather than tokens per second alone. More agents are not automatically faster or cheaper.
