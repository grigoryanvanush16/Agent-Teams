"""
PostToolUse hook: автоформатирование SQL-файлов через sqlfluff.
Запускается после Edit/Write на *.sql файлах в DWH-проектах.

Получает JSON через stdin с информацией о tool_use.
Выходит с exit 0 (успех), либо exit 1 (предупреждение, не блокирует).
"""
import json
import sys
import io
import subprocess
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", line_buffering=True)


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = payload.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path or not file_path.endswith(".sql"):
        sys.exit(0)

    p = Path(file_path)
    if not p.exists():
        sys.exit(0)

    dwh_paths = ("4.DWH_Production", "models", "dbt_project")
    if not any(marker in str(p) for marker in dwh_paths):
        sys.exit(0)

    try:
        result = subprocess.run(
            ["sqlfluff", "fix", "--dialect", "postgres", "--force", str(p)],
            capture_output=True,
            text=True,
            timeout=15,
            encoding="utf-8",
        )
        if result.returncode == 0:
            print(f"[sqlfluff] Formatted {p.name}", file=sys.stderr)
        sys.exit(0)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        sys.exit(0)


if __name__ == "__main__":
    main()
