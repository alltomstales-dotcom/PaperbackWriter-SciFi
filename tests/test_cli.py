import json

from pbw_scifi.cli import main


def test_rules_command_exit_codes(tmp_path, capsys):
    (tmp_path / "02b_rules_and_clues.md").write_text("| R1 | Spin | ch 2 |\n| R3 | Spine | ch 20 |\n")
    (tmp_path / "01_novum_and_solutions.md").write_text("Uses rules: R1\n")
    assert main(["rules", str(tmp_path)]) == 0
    (tmp_path / "01_novum_and_solutions.md").write_text("Uses rules: R3\n")
    assert main(["rules", str(tmp_path)]) == 1
    assert "Spine" not in capsys.readouterr().out


def test_bad_input_is_exit_two(tmp_path):
    assert main(["rules", str(tmp_path / "missing")]) == 2


def test_check_plan_command_reports_missing_files(tmp_path, capsys):
    assert main(["check-plan", str(tmp_path)]) == 1
    assert "Missing 01_novum_and_solutions.md" in capsys.readouterr().out


def test_pointers_command_exit_codes(tmp_path, capsys):
    (tmp_path / "ch01.txt").write_text("Chapter 1: A\n\nThe pump ran.\n", encoding="utf-8")
    assert main(["pointers", str(tmp_path)]) == 0
    (tmp_path / "ch02.txt").write_text("Chapter 2: B\n\nIt was not hers yet.\n", encoding="utf-8")
    assert main(["pointers", str(tmp_path)]) == 1
    assert "ch02" in capsys.readouterr().out


def test_spoilers_command_fails_on_a_hit_and_never_prints_the_text(tmp_path, capsys):
    import subprocess
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / "a.md").write_text("all clear\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "a.md"], check=True)
    terms = tmp_path / "terms.txt"
    terms.write_text("\\bwidget\\b\n", encoding="utf-8")
    assert main(["spoilers", "--terms", str(terms), "--repo", str(repo)]) == 0
    (repo / "a.md").write_text("the Widget did it\n", encoding="utf-8")
    assert main(["spoilers", "--terms", str(terms), "--repo", str(repo)]) == 1
    out = capsys.readouterr().out
    assert "a.md:1" in out and "Widget" not in out
    assert main(["spoilers", "--terms", str(tmp_path / "nope"), "--repo", str(repo)]) == 2
