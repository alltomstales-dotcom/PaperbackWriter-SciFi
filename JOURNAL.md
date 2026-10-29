# Journal

Dated process notes: stage reached, scores, what changed and why. No plot.

- 2026-10-28: Project started. Design agreed with the author: separate repo that depends on the mystery engine (pinned) for genre-neutral tools; near-future closed-setting SF; validated by a two-book series (Book 1 builds the engine, Book 2 runs it frozen). Spec written.
- 2026-10-28: Implementation plan written (12 tasks: engine code test-first, method docs, private versioned books repo, calibration read, Book 1, Book 2). Author asked that every iteration of the books be uploaded as a versioned object: book work goes to a private repo with an annotated tag per iteration.
- 2026-10-28: Engine code complete (7 commands, 30 tests) and method written (skill, templates). Private books repo created (PaperbackWriter-SciFi-Books, tag `init`); every book artefact goes there with a tag per iteration.
- 2026-10-28: Calibration read of *The Invisible Man* (Opus, staged 9/14/20/26/29): overall 7, rules fair 8, earned 7, wonder 8, prose 7, character 6; 290/290 quotes verified. Exposition threshold set to 300 words. Added `check-plan` for sci-fi file names. Book 1 intake and series bible written (private repo, tag `b1-bible-v1`).
- 2026-10-28: Book 1 plan read v1 failed at ch 7 (compound rules; early leak). v2 failed at ch 12 (cure demonstrated mid-book). v3 passed: clarity 13/17, solution rank 3 at .10 (ch 12), rank 2 at .12 (ch 17), .72 at ch 21; verdict 8/7/7/7. The keyword answer key missed passive phrasing twice: graders are now required and authoritative at the hiding checkpoints (39 tests). Post-read polish applied as plan v3.1 (books repo tag `b1-plan-v3.1`); the v3 read describes v3. Next: drafting.
- 2026-10-28: Book 1 drafted by five Sonnet 5.5 agents in order (24 chapters, 49.2k words); planner pass between agents (winks, demonstrating images, an early pointer, two fair-play holes found by the writers' own conflict lists); no exposition run over 300. Tag b1-draft-1. Staged prose blind read started.
- 2026-10-28: Prose read 1 (draft 1): rules fair 8, earned 7, wonder 8, prose 7, character 7, overall 7; quotes 342/342; hiding failed (first from ch 7, obvious ch 8). Causes named by the reader: post-read plants, a skeleton simile, four narrator pointers; plus a chemistry error. Engine: `pointers` check (45 tests), stop rules for hiding failure with passing scores. Plan v3.2; fix pass 1 running.
- 2026-10-28: Fix pass 1 (plan v3.2, four parallel Sonnet agents, tag b1-fix-1). Prose read 2: 6/8/7/7/7/6, hiding improved (ch 7 2nd .20; ch 12 .35; ch 17 .45) but failed; both readers had the cause by ch 3–4 and the cure shares its object. Plan rules added: cause and cure must not share an object; blocked evidence is a signal. Book 1 to proofread, final read, release.
- 2026-10-29: Book 1 proofread (79 hard-error fixes), final read of the released text 8/8/7/8/7/7 (hiding failed, obvious ch 8), released (books repo b1-release, EPUB/PDF/RTF). Engine frozen as engine-v1 for Book 2.
- 2026-10-29: Task 12 started: Book 2 on engine-v1. Plan v1 written under the three Book 1 plan rules (cause and cure share no object; the cause is given early on purpose; no blocked evidence); rules check clean (27 rules); check-plan pass; key tested on 6 paraphrases and 6 near-misses. Books repo tag b2-plan-v1. Plan read v1 running.
- 2026-10-29: Book 2 plan read v1 failed (intended first .25 at ch 12; two jobless plants plus a skeleton wink of mine; read prompt deviation ledgered). Plan v2 moved the plants after the checkpoints. Plan read v2 PASSED all hiding gates (ch 7 clarity 14/17; ch 12 absent; ch 17 .30; ch 21 .60), verdict 8/8/7/8. Late solution rule kept at ch 18 (rules fair 8 ≥ pre-set 7); air clock, chemistry and counts fixed in DRAFTING_NOTES (outside the hashed plan). Tag b2-planread-v2-pass. Drafting next.
- 2026-10-29: Book 2 drafted (5 Sonnet agents, 47.5k words, b2-draft-1). Prose read 1: clarity 16/17; intended ABSENT at ch 7/12/17 (graders null); verdict 8/8/7/8/7/8; obvious ch 19 (the turn) — every target met, first hiding pass in prose. Stakes hole (an honest sum made the main decoy survivable) → fix pass: a plot change after the last checkpoint. Late solution rule kept at ch 18 (ruling). Tag b2-read-1; fix pass running.
- 2026-10-29: Book 2 fix pass (4 parallel Sonnet, shared decisions D1–D5), b2-fix-1. Prose read 2: 8/8/8/8/7/8, obvious ch 18; hiding passes (ch 17 .35 = gate). Read-to-read spread at ch 17: absent / .30 / .35. Found: cabin-air buffer far larger than canon's 16 kg (physics gap since plan v1) → made consistent in proofread, recorded as a planner lesson (physics-check clock numbers before the plan read). b2-read-2. Proofread running.
- 2026-10-29: Book 2 proofread (37 exact-string fixes, b2-proof); final read of the released text 8/8/7/8/7/7, obvious ch 18, hiding pass (absent ch 7/12, .30 ch 17); released (books repo b2-release, EPUB/PDF/RTF, 47,941 words).

## Validation verdict (engine-v1, two books)

| Gate | Book 1 | Book 2 | What a miss needs |
|---|---|---|---|
| Plan read: clarity at ch 7 | pass (v3) | pass (v1 17/18, v2 14/17) | — |
| Plan read: intended not first at ch 12 | pass after 3 plans | fail v1, pass v2 | redesign the plants: give each a job in a wrong solution, move jobless ones past the checkpoint |
| Plan read: intended ≤ .35 at ch 17 | pass | pass (.30) | — |
| Prose: clarity at ch 7 | pass ×3 | pass ×3 (16, 14, 16 of 17) | — |
| Prose: hidden at ch 12 / ch 17 | **fail ×3** | **pass ×3** (absent/absent/absent; absent/.35/.30) | structural: cause and cure must share no object (now a plan rule) |
| Prose: obvious ≥ one before the turn | **fail ×3** (ch 7–8) | pass ×3 (ch 19, 18, 18) | same |
| Verdict scores ≥ 7 | pass ×2 of 3 | pass ×3 (overall 8, 8, 7) | — |
| Quotes verified | ~900/900 | ~885/885 | — |
| Exposition / pointers | 0 / 0 after fixes | 0 / 0 every batch | — |

**Is it predictable?** On Book 2, yes: three independent readers on three versions agree within one point on every score and within .05 at the last hiding checkpoint. The gates fired exactly where a human editor would have pushed back (Book 2 plan v1 at ch 12). The one class of error no gate caught is physics in canon numbers (the cabin-air buffer): add a physics check on the clock's numbers to the plan files before Book 3 or the romance engine.

## 2026-10-29 · Spoiler leak found and gated

The final review found solution terms for both books in public docs and tests. Scrubbed forward; added `spoilers --terms` (private regex list, reports file:line:pattern only) and a local pre-push hook. Earlier commits still contain the old wording; a history rewrite is pending the owner's decision.
