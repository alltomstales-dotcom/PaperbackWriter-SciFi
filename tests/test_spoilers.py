from pathlib import Path

import pytest

from pbw_scifi.spoilers import load_terms, scan


def test_scan_reports_file_line_and_pattern_but_not_the_text(tmp_path: Path):
    (tmp_path / "notes.md").write_text("one\nthe Widget saved them\n", encoding="utf-8")
    hits = scan([tmp_path / "notes.md"], [r"\bwidget\b"], root=tmp_path)
    assert hits == [{"file": "notes.md", "line": 2, "pattern": 1}]


def test_terms_file_skips_comments_and_blank_lines(tmp_path: Path):
    terms = tmp_path / "terms.txt"
    terms.write_text("# names\n\\bAna\\b\n\n\\bwidget\\b\n", encoding="utf-8")
    assert load_terms(terms) == [r"\bAna\b", r"\bwidget\b"]


def test_a_missing_terms_file_is_an_error_not_a_clean_pass(tmp_path: Path):
    with pytest.raises(ValueError, match="terms"):
        load_terms(tmp_path / "nope.txt")
