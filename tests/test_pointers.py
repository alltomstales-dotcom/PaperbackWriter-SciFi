from pathlib import Path

from pbw_scifi.pointers import find_pointers, report


def test_flags_a_wink_in_narration():
    text = "The radio was chatter and nobody in the Dock had ears for it."
    hits = find_pointers(text)
    assert [h.phrase for h in hits] == ["nobody in the Dock had ears for it"]


def test_flags_right_answer_and_foreshadowing():
    text = ("She had a feeling of having been given the right answer to a question she had not quite asked.\n\n"
            "It was not hers yet.\n\n"
            "She would remember that later.")
    assert len(find_pointers(text)) == 3


def test_ignores_the_same_words_inside_dialogue():
    text = "“Nobody had ears for it,” said Ana. “Not hers yet.”"
    assert find_pointers(text) == []


def test_ignores_plain_narration():
    text = "The tractor crawled on a few metres, the tracks leaving long twin grooves behind."
    assert find_pointers(text) == []


def test_report_lists_chapter_and_phrase(tmp_path: Path):
    (tmp_path / "ch01.txt").write_text("Chapter 1: A\n\nShe registered it without hearing it.\n", encoding="utf-8")
    (tmp_path / "ch02.txt").write_text("Chapter 2: B\n\nThe pump ran.\n", encoding="utf-8")
    rows = report(tmp_path)
    assert rows == [{"chapter": 1, "phrase": "registered it without hearing it",
                     "sentence": "She registered it without hearing it."}]
