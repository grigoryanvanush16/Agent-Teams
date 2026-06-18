import time

from router.scan import should_ignore, is_sortable, iter_candidates


def test_md_is_ignored():
    assert should_ignore("notes.md")


def test_dotfile_is_ignored():
    assert should_ignore(".gitignore")


def test_claude_md_is_ignored():
    assert should_ignore("CLAUDE.md")


def test_normal_file_not_ignored():
    assert not should_ignore("report.xlsx")


def test_excel_lock_file_is_ignored():
    assert should_ignore("~$Бюджет 2026.xlsx")


def test_is_sortable_extensions():
    assert is_sortable("a.PDF")
    assert is_sortable("b.xlsx")
    assert not is_sortable("c.py")
    assert not is_sortable("d.md")


def test_iter_skips_recent_files(tmp_path):
    (tmp_path / "fresh.xlsx").write_text("x")
    # now == сейчас: возраст ~0 < min_age → пропуск
    got = list(iter_candidates([tmp_path], min_age_seconds=120, now=time.time()))
    assert got == []


def test_iter_yields_old_files(tmp_path):
    f = tmp_path / "old.xlsx"
    f.write_text("x")
    got = list(iter_candidates([tmp_path], min_age_seconds=120,
                               now=time.time() + 1000))
    assert f in got


def test_iter_filters_by_extension_and_md(tmp_path):
    (tmp_path / "a.xlsx").write_text("x")
    (tmp_path / "b.py").write_text("x")
    (tmp_path / "c.md").write_text("x")
    (tmp_path / "sub").mkdir()  # каталоги пропускаем
    got = {p.name for p in iter_candidates([tmp_path], min_age_seconds=0,
                                           now=time.time() + 1000)}
    assert got == {"a.xlsx"}


def test_iter_skips_missing_source_dir(tmp_path):
    missing = tmp_path / "nope"
    got = list(iter_candidates([missing], min_age_seconds=0, now=time.time()))
    assert got == []
