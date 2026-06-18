import argparse
import sys
from datetime import datetime
from pathlib import Path

import yaml

from router.match import load_manifest, match_file
from router.move import safe_move, undo_last_run, undo_since
from router.scan import iter_candidates

HERE = Path(__file__).resolve().parent


def load_config(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def run(config, manifest, dry_run, run_id, matched_only=False, only=None):
    rows = []
    for f in iter_candidates(config["sources"],
                             min_age_seconds=config.get("min_age_seconds", 120)):
        project = match_file(f.name, manifest)
        if only is not None:
            # приоритет считаем по полному манифесту, двигаем только это правило
            if not project or project["name"] != only:
                continue
            dest_dir = Path(project["dest"])
            rule = project["name"]
        elif project:
            dest_dir = Path(project["dest"])
            rule = project["name"]
        elif matched_only:
            continue  # несматченные оставляем на месте
        else:
            dest_dir = Path(config["unsorted_dir"])
            rule = "_не_разобрано"
        safe_move(f, dest_dir, journal_path=config["journal"], rule=rule,
                  layer=1, run_id=run_id, dry_run=dry_run)
        rows.append((f.name, rule, str(dest_dir)))
    return rows


def print_table(rows, dry_run):
    if dry_run:
        sys.stdout.write("DRY-RUN — ничего не перемещено\n")
    for name, rule, dest in rows:
        sys.stdout.write(f"  {name}  ->  {rule}  ({dest})\n")
    sys.stdout.write(f"\nИтого: {len(rows)}\n")


def main(argv=None):
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="File organizer — слой 1")
    parser.add_argument("--config", default=str(HERE / "config.yaml"))
    parser.add_argument("--manifest", default=str(HERE / "projects.yaml"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--matched-only", action="store_true",
                        help="перемещать только сматченные, несматченные оставить на месте")
    parser.add_argument("--only",
                        help="двигать только файлы этого правила (приоритет по полному манифесту)")
    parser.add_argument("--undo", action="store_true")
    parser.add_argument("--undo-since")
    args = parser.parse_args(argv)

    config = load_config(args.config)

    if args.undo:
        n = undo_last_run(config["journal"])
        sys.stdout.write(f"Откат последнего прогона: {n} файл(ов)\n")
        return
    if args.undo_since:
        n = undo_since(config["journal"], args.undo_since)
        sys.stdout.write(f"Откат с {args.undo_since}: {n} файл(ов)\n")
        return

    manifest = load_manifest(args.manifest)
    run_id = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    rows = run(config, manifest, args.dry_run, run_id,
               matched_only=args.matched_only, only=args.only)
    print_table(rows, args.dry_run)


if __name__ == "__main__":
    main()
