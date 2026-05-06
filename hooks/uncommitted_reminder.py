"""
Stop hook: при наличии незакоммиченных изменений в текущем git-репозитории
напоминает запустить агента git-committer.

Ничего не коммитит автоматически — только выводит подсказку.
"""
import json
import subprocess
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", line_buffering=True)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    cwd = payload.get("cwd") or payload.get("workspace") or "."
    cwd_path = Path(cwd)
    if not cwd_path.exists():
        return 0

    try:
        inside = subprocess.run(
            ["git", "-C", str(cwd_path), "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, timeout=3,
        )
        if inside.returncode != 0 or inside.stdout.strip() != "true":
            return 0
    except Exception:
        return 0

    try:
        status = subprocess.run(
            ["git", "-C", str(cwd_path), "status", "--porcelain"],
            capture_output=True, text=True, timeout=5,
        )
    except Exception:
        return 0

    if status.returncode != 0:
        return 0

    lines = [l for l in status.stdout.splitlines() if l.strip()]
    if not lines:
        return 0

    modified = sum(1 for l in lines if l[:2].strip() and not l.startswith("??"))
    untracked = sum(1 for l in lines if l.startswith("??"))

    parts = []
    if modified:
        parts.append(f"{modified} изменённых")
    if untracked:
        parts.append(f"{untracked} новых")
    summary = ", ".join(parts) if parts else f"{len(lines)} файлов"

    repo_name = cwd_path.name
    msg = (
        f"\n[git] В {repo_name} есть незакоммиченные изменения: {summary}. "
        f"Запусти агента git-committer, чтобы разложить по атомарным коммитам.\n"
    )
    print(msg, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
