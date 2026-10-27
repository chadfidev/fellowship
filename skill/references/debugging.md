# Debugging a concrete failure

1. Reproduce the observed failure with the smallest useful case. Read the full error and current check output. If reproduction is unavailable, record the missing evidence and gather it before guessing.
2. Inspect the relevant code, its callers, recent changes, and a working comparison. Trace incorrect input or state back to its source. At a component boundary, inspect the actual input/output and configuration without exposing secrets.
3. State one cause supported by that evidence. Test it with a bounded experiment that distinguishes it from alternatives. Change one cause at a time; a failed experiment is evidence for the next investigation.
4. Add an observable failing regression when practical. Fix the cause in the shared code with the smallest complete change, including affected callers and fixtures. Run the regression and relevant neighboring checks, and inspect their results.
5. Return the exact proposed revision and evidence through the shared protocol's independent review. Disclose what is observed, inferred, or still blocked. Use the protocol's retry bound when attempts keep failing; do not stack speculative fixes.

These practices were informed by Superpowers; see [its MIT notice](SUPERPOWERS-LICENSE.txt). Fellowship's shared protocol owns the lifecycle and stopping rules.
