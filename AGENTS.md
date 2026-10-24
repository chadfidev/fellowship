# Fellowship contributor instructions

Use Python 3.11+ and the standard library. Run `python3 -B -m unittest discover -s tests -v`. Tests use disposable Git repositories and native-home fixtures; keep their mutations away from real application state.

The shipped installation targets Codex and Claude Code on macOS/Linux. Preserve existing instructions, hook groups, agents, permissions, authentication, and app state. OpenCode and Pi are outside scope. `models.json` is the source of native model routing; `install.py` renders independent app copies and explicitly refreshed project snapshots.

Keep one coordinator, at most two coding workers, and an independent strong reviewer for implementation. Read `skill/references/protocol.md` and only the needed role contract. Review must name the exact revision and relevant evidence. Existing user model restrictions and approvals prevail; a historical review exception never authorizes future model use.

Bedtime means checkpoint promptly and stop, leaving review and integration for explicit resume. Report unfinished calls or missing acknowledgments honestly. Preserve actual project boundaries and peer work. The installer and hooks do not grant merge, publication, deployment or remote-process authority.

For portable changes, verify a clean clone can run tests and install into disposable application homes. Keep private application state, credentials, real project data and local runtime registries out of Git. Document supported platforms and actual hook limitations; do not imply distributed locking or security containment.
