import re
import time
from pathlib import Path

SORTABLE_EXTENSIONS = {
    ".xlsx", ".xls", ".xlsm", ".csv", ".pdf", ".docx", ".doc", ".pptx",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".zip", ".rar", ".7z",
}

IGNORE_PATTERNS = [
    r"^\.",            # .gitignore, .DS_Store, dotfiles
    r"^README",
    r"^CLAUDE\.md$",
    r"^settings",
    r"^\.mcp",
    r"\.gitkeep$",
]


def should_ignore(name):
    if name.lower().endswith(".md"):
        return True
    for pattern in IGNORE_PATTERNS:
        if re.search(pattern, name, re.IGNORECASE):
            return True
    return False


def is_sortable(name):
    return Path(name).suffix.lower() in SORTABLE_EXTENSIONS


def is_locked(path):
    """Best-effort: файл открыт в Excel/Word → PermissionError → считаем занятым."""
    try:
        with open(path, "rb+"):
            return False
    except (PermissionError, OSError):
        return True


def iter_candidates(source_dirs, *, min_age_seconds=120, now=None):
    """Файлы верхнего уровня источников, годные к раскладке.

    Пропускает: каталоги, .md и игнор-паттерны, не-sortable расширения,
    слишком свежие (возраст < min_age_seconds), занятые файлы.
    """
    now = now if now is not None else time.time()
    for d in source_dirs:
        d = Path(d)
        if not d.is_dir():
            continue
        for entry in d.iterdir():
            if not entry.is_file():
                continue
            name = entry.name
            if should_ignore(name) or not is_sortable(name):
                continue
            if now - entry.stat().st_mtime < min_age_seconds:
                continue
            if is_locked(entry):
                continue
            yield entry
