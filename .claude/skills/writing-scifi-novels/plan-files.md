# The book plan (stages 2 and 3)

Files in `series/<slug>/bookN/plan/`, written in this order, one per turn, each under 2,000 words.

## 01_novum_and_solutions.md

- **The novum:** the one "what if" the book is about, in two sentences.
- **The setting:** the closed place, who is inside it, why nobody can simply leave or call for help.
- **The central problem:** what goes wrong, its clock (the deadline), and the cost of failing.
- **The intended solution:** what is done, by whom, with what. Then one line the rules checker reads:

  `Uses rules: R2, R5, R9`

- **The solutions matrix,** four or more rows, the intended one included:

| Solution | Support on the page (chapters) | Why a sharp reader believes it | Why it fails, or why it works | Who argues for it |
|---|---|---|---|---|

Rules for the matrix:
- At least three solutions have real support on the page by the halfway mark.
- One wrong solution is the lead's own, argued aloud and acted on, and fails for a reason already on the page.
- The intended solution's pieces appear early as background, used for something else.
- **Hold-back:** what only the lead knows, and the public story.

## 02a_curve.md

One row per chapter: the probability a sharp reader gives each solution, the front-runner, and what moves the numbers. Design to these limits:
- Checkpoint 1 (about 30%): the reader can state the premise and the rules introduced so far. No solution above .40.
- Checkpoint 2 (50%): the intended solution is not first.
- Checkpoint 3 (70%): the intended solution at .35 or less, with at least three solutions at .15 or more.
- The intended solution not above .80 until the chapter before the turn.

## 02b_rules_and_clues.md

**The rules table.** Every rule the plot relies on, one row each. The checker reads this format:

```
| ID | Rule | Introduced |
|---|---|---|
| R1 | The ring makes one turn a minute | ch 1 |
| R2 | ... | ch 4 |
```

- The "Introduced" chapter is where the rule first appears **on the page**, shown in action, not where it is explained.
- Rules from `SERIES_RULES.md` keep their IDs. Book 2 numbers new rules after the series' last ID.
- No rule the intended solution uses may first appear after 75% (chapter 18 of 24).

**The clue map,** one row per clue:

| ID | Chapter | Clue as shown | Foreground (the louder event) | Innocent reading | Seems to support | Reinterpreted in |
|---|---|---|---|---|---|---|

- At most one clue to the intended solution in any three chapters before two-thirds.
- Each wrong solution gets its own clues that hold up until it is ruled out.

## 03_resolution_map.md

- **Sub-problems:** raised in, doubted in, resolved in. None resolves in the chapter that raises it.
- **The wrong turn:** the lead's own solution, acted on, then broken by a fact already on the page.
- **The proof chain:** each step of the solution, with the rule ID it uses and the chapter that rule appeared in.
- Every wrong solution is closed by the end.

## 04 to 07: chapter skeletons

The mystery engine's planner format, so `paperbackwriter reader` and `paperbackwriter digest` work unchanged:

```
**Ch 1. Title. When. Where.**
- **Event:** what happens.
- **Rule shown:** R1 appears in action (planner note; stripped for the reader).
- **Wonder:** the moment of scale or awe.
- [D]: the lead's own decision.
```

Mark rule and clue IDs in parentheses, e.g. `(R1)`, `(C3)`; the reader tool strips them. Vary chapter endings.

## canon.md

Names, ages, roles; the setting's layout (decks, doors, routes); every number (power, air, distances, times); technology limits; every document's exact wording; the timeline.

## audit.md (stage 3)

1. **Your own pass.** At each checkpoint list only what the plan has shown so far and rank the solutions the way a reader would.
2. **The private reference** for the plan read, written **before** the read: `reference.json` with the candidate directory, the reader folder, SHA-256 of every plan file and digest batch, and `solution_keys`, regexes that identify the intended solution in a reader's own words (test them against two or three paraphrases).
3. Run the plan read (`blind-read.md`), gating each checkpoint with `paperbackwriter-scifi gate`.

Pass when the gate passes all three early checkpoints. Fail means redesign file 01, not rewording.
