import json
import shutil
from datetime import datetime
from pathlib import Path


def resolve_collision(dest_dir, name):
    """Непересекающийся путь в dest_dir: при коллизии добавляет ' (2)', ' (3)'."""
    dest_dir = Path(dest_dir)
    target = dest_dir / name
    if not target.exists():
        return target
    stem, suffix = target.stem, target.suffix
    i = 2
    while True:
        candidate = dest_dir / f"{stem} ({i}){suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def _append_journal(journal_path, entry):
    p = Path(journal_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def safe_move(src, dest_dir, *, journal_path, rule, layer, run_id,
              ts=None, dry_run=False):
    """Перемещает src в dest_dir без перезаписи, пишет запись в журнал.

    dry_run=True: возвращает планируемый путь, ничего не двигает и не пишет.
    """
    src = Path(src)
    dest_dir = Path(dest_dir)
    target = resolve_collision(dest_dir, src.name)
    if dry_run:
        return target
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(target))
    _append_journal(journal_path, {
        "ts": ts or datetime.now().isoformat(timespec="seconds"),
        "run_id": run_id,
        "layer": layer,
        "src": str(src),
        "dst": str(target),
        "rule": rule,
    })
    return target


def _read_journal(journal_path):
    p = Path(journal_path)
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def _rewrite_journal(journal_path, entries):
    p = Path(journal_path)
    with open(p, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")


def _move_back(entry):
    dst = Path(entry["dst"])
    src = Path(entry["src"])
    if not dst.exists():
        return False
    src.parent.mkdir(parents=True, exist_ok=True)
    # не перезаписывать, если на исходном месте уже что-то появилось
    target = src if not src.exists() else resolve_collision(src.parent, src.name)
    shutil.move(str(dst), str(target))
    return True


def _undo_entries(journal_path, to_undo, to_keep):
    moved = 0
    for entry in reversed(to_undo):
        if _move_back(entry):
            moved += 1
    _rewrite_journal(journal_path, to_keep)
    return moved


def undo_last_run(journal_path):
    """Откатывает последний прогон (run_id с наибольшим ts)."""
    entries = _read_journal(journal_path)
    if not entries:
        return 0
    last_run = max(entries, key=lambda e: e["ts"]).get("run_id")
    to_undo = [e for e in entries if e.get("run_id") == last_run]
    to_keep = [e for e in entries if e.get("run_id") != last_run]
    return _undo_entries(journal_path, to_undo, to_keep)


def undo_since(journal_path, since_iso):
    """Откатывает все перемещения с ts >= since_iso (ISO-строка)."""
    entries = _read_journal(journal_path)
    to_undo = [e for e in entries if e["ts"] >= since_iso]
    to_keep = [e for e in entries if e["ts"] < since_iso]
    return _undo_entries(journal_path, to_undo, to_keep)
