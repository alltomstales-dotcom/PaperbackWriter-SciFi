from pbw_scifi.plan import check_plan

SCIFI = ("01_novum_and_solutions.md", "02a_curve.md", "02b_rules_and_clues.md",
         "03_resolution_map.md", "canon.md", "audit.md")


def _plan(tmp_path, words=10):
    for name in SCIFI:
        (tmp_path / name).write_text("word " * words)
    (tmp_path / "WRITER_BRIEF.md").write_text("brief")
    return tmp_path


def test_sci_fi_file_names_satisfy_the_structure_check(tmp_path):
    errors = check_plan(_plan(tmp_path))["errors"]
    assert not any("01_solution_and_suspects" in e or "02b_clues" in e for e in errors)
    assert not any(name in e for e in errors for name in SCIFI)


def test_missing_sci_fi_file_is_reported(tmp_path):
    _plan(tmp_path)
    (tmp_path / "02b_rules_and_clues.md").unlink()
    assert "Missing 02b_rules_and_clues.md" in check_plan(tmp_path)["errors"]


def test_word_cap_applies_to_sci_fi_files(tmp_path):
    _plan(tmp_path)
    (tmp_path / "01_novum_and_solutions.md").write_text("word " * 2000)
    assert "01_novum_and_solutions.md must contain fewer than 2,000 words" in check_plan(tmp_path)["errors"]
