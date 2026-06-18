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
