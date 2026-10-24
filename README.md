# Fellowship

Portable LOTR agent roles for Codex and Claude Code. OpenCode and Pi are outside this installation.

The source is intentionally small: `install.py` renders the native role definitions and preserves existing app configuration; `skill/scripts/fellowship.py` provides opt-in project checkpoints and a cooperative local pause guard. No daemon or extra dependency is installed.

```sh
python3 -B -m unittest discover -s tests -v
python3 install.py install
python3 install.py onboard --project '/absolute/path/to/repo'
```

Run installation and project enrollment only for authorized targets. A repeat run updates owned files and preserves unrelated configuration; independently modified managed files stop the update for review. Native hook trust stays with the application. Restart/open a fresh session after installing native roles.

Change the coder profile in `models.json` after choosing a benchmark winner, then rerun `install` and explicit `onboard` for the project snapshots you want updated. Profiles are regenerated for both ordinary and important worker variants; reviewers remain on the strong profile. Nothing automatically migrates all existing repos.

Fellowship governs coordination, model routing, handoff, and bedtime. Superpowers supplies relevant development techniques inside the approved packet; Ponytail favors small implementations and only useful agents. The worker's approved packet is its brief, not a prompt to repeat brainstorming. Existing user approvals and project execution boundaries persist.

The hooks track supported local lifecycle/tool events and prevent new supported tool work when pause is active. They cannot kill arbitrary processes or promise complete containment, remote shutdown, or control of sessions that did not load them. Keep unconfirmed participants and in-flight operations visible; preserve application services separately. Codex custom roles inherit the parent sandbox; Claude read-only roles receive a native read-tool allowlist.

`skill/references/` carries the approved behavioral contracts; `skill/INSTALLATION.md` states implemented capabilities and their limits. See `docs/install-plan.md` for scope, acceptance, and compatibility checks.
