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
