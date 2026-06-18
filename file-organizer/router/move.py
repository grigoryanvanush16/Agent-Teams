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
