import hashlib
import json
from pathlib import Path

import pytest

from pbw_scifi.reads import advance_plan_read, clarity


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_clarity_counts_missing_rules_and_fails_on_a_wrong_one(tmp_path):
    g = tmp_path / "grade_ch07.json"
    g.write_text(json.dumps({"premise_correct": True, "rules": [
        {"id": "R1", "verdict": "stated"}, {"id": "R2", "verdict": "stated"}]}))
    assert clarity(g, ["R1", "R2", "R3"])["passed"]          # 2 of 3, R3 absent = missing
    assert not clarity(g, ["R1", "R2", "R3", "R4"])["passed"]  # 2 of 4
    g.write_text(json.dumps({"premise_correct": True, "rules": [
        {"id": "R1", "verdict": "stated"}, {"id": "R2", "verdict": "wrong"}]}))
    assert clarity(g, ["R1", "R2"])["passed"] is False
    assert clarity(g, ["R1", "R2"])["wrong"] == ["R2"]


def _setup(tmp: Path):
    plan = tmp / "plan"
    (plan / "digest").mkdir(parents=True)
    (plan / "01_novum_and_solutions.md").write_text("Uses rules: R1\n")
    (plan / "02b_rules_and_clues.md").write_text("| R1 | Spin | ch 2 |\n| R2 | Air | ch 5 |\n| R3 | Spine | ch 15 |\n")
    for i, (lo, hi) in enumerate([(1, 7), (8, 12), (13, 17), (18, 21), (22, 24)], 1):
        (plan / "digest" / f"batch{i}.md").write_text(
            "\n\n".join(f"Chapter {n}: T\n\nThe ring spun in chapter {n}." for n in range(lo, hi + 1)) + "\n")
    read = tmp / "read"
    read.mkdir()
    (read / "batch1.md").write_bytes((plan / "digest" / "batch1.md").read_bytes())
    ref = plan / "reference.json"
    ref.write_text(json.dumps({
        "candidate_directory": ".", "reader_folder": "../read", "solution_keys": [r"vent"],
        "plan_sha256": {n: _sha(plan / n) for n in ("01_novum_and_solutions.md", "02b_rules_and_clues.md")},
        "digest_sha256": {p.name: _sha(p) for p in (plan / "digest").glob("batch*.md")}}))
    gate = plan / "gate.json"
    gate.write_text('{"checkpoints": []}')
    return plan, read, ref, gate


def _log(read: Path, after: int, solutions):
    (read / f"log_ch{after:02d}.json").write_text(json.dumps(
        {"after_chapter": after, "premise": "p", "rules": [], "solutions": solutions, "wonder": []}))


def test_checkpoint_one_is_the_clarity_gate(tmp_path):
    plan, read, ref, gate = _setup(tmp_path)
    _log(read, 7, [{"route": "vent it", "p_solution": 0.9}, {"route": "other", "p_solution": 0.1}])
    with pytest.raises(ValueError, match="grade_ch07.json"):
        advance_plan_read(ref, gate, 7)
    (read / "grade_ch07.json").write_text(json.dumps({"premise_correct": True, "rules": [
        {"id": "R1", "verdict": "stated"}, {"id": "R2", "verdict": "stated"}]}))
    record = advance_plan_read(ref, gate, 7)
    assert record["passed"] and (read / "batch2.md").exists()


def test_checkpoint_two_fails_when_the_intended_solution_ranks_first(tmp_path):
    plan, read, ref, gate = _setup(tmp_path)
    _log(read, 7, [{"route": "x", "p_solution": 1.0}])
    (read / "grade_ch07.json").write_text(json.dumps({"premise_correct": True, "rules": [
        {"id": "R1", "verdict": "stated"}, {"id": "R2", "verdict": "stated"}]}))
    advance_plan_read(ref, gate, 7)
    _log(read, 12, [{"route": "vent the spine", "p_solution": 0.5}, {"route": "x", "p_solution": 0.5 - 0.1},
                    {"route": "y", "p_solution": 0.1}])
    (read / "rank_ch12.json").write_text(json.dumps({"route_index": 0}))
    record = advance_plan_read(ref, gate, 12)
    assert not record["passed"] and json.loads(gate.read_text())["stage"] == "FAILED_AT_12"
    assert not (read / "batch3.md").exists()


def test_an_absent_intended_solution_counts_as_hidden(tmp_path):
    plan, read, ref, gate = _setup(tmp_path)
    _log(read, 7, [{"route": "x", "p_solution": 1.0}])
    (read / "grade_ch07.json").write_text(json.dumps({"premise_correct": True, "rules": [
        {"id": "R1", "verdict": "stated"}, {"id": "R2", "verdict": "stated"}]}))
    advance_plan_read(ref, gate, 7)
    _log(read, 12, [{"route": "x", "p_solution": 1.0}])
    (read / "rank_ch12.json").write_text(json.dumps({"route_index": None}))
    assert advance_plan_read(ref, gate, 12)["passed"]


def test_a_changed_plan_file_is_refused(tmp_path):
    plan, read, ref, gate = _setup(tmp_path)
    (plan / "01_novum_and_solutions.md").write_text("Uses rules: R2\n")
    _log(read, 7, [{"route": "x", "p_solution": 1.0}])
    with pytest.raises(ValueError, match="changed"):
        advance_plan_read(ref, gate, 7)


def test_gate_finds_the_digest_under_reader_for_planner_format_plans(tmp_path):
    plan, read, ref, gate = _setup(tmp_path)
    (plan / "reader").mkdir()
    (plan / "digest").rename(plan / "reader" / "digest")   # where `paperbackwriter digest reader` writes it
    _log(read, 7, [{"route": "vent it", "p_solution": 0.9}, {"route": "other", "p_solution": 0.1}])
    (read / "grade_ch07.json").write_text(json.dumps({"premise_correct": True, "rules": [
        {"id": "R1", "verdict": "stated"}, {"id": "R2", "verdict": "stated"}]}))
    assert advance_plan_read(ref, gate, 7)["passed"]
    assert (read / "batch2.md").read_bytes() == (plan / "reader" / "digest" / "batch2.md").read_bytes()


def _pass_seven(read, ref, gate):
    _log(read, 7, [{"route": "x", "p_solution": 1.0}])
    (read / "grade_ch07.json").write_text(json.dumps({"premise_correct": True, "rules": [
        {"id": "R1", "verdict": "stated"}, {"id": "R2", "verdict": "stated"}]}))
    advance_plan_read(ref, gate, 7)


def test_hiding_checkpoint_needs_a_grader_ranking_even_when_no_key_matches(tmp_path):
    plan, read, ref, gate = _setup(tmp_path)
    _pass_seven(read, ref, gate)
    _log(read, 12, [{"route": "override the lockout and scour it", "p_solution": 0.6},
                    {"route": "x", "p_solution": 0.4}])
    with pytest.raises(ValueError, match="rank_ch12.json"):
        advance_plan_read(ref, gate, 12)


def test_the_grader_ranking_overrides_a_key_that_missed(tmp_path):
    plan, read, ref, gate = _setup(tmp_path)
    _pass_seven(read, ref, gate)
    _log(read, 12, [{"route": "override the lockout and scour it", "p_solution": 0.6},
                    {"route": "x", "p_solution": 0.4}])
    (read / "rank_ch12.json").write_text(json.dumps({"route_index": 0}))
    record = advance_plan_read(ref, gate, 12)
    assert not record["passed"] and record["rank"] == 1 and record["probability"] == 0.6
    assert record["key_status"] == "absent"
