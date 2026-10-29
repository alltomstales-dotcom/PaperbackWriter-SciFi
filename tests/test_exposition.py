from pbw_scifi.exposition import Run, calibrated_threshold, report, runs

TEXT = "Chapter 1: Spin\n\nThe ring turned. " + "word " * 100 + "\n\nMore of the same. " + "word " * 50 + \
       "\n\n“Air,” she said.\n\nAfter that. " + "word " * 10 + "\n\n* * *\n\nNew scene.\n"


def test_runs_break_on_dialogue_and_scene_breaks_and_skip_the_heading():
    assert [r.words for r in runs(TEXT)] == [157, 12, 2]
    assert runs(TEXT)[0].start.startswith("The ring turned.")


def test_straight_and_single_quotes_count_as_dialogue():
    assert [r.words for r in runs("a b\n\n\"Hi,\" he said.\n\nc d\n\n‘Yes,’ she said.\n\ne\n")] == [2, 2, 1]


def test_report_lists_only_runs_over_the_threshold(tmp_path):
    (tmp_path / "ch01.txt").write_text(TEXT)
    assert report(tmp_path, 150) == [{"chapter": 1, "words": 157, "start": runs(TEXT)[0].start}]
    assert report(tmp_path, 400) == []


def test_calibrated_threshold_is_the_rounded_90th_percentile_with_a_floor(tmp_path):
    body = "\n\n“x,” y.\n\n".join("w " * n for n in range(100, 1100, 100))  # runs 100..1000
    (tmp_path / "ch01.txt").write_text("Chapter 1: A\n\n" + body + "\n")
    result = calibrated_threshold(tmp_path)
    assert result["p90"] == 900 and result["threshold"] == 900
    (tmp_path / "ch01.txt").write_text("Chapter 1: A\n\nw w w\n")
    assert calibrated_threshold(tmp_path)["threshold"] == 300
