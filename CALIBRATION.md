# Calibration

Every change to a gate, threshold, prompt or log schema, with the evidence for it.

| Date | Change | Evidence |
|---|---|---|
| 2026-10-28 | Initial gates from the spec: clarity at ch 7, intended solution not first at 12, ≤ .35 at 17; blind-read targets 7/7/7/7; exposition threshold 400 words (placeholder until calibrated) | Carried over from the mystery engine's measured gates; sci-fi values not yet measured |
| 2026-10-28 | Exposition threshold 400 → **300 words** | *The Invisible Man* (Gutenberg #5230, 29 chapters, 48,162 words): 146 runs, p90 225 (rounds to 200, under the 300 floor), longest 819. Over 300: 9 runs; over 400: 3 runs, all in chapters 26–27, the manhunt told in summary. Glass Island Book 1 (house style) also has p90 225. |
| 2026-10-28 | New command `check-plan` (sci-fi file names) | Found while starting Book 1's plan: the parent's `check-plan` requires mystery file names (`01_solution_and_suspects.md`, `02b_clues.md`) and would always fail a sci-fi plan. The wrapper reuses its outline/digest checks and swaps the names. 3 new tests. |
