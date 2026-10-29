import json
from pathlib import Path

from pbw_scifi.reads import check_log, solution_rank, wonder_count


def _folder(tmp: Path, upto: int) -> Path:
    for n in range(1, upto + 1):
        (tmp / f"ch{n:02d}.txt").write_text(f"Chapter {n}: T\n\nThe ring spun in chapter {n}.\n")
    return tmp


def _log(folder: Path, after: int, **fields) -> Path:
    data = {"after_chapter": after, "premise": "p", "rules": [], "solutions": [], "wonder": [], "skimmed": []}
    data.update(fields)
    path = folder / f"log_ch{after:02d}.json"
    path.write_text(json.dumps(data))
    return path


SOL = [{"route": "They vent the spine to stop the spin", "p_solution": 0.6},
       {"route": "The captain overrides the reactor", "p_solution": 0.4}]


def test_quotes_anywhere_in_the_log_are_verified(tmp_path):
    f = _folder(tmp_path, 3)
    good = _log(f, 3, solutions=SOL, wonder=[{"chapter": 2, "quote": "The ring spun in chapter 2"}],
                rules=[{"rule": "spin", "evidence": [{"chapter": 1, "quote": "ring spun"}]}])
    assert check_log(good)["passed"] and check_log(good)["evidence_count"] == 2
    bad = _log(f, 3, solutions=SOL, skimmed=[{"chapter": 3, "quote": "the ring stopped", "why": "x"}])
    assert not check_log(bad)["passed"]


def test_solution_probabilities_must_sum_to_one(tmp_path):
    log = _log(_folder(tmp_path, 3), 3, solutions=[{"route": "a", "p_solution": 0.5}])
    assert "Solution probabilities do not sum to one" in check_log(log)["errors"]


def test_staged_folder_must_stop_at_the_checkpoint_unless_finished(tmp_path):
    log = _log(_folder(tmp_path, 4), 3, solutions=SOL)
    assert not check_log(log)["passed"]
    assert check_log(log, finished=True)["passed"]


def test_solution_rank_matched_absent_and_ambiguous(tmp_path):
    log = _log(_folder(tmp_path, 3), 3, solutions=SOL)
    assert solution_rank(log, [r"vent\w*.*spine"]) == {"status": "matched", "rank": 1, "p": 0.6, "matches": [0]}
    assert solution_rank(log, [r"radio"]) == {"status": "absent", "rank": 3, "p": 0.0, "matches": []}
    amb = solution_rank(log, [r"the"])
    assert amb["status"] == "ambiguous" and amb["rank"] is None and amb["matches"] == [0, 1]


def test_wonder_count(tmp_path):
    log = _log(_folder(tmp_path, 3), 3, solutions=SOL, wonder=[{"chapter": 1, "quote": "ring spun"}])
    assert wonder_count(log) == 1
