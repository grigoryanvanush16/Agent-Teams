import json

from router.move import resolve_collision, safe_move


def test_resolve_no_collision(tmp_path):
    assert resolve_collision(tmp_path, "a.txt") == tmp_path / "a.txt"


def test_resolve_collision_adds_suffix(tmp_path):
    (tmp_path / "a.txt").write_text("x")
    assert resolve_collision(tmp_path, "a.txt") == tmp_path / "a (2).txt"


def test_resolve_collision_increments(tmp_path):
    (tmp_path / "a.txt").write_text("x")
    (tmp_path / "a (2).txt").write_text("x")
    assert resolve_collision(tmp_path, "a.txt") == tmp_path / "a (3).txt"


def test_safe_move_moves_and_journals(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    f = src_dir / "report.xlsx"
    f.write_text("data")
    journal = tmp_path / "journal.jsonl"

    out = safe_move(f, tmp_path / "dst", journal_path=journal,
                    rule="renewals", layer=1, run_id="R1",
                    ts="2026-06-18T10:00:00")

    assert out == tmp_path / "dst" / "report.xlsx"
    assert out.read_text() == "data"
    assert not f.exists()
    entry = json.loads(journal.read_text(encoding="utf-8").strip())
    assert entry["dst"] == str(out)
    assert entry["rule"] == "renewals"
    assert entry["run_id"] == "R1"


def test_safe_move_dry_run_does_nothing(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    f = src_dir / "a.xlsx"
    f.write_text("d")
    journal = tmp_path / "j.jsonl"

    out = safe_move(f, tmp_path / "dst", journal_path=journal,
                    rule="r", layer=1, run_id="R1", dry_run=True)

    assert out == tmp_path / "dst" / "a.xlsx"
    assert f.exists()
    assert not journal.exists()


from router.move import undo_last_run, undo_since


def _seed_two_runs(tmp_path):
    """Создаёт src/dst, делает 2 перемещения в run R1 и одно в R2."""
    src = tmp_path / "src"
    src.mkdir()
    journal = tmp_path / "journal.jsonl"
    for nm in ("a.xlsx", "b.xlsx"):
        f = src / nm
        f.write_text(nm)
        safe_move(f, tmp_path / "dst", journal_path=journal, rule="r",
                  layer=1, run_id="R1", ts="2026-06-18T09:00:00")
    f = src / "c.xlsx"
    f.write_text("c")
    safe_move(f, tmp_path / "dst", journal_path=journal, rule="r",
              layer=1, run_id="R2", ts="2026-06-18T11:00:00")
    return src, journal


def test_undo_last_run_reverts_only_last(tmp_path):
    src, journal = _seed_two_runs(tmp_path)
    n = undo_last_run(journal)
    assert n == 1
    assert (src / "c.xlsx").exists()          # R2 откатан
    assert not (tmp_path / "dst" / "c.xlsx").exists()
    assert (tmp_path / "dst" / "a.xlsx").exists()  # R1 на месте


def test_undo_since_reverts_by_timestamp(tmp_path):
    src, journal = _seed_two_runs(tmp_path)
    n = undo_since(journal, "2026-06-18T10:00:00")
    assert n == 1                              # только R2 (11:00) >= порога
    assert (src / "c.xlsx").exists()
    assert (tmp_path / "dst" / "a.xlsx").exists()


def test_undo_empty_journal_returns_zero(tmp_path):
    assert undo_last_run(tmp_path / "absent.jsonl") == 0


def test_undo_does_not_overwrite_reappeared_source(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    f = src_dir / "report.xlsx"
    f.write_text("original")
    journal = tmp_path / "journal.jsonl"
    safe_move(f, tmp_path / "dst", journal_path=journal, rule="r", layer=1,
              run_id="R1", ts="2026-06-18T09:00:00")
    # на исходном месте появился ДРУГОЙ файл с тем же именем
    (src_dir / "report.xlsx").write_text("new different file")

    undo_last_run(journal)

    # оба файла целы: новый на месте, откатанный — рядом с суффиксом
    assert (src_dir / "report.xlsx").read_text() == "new different file"
    restored = list(src_dir.glob("report (*).xlsx"))
    assert len(restored) == 1
    assert restored[0].read_text() == "original"
