# Self-contained workflow verification

## Delivered scope

Extend the existing shared contract and thin Codex/Claude integrations. Keep coding activation narrow, preserve approved briefs and project boundaries, default ordinary Codex work to Luna/high, require independent Sol/high review, and keep Astra/Fable out of every delegated route. Local workers remain optional. Installation must select its intended application, preserve unrelated state, update safely, and support ownership-aware uninstallation. No inference, credentials, provider changes, or unrelated project implementation are part of setup verification.

## Evidence

- Baseline: `python3 -B -m unittest discover -s tests -v` passed 19 tests on macOS.
- Fixture coverage includes repeated installation, ownership conflicts, unrelated hook/settings/profile preservation, dirty project enrollment, explicit native model profiles, shared worktree pause, unfinished tool calls, missing stop acknowledgments, denied/failed calls, explicit resume, and corrupt-state preservation.
- Current official host skill, agent, and hook documentation was fetched and inspected; sources and capability limits are in [the installation guide](../skill/INSTALLATION.md).
- Development practices were adapted into the shared protocol and a narrowly loaded debugging reference. The distributed MIT notice records Superpowers attribution without a runtime dependency.

The updated macOS fixture suite passes 32 tests, including selected-app detection/ambiguity, forbidden/inherited model routing, modified-block and hook conflicts, exact instruction-byte restoration, receipt traversal/symlink refusal, customized-command and active-path symlink safety (including shell-quoted paths), and selection of the invoking Python interpreter for hooks. `git diff --check` passes. The first temporary-checkout run selected Apple Python 3.9 and failed the Python 3.11+ requirement (`tomllib` unavailable); rerunning with Homebrew Python 3.13.18 passed. Hooks now retain the invoking interpreter, and old installer runtimes receive a clear version error. Historical passing checks do not establish a later revision's correctness.

## Final acceptance — October 27, 2026

An independent Sol/high reviewer approved the complete implementation in one review lifecycle, with no unresolved blocking finding:

- Base commit: `3875a1eaa2cf13d83f5a1fa7f442b8fcf083f3d1`.
- Exact proposed snapshot commit: `c3df8f4bd2ba92908c530daf01226f93bdd9dfd3`.
- Exact proposed tree: `b01f65dff7f976a2b35926c6acb82b9fa35821cb`.
- Both coordinator and reviewer independently ran all 32 tests against that clean snapshot using Python 3.13.18. The coordinator's final run completed in 6.537 seconds with exit 0.
- The reviewer independently reproduced and verified fixes for settings symlinks during update/uninstall, instruction symlinks during uninstall, and customized hook commands including the installer's shell-quoted apostrophe path form. Refused operations preserved configuration, receipts, and helpers. Source fixes returned to the implementer; the reviewer authored no implementation.
- The coordinator also verified disposable dual-host install/reinstall/uninstall, parsed native TOML profiles, retained a selected Astra main model while children used allowed profiles, restored original instruction bytes including CRLF, and preserved an unrelated Claude hook.

These commit/tree identities identify the disposable review snapshot, not a published release or a commit added to the working repository. The snapshot was made from the actual proposed files while leaving the original Git index and existing work intact. Only this final verification record changed afterward; the reviewed implementation, tests, contracts, and installed assets remained unchanged.

## Installation and cleanup

After independent acceptance, both real application homes received independent installations with 34 receipt-owned files and 12 native profiles each. Receipt hashes were verified. Existing instruction prefixes, unrelated hook groups/settings, selected main model/provider configuration, unrelated plugin registrations, and Pi configuration were verified preserved. After an application restart, both receipts still matched and the source still matched the reviewed snapshot. Codex exposed the Fellowship skill and generated native roles in this chat's skill/tool catalogs after restart, verifying discovery; hook trust and natural-language invocation remain separate checks. Fresh-session Claude loading was not exercised.

Codex's native uninstall operation reported Superpowers was already not installed. Claude's native plugin list and Pi's active package/skill configuration contained no Superpowers. A remaining exclusive 67-file temporary Superpowers package source was removed after acceptance; its MIT notice remains distributed with Fellowship. Shared catalogs and unrelated plugins were preserved.

The earlier removal/recovery folder contained only its final human-readable report; that report was updated without creating new backup archives. Authoritative historical project records remain where existing profiling tools, handoffs and proof manifests require their paths. Those records are marked as records only, and no paused feature work, real saves, services, or existing worktrees were changed.

The disposable review clone, temporary manifests and review scratch were removed after transferring their useful result into this record. An existing `tests/__pycache__/test_install.cpython-313.pyc` was retained because ownership could not be established: its code contains only the original three installer tests, with no task-added tests. No model/Pi inference or persistent preview/service was launched for setup or verification. Publication follows the user's separate, explicit commit-and-push authorization; the implementation hashes were rechecked against the approved version before publication.

## Limits

Fixture tests exercise native payloads and generated files without launching models or modifying live personal state. They cannot prove every natural-language request invokes a skill, that an account has a model, or that a native client has trusted and loaded changed hooks. Fresh native sessions and native hook review remain necessary. Linux is in the supported scope and CI matrix; this local verification runs on macOS. The optional skill-creator validator could not run because its environment lacked PyYAML; frontmatter was inspected and Python syntax was parsed without adding a project dependency. Existing application histories and authoritative unfinished project records are outside disposable cleanup.
