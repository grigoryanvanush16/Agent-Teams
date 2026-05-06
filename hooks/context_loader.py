"""
UserPromptSubmit hook: автоматически подгружает релевантный контекст
по ключевым словам в запросе пользователя.

Триггеры:
- "DWH", "ДВХ", "хранилище", "слой L0/L1/L2/L3" → memory project_dwh.md
- "продление", "renewals" → CLAUDE.md проекта renewals-powerbi
- "Михаил", "автоматизация Михаила" → CLAUDE.md проекта mikhail-replacement
- "развилка", "blocker DWH" → подсказка о ключевых блокерах

Возвращает JSON с дополнительным контекстом или exit 0 без изменений.
"""
import json
import sys
import re
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", line_buffering=True)


TRIGGERS = [
    {
        "patterns": [r"\bDWH\b", r"\bДВХ\b", r"хранилищ", r"\bL[0-3]\b", r"slay\s+[0-3]"],
        "context_files": [
            "C:/Users/User/.claude/projects/c--Users-User--claude/memory/project_dwh.md",
        ],
        "name": "DWH context",
    },
    {
        "patterns": [r"продлен", r"renewals", r"powerbi"],
        "context_files": [
            "C:/Users/User/Projects/renewals-powerbi/CLAUDE.md",
        ],
        "name": "Power BI Renewals context",
    },
    {
        "patterns": [r"михаил", r"mikhail", r"автоматизац\w*\s+михаила"],
        "context_files": [
            "C:/Users/User/Projects/mikhail-replacement/CLAUDE.md",
        ],
        "name": "Mikhail Replacement context",
    },
]


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    prompt = payload.get("prompt", "").lower()
    if not prompt:
        sys.exit(0)

    matched_files = []
    matched_names = []

    for trigger in TRIGGERS:
        for pattern in trigger["patterns"]:
            if re.search(pattern, prompt, re.IGNORECASE):
                matched_names.append(trigger["name"])
                for f in trigger["context_files"]:
                    if f not in matched_files and Path(f).exists():
                        matched_files.append(f)
                break

    if not matched_files:
        sys.exit(0)

    additions = []
    for f in matched_files:
        try:
            content = Path(f).read_text(encoding="utf-8")[:3000]
            additions.append(f"## Auto-loaded: {f}\n\n{content}")
        except Exception:
            continue

    if additions:
        output = {
            "additionalContext": "\n\n---\n\n".join(additions),
            "systemMessage": f"[context_loader] Подгружено: {', '.join(matched_names)}",
        }
        print(json.dumps(output, ensure_ascii=False))

    sys.exit(0)


if __name__ == "__main__":
    main()
