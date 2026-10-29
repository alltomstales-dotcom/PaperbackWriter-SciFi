from pathlib import Path

import pytest

from pbw_scifi.rules import Rule, check_rules, parse_rules, solution_rules

TABLE = """| ID | Rule | Introduced |
|---|---|---|
| R1 | The ring spins once a minute | ch 1 |
| **R2** | Air is rationed by deck | introduced: Ch. 3 |
| R3 | Nobody crosses the spine at night | chapter 20 |
"""


def test_parse_rules_reads_loose_formatting():
    rules = parse_rules(TABLE)
    assert rules["R2"] == Rule("R2", "Air is rationed by deck", 3)
    assert rules["R3"].chapter == 20


def test_series_rows_are_established_before_the_book():
    assert parse_rules("| R9 | Gravity is 0.8 g | book 1 |\n")["R9"].chapter == 0


def test_duplicate_rule_ids_are_an_error():
    with pytest.raises(ValueError, match="R1"):
        parse_rules(TABLE + "| R1 | Again | ch 2 |\n")


def test_an_unreadable_rule_row_is_an_error_not_a_skip():
    with pytest.raises(ValueError, match="R4"):
        parse_rules(TABLE + "| R4 | No chapter column |\n")


def test_solution_rules_reads_the_uses_line():
    assert solution_rules("Intended solution: x\n**Uses rules:** R1, R3 and R2\n") == ["R1", "R3", "R2"]
    with pytest.raises(ValueError):
        solution_rules("no line here")


def _plan(tmp: Path, uses: str, table: str = TABLE) -> Path:
    (tmp / "02b_rules_and_clues.md").write_text(table)
    (tmp / "01_novum_and_solutions.md").write_text(f"Uses rules: {uses}\n")
    return tmp


def test_a_solution_on_early_rules_passes(tmp_path):
    result = check_rules(_plan(tmp_path, "R1, R2"))
    assert result["passed"], result["errors"]
    assert result["cutoff"] == 18


def test_a_solution_rule_introduced_after_75_percent_fails(tmp_path):
    result = check_rules(_plan(tmp_path, "R1, R3"))
    assert result["errors"] == ["R3 is used by the solution but first appears in chapter 20 (after 18)"]


def test_an_unknown_solution_rule_fails(tmp_path):
    assert "R7 is used by the solution but is not in the rules list" in check_rules(_plan(tmp_path, "R7"))["errors"]


def test_book_two_may_add_rules_but_not_redefine_series_rules(tmp_path):
    series = tmp_path / "SERIES_RULES.md"
    series.write_text("| R1 | The ring spins once a minute | book 1 |\n| R8 | Docking needs two keys | book 1 |\n")
    plan = tmp_path / "plan"
    plan.mkdir()
    _plan(plan, "R8, R2")
    assert check_rules(plan, series)["passed"]
    (plan / "02b_rules_and_clues.md").write_text(TABLE.replace("R1 | The ring spins once a minute", "R1 | The ring is still"))
    assert "R1 redefines a series rule" in check_rules(plan, series)["errors"]


def test_errors_never_contain_rule_text(tmp_path):
    result = check_rules(_plan(tmp_path, "R3"))
    assert not any("spine" in e for e in result["errors"])


def test_a_rule_with_more_than_one_claim_is_an_error(tmp_path):
    (tmp_path / "02b_rules_and_clues.md").write_text(
        "| R1 | The ring turns once a minute; the hub has no gravity | ch 2 |\n| R2 | Air leaks hiss | ch 3 |\n")
    (tmp_path / "01_novum_and_solutions.md").write_text("Uses rules: R2\n")
    result = check_rules(tmp_path)
    assert not result["passed"]
    assert "R1 states more than one claim (split it: one claim per rule)" in result["errors"]
    assert "ring" not in " ".join(result["errors"])
