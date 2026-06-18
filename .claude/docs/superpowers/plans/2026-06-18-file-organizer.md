# File Organizer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Двухслойный помощник, который автоматически и осмысленно раскладывает входящие файлы из Downloads / Telegram / Я.Мессенджера / `.claude` / Desktop по существующим папкам проектов, ничего не теряя и не затирая, с журналом и откатом.

**Architecture:** Быстрый детерминированный слой (`file_router.py` + regex-манифест) раскладывает уверенные совпадения и пишет журнал; всё прочее — в `_не_разобрано/`. Дневной Claude-проход (`claude -p`) разбирает остаток осмысленно и дописывает правила в манифест. Старт — в ручной фазе обучения (подтверждения), затем перевод на Task Scheduler.

**Tech Stack:** Python 3, PyYAML, pytest. Windows / Git Bash. Инструмент живёт в `C:/Users/User/.claude/file-organizer/` (внутри git-репозитория с корнем `C:/Users/User/.claude`).

**Уточнения к спеке (приняты при планировании):**
- Слой 1 трогает только документ/данные-расширения (xlsx, xls, xlsm, csv, pdf, docx, doc, pptx, png, jpg, jpeg, gif, webp, zip, rar, 7z). Код (`.py/.js/...`) и `.md` не двигает — рабочие скрипты в `.claude` остаются на месте.
- Коммитим код и манифест; рантайм (`journal.jsonl`, `reports/`, `_не_разобрано/`, `__pycache__`) — в `.gitignore`. Это уточняет фразу спеки «папку не коммитим» до «не коммитим рантайм».
- Откат опирается на `run_id` (метка запуска), который пишется в каждую запись журнала.

---

## File Structure

```
C:/Users/User/.claude/file-organizer/
├── config.yaml          # источники, пути unsorted/journal, min_age
├── projects.yaml        # манифест правил (имя→dest→keywords)
├── file_router.py       # CLI слоя 1: scan → match → move, dry-run, undo
├── router/
│   ├── __init__.py
│   ├── match.py         # имя файла → проект (regex по манифесту)
│   ├── move.py          # safe_move, коллизии, журнал, undo
│   └── scan.py          # обход источников, фильтры (расширение, md, recent, lock)
├── layer2_prompt.md     # промпт для дневного claude -p прохода
├── tests/
│   ├── test_match.py
│   ├── test_move.py
│   ├── test_scan.py
│   └── test_cli.py
├── reports/             # (gitignored) дневные отчёты слоя 2
├── journal.jsonl        # (gitignored) журнал перемещений
└── .gitignore
```

Запускать pytest из `C:/Users/User/.claude/file-organizer/` (чтобы пакет `router` был на пути).

---

### Task 1: Каркас, зависимости, конфиги

**Files:**
- Create: `file-organizer/.gitignore`
- Create: `file-organizer/router/__init__.py`
- Create: `file-organizer/config.yaml`
- Create: `file-organizer/projects.yaml`

- [ ] **Step 1: Установить зависимости**

Run: `python -m pip install pyyaml pytest`
Expected: успешная установка (или «already satisfied»).

- [ ] **Step 2: Создать `.gitignore`**

`file-organizer/.gitignore`:
```
journal.jsonl
reports/
_не_разобрано/
__pycache__/
*.pyc
.pytest_cache/
```

- [ ] **Step 3: Создать пустой пакет**

`file-organizer/router/__init__.py`:
```python
```
(пустой файл)

- [ ] **Step 4: Создать `config.yaml`**

`file-organizer/config.yaml`:
```yaml
sources:
  - "C:/Users/User/Downloads"
  - "C:/Users/User/Downloads/Telegram Desktop"
  - "C:/Users/User/.claude/.claude"
  - "C:/Users/User/Desktop"
unsorted_dir: "C:/Users/User/.claude/file-organizer/_не_разобрано"
journal: "C:/Users/User/.claude/file-organizer/journal.jsonl"
min_age_seconds: 120
```

- [ ] **Step 5: Создать стартовый `projects.yaml` (черновой, доводим в Task 7)**

`file-organizer/projects.yaml`:
```yaml
- name: renewals
  dest: "C:/Users/User/Desktop/МД/Продления/"
  keywords: ["продлени", "renewal", "сравнен.*продл"]

- name: tz_dwh
  dest: "C:/Users/User/Desktop/МД/3.ТЗ_DWH/"
  keywords: ["^тз ", "^тз_", "техническое задание"]

- name: marketing_analytics
  dest: "C:/Users/User/Desktop/МД/Аналитика/"
  keywords: ["метрик.*маркет", "маркет.*метрик", "глоссарий метрик", "список метрик", "описание метрик"]

- name: callanalytics_sales
  dest: "C:/Users/User/Desktop/МД/Диагностика функций/"
  keywords: ["статусы_", "квалификатор", "оператор", "operations .*\\.csv", "исходящ.*лини"]

- name: sales_reports
  dest: "C:/Users/User/Desktop/МД/КД/"
  keywords: ["отч[её]т продажи", "выгрузка по продажам", "выгрузка по .*лид", "план_мп", "план_лиды"]
```

- [ ] **Step 6: Commit**

```bash
git add file-organizer/.gitignore file-organizer/router/__init__.py file-organizer/config.yaml file-organizer/projects.yaml
git commit -m "feat(file-organizer): каркас, конфиг и стартовый манифест"
```

---

### Task 2: `match.py` — имя файла → проект

**Files:**
- Create: `file-organizer/router/match.py`
- Test: `file-organizer/tests/test_match.py`

- [ ] **Step 1: Написать падающий тест**

`file-organizer/tests/test_match.py`:
```python
import yaml
from router.match import load_manifest, match_file

MANIFEST = [
    {"name": "tz_dwh", "dest": "/x/tz", "keywords": [r"^тз ", r"^тз_"]},
    {"name": "renewals", "dest": "/x/ren", "keywords": [r"продлени"]},
]


def test_match_by_prefix_keyword():
    assert match_file("ТЗ Отчет по опозданиям.docx", MANIFEST)["name"] == "tz_dwh"


def test_match_is_case_insensitive():
    assert match_file("Сравнение_продления.xlsx", MANIFEST)["name"] == "renewals"


def test_no_match_returns_none():
    assert match_file("Портрет.xlsx", MANIFEST) is None


def test_order_is_priority():
    manifest = [
        {"name": "narrow", "dest": "/a", "keywords": [r"отчет продажи"]},
        {"name": "broad", "dest": "/b", "keywords": [r"отчет"]},
    ]
    assert match_file("Отчет продажи 2.0.xlsx", manifest)["name"] == "narrow"


def test_load_manifest_roundtrip(tmp_path):
    f = tmp_path / "m.yaml"
    f.write_text(yaml.safe_dump(MANIFEST, allow_unicode=True), encoding="utf-8")
    loaded = load_manifest(f)
    assert loaded[0]["name"] == "tz_dwh"


def test_load_missing_manifest_returns_empty(tmp_path):
    assert load_manifest(tmp_path / "nope.yaml") == []
```

- [ ] **Step 2: Запустить — убедиться, что падает**

Run: `python -m pytest tests/test_match.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'router.match'`.

- [ ] **Step 3: Реализовать `match.py`**

`file-organizer/router/match.py`:
```python
import re
from pathlib import Path

import yaml


def load_manifest(path):
    """Читает projects.yaml → список проектов. Нет файла → []."""
    p = Path(path)
    if not p.exists():
        return []
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def match_file(filename, manifest):
    """Имя файла → словарь проекта или None.

    Регистронезависимый regex-поиск по keywords. Первый проект
    в порядке манифеста, у которого совпал хоть один keyword, выигрывает.
    """
    for project in manifest:
        for keyword in project.get("keywords", []):
            if re.search(keyword, filename, re.IGNORECASE):
                return project
    return None
```

- [ ] **Step 4: Запустить — убедиться, что проходит**

Run: `python -m pytest tests/test_match.py -v`
Expected: PASS (6 passed).

- [ ] **Step 5: Commit**

```bash
git add file-organizer/router/match.py file-organizer/tests/test_match.py
git commit -m "feat(file-organizer): сопоставление имени файла с проектом"
```

---

### Task 3: `move.py` — безопасное перемещение, коллизии, журнал

**Files:**
- Create: `file-organizer/router/move.py`
- Test: `file-organizer/tests/test_move.py`

- [ ] **Step 1: Написать падающий тест**

`file-organizer/tests/test_move.py`:
```python
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
```

- [ ] **Step 2: Запустить — убедиться, что падает**

Run: `python -m pytest tests/test_move.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'router.move'`.

- [ ] **Step 3: Реализовать `move.py`**

`file-organizer/router/move.py`:
```python
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
```

- [ ] **Step 4: Запустить — убедиться, что проходит**

Run: `python -m pytest tests/test_move.py -v`
Expected: PASS (5 passed).

- [ ] **Step 5: Commit**

```bash
git add file-organizer/router/move.py file-organizer/tests/test_move.py
git commit -m "feat(file-organizer): безопасное перемещение с журналом и коллизиями"
```

---

### Task 4: Откат (`undo`) в `move.py`

**Files:**
- Modify: `file-organizer/router/move.py`
- Test: `file-organizer/tests/test_move.py` (дополняем)

- [ ] **Step 1: Дописать падающие тесты**

Добавить в конец `file-organizer/tests/test_move.py`:
```python
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
```

- [ ] **Step 2: Запустить — убедиться, что падает**

Run: `python -m pytest tests/test_move.py -v`
Expected: FAIL — `ImportError: cannot import name 'undo_last_run'`.

- [ ] **Step 3: Дописать функции отката в `move.py`**

Добавить в конец `file-organizer/router/move.py`:
```python
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
    shutil.move(str(dst), str(src))
    return True


def _undo_entries(journal_path, to_undo, to_keep):
    moved = 0
    for entry in reversed(to_undo):
        if _move_back(entry):
            moved += 1
    _rewrite_journal(journal_path, to_keep)
    return moved


def undo_last_run(journal_path):
    """Откатывает последний прогон (по run_id последней записи)."""
    entries = _read_journal(journal_path)
    if not entries:
        return 0
    last_run = entries[-1].get("run_id")
    to_undo = [e for e in entries if e.get("run_id") == last_run]
    to_keep = [e for e in entries if e.get("run_id") != last_run]
    return _undo_entries(journal_path, to_undo, to_keep)


def undo_since(journal_path, since_iso):
    """Откатывает все перемещения с ts >= since_iso (ISO-строка)."""
    entries = _read_journal(journal_path)
    to_undo = [e for e in entries if e["ts"] >= since_iso]
    to_keep = [e for e in entries if e["ts"] < since_iso]
    return _undo_entries(journal_path, to_undo, to_keep)
```

- [ ] **Step 4: Запустить — убедиться, что проходит**

Run: `python -m pytest tests/test_move.py -v`
Expected: PASS (8 passed).

- [ ] **Step 5: Commit**

```bash
git add file-organizer/router/move.py file-organizer/tests/test_move.py
git commit -m "feat(file-organizer): откат прогона и отбор по дате"
```

---

### Task 5: `scan.py` — обход источников и фильтры

**Files:**
- Create: `file-organizer/router/scan.py`
- Test: `file-organizer/tests/test_scan.py`

- [ ] **Step 1: Написать падающий тест**

`file-organizer/tests/test_scan.py`:
```python
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
```

- [ ] **Step 2: Запустить — убедиться, что падает**

Run: `python -m pytest tests/test_scan.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'router.scan'`.

- [ ] **Step 3: Реализовать `scan.py`**

`file-organizer/router/scan.py`:
```python
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
```

- [ ] **Step 4: Запустить — убедиться, что проходит**

Run: `python -m pytest tests/test_scan.py -v`
Expected: PASS (9 passed).

- [ ] **Step 5: Commit**

```bash
git add file-organizer/router/scan.py file-organizer/tests/test_scan.py
git commit -m "feat(file-organizer): обход источников с фильтрами"
```

---

### Task 6: `file_router.py` — CLI слоя 1

**Files:**
- Create: `file-organizer/file_router.py`
- Test: `file-organizer/tests/test_cli.py`

- [ ] **Step 1: Написать падающий тест**

`file-organizer/tests/test_cli.py`:
```python
import yaml

import file_router


def _setup(tmp_path):
    src = tmp_path / "Downloads"
    src.mkdir()
    dest = tmp_path / "Продления"
    unsorted = tmp_path / "_не_разобрано"
    journal = tmp_path / "journal.jsonl"

    (src / "Сравнение_продления.xlsx").write_text("a")
    (src / "Портрет.xlsx").write_text("b")  # ни одно правило не ловит

    config = tmp_path / "config.yaml"
    config.write_text(yaml.safe_dump({
        "sources": [str(src)],
        "unsorted_dir": str(unsorted),
        "journal": str(journal),
        "min_age_seconds": 0,
    }, allow_unicode=True), encoding="utf-8")

    manifest = tmp_path / "projects.yaml"
    manifest.write_text(yaml.safe_dump([
        {"name": "renewals", "dest": str(dest), "keywords": ["продлени"]},
    ], allow_unicode=True), encoding="utf-8")

    return src, dest, unsorted, config, manifest, journal


def test_dry_run_moves_nothing(tmp_path):
    src, dest, unsorted, config, manifest, journal = _setup(tmp_path)
    file_router.main(["--dry-run", "--config", str(config),
                      "--manifest", str(manifest)])
    assert (src / "Сравнение_продления.xlsx").exists()
    assert not dest.exists()
    assert not journal.exists()


def test_real_run_routes_matched_and_unsorted(tmp_path):
    src, dest, unsorted, config, manifest, journal = _setup(tmp_path)
    file_router.main(["--config", str(config), "--manifest", str(manifest)])
    assert (dest / "Сравнение_продления.xlsx").exists()
    assert (unsorted / "Портрет.xlsx").exists()
    assert not (src / "Сравнение_продления.xlsx").exists()
    assert journal.exists()


def test_undo_after_run_restores(tmp_path):
    src, dest, unsorted, config, manifest, journal = _setup(tmp_path)
    file_router.main(["--config", str(config), "--manifest", str(manifest)])
    file_router.main(["--undo", "--config", str(config),
                      "--manifest", str(manifest)])
    assert (src / "Сравнение_продления.xlsx").exists()
    assert (src / "Портрет.xlsx").exists()
```

- [ ] **Step 2: Запустить — убедиться, что падает**

Run: `python -m pytest tests/test_cli.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'file_router'`.

- [ ] **Step 3: Реализовать `file_router.py`**

`file-organizer/file_router.py`:
```python
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


def run(config, manifest, dry_run, run_id):
    rows = []
    for f in iter_candidates(config["sources"],
                             min_age_seconds=config.get("min_age_seconds", 120)):
        project = match_file(f.name, manifest)
        if project:
            dest_dir = Path(project["dest"])
            rule = project["name"]
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
    run_id = datetime.now().isoformat(timespec="seconds")
    rows = run(config, manifest, args.dry_run, run_id)
    print_table(rows, args.dry_run)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Запустить — убедиться, что проходит**

Run: `python -m pytest tests/test_cli.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Прогнать весь набор тестов**

Run: `python -m pytest -v`
Expected: PASS (все: match 6 + move 8 + scan 9 + cli 3 = 26).

- [ ] **Step 6: Commit**

```bash
git add file-organizer/file_router.py file-organizer/tests/test_cli.py
git commit -m "feat(file-organizer): CLI слоя 1 (scan/match/move, dry-run, undo)"
```

---

### Task 7: Дозаполнить манифест по реальному Downloads (верификация с пользователем)

**Files:**
- Modify: `file-organizer/projects.yaml`

- [ ] **Step 1: Сухой прогон на реальных источниках**

Run (из `C:/Users/User/.claude/file-organizer/`):
`python file_router.py --dry-run`
Expected: таблица «файл -> правило (dest)». Часть файлов уйдёт в `_не_разобрано`.

- [ ] **Step 2: Свериться с пользователем**

Показать пользователю таблицу. Для каждого файла в `_не_разобрано`, который на самом деле относится к проекту, спросить: какой проект и какая папка-назначение. (Это фаза обучения из спеки.)

- [ ] **Step 3: Дописать правила**

Для каждого подтверждённого решения добавить keyword/проект в `file-organizer/projects.yaml`. Узкие правила ставить выше широких. Проверять regex на конкретном имени файла перед добавлением.

- [ ] **Step 4: Повторный сухой прогон до сходимости**

Run: `python file_router.py --dry-run`
Expected: в `_не_разобрано` остаются только реально неоднозначные файлы.

- [ ] **Step 5: Commit**

```bash
git add file-organizer/projects.yaml
git commit -m "feat(file-organizer): манифест под реальный Downloads"
```

---

### Task 8: Промпт слоя 2 для `claude -p`

**Files:**
- Create: `file-organizer/layer2_prompt.md`

- [ ] **Step 1: Написать промпт**

`file-organizer/layer2_prompt.md`:
```markdown
# Слой 2 — дневной разбор `_не_разобрано/`

Ты — помощник по раскладке файлов Вануша. Работаешь автономно, но осторожно.

## Что делать
1. Прочитай манифест `C:/Users/User/.claude/file-organizer/projects.yaml`
   (проекты, их папки `dest`, ключевые слова).
2. Перечисли файлы в `C:/Users/User/.claude/file-organizer/_не_разобрано/`.
3. Для каждого файла определи проект по смыслу: имя файла, при
   необходимости — быстрый просмотр содержимого (первый лист xlsx,
   первая страница pdf/docx). Сопоставь с проектами из манифеста.
4. Если уверен (>= высокая уверенность): перемести файл в `dest`
   проекта командой
   `python C:/Users/User/.claude/file-organizer/file_router.py`
   НЕ подходит для одиночного файла — перемещай через тот же безопасный
   путь: дозапиши временное правило в манифест ИЛИ перемести вручную
   и занеси запись в журнал `journal.jsonl`
   (поля: ts, run_id, layer=2, src, dst, rule).
5. Если по смыслу видно устойчивый признак проекта (например, все
   «*квалификатор*» → callanalytics_sales) — допиши keyword в
   `projects.yaml`, чтобы слой 1 ловил это сам в дальнейшем.
6. По-настоящему неоднозначное оставь в `_не_разобрано/` и добавь рядом
   файл `<имя>.note.txt` с одной строкой: почему не разложил и какие
   варианты.

## Правила безопасности
- Никогда не удаляй и не перезаписывай файлы. Только move; при коллизии
  имени добавляй ` (2)`.
- Не трогай `.md` (они маршрутизируются правилом CLAUDE.md отдельно).
- Каждое перемещение — строкой в `journal.jsonl` (для отката).

## Отчёт
В конце запиши краткий отчёт в
`C:/Users/User/.claude/file-organizer/reports/YYYY-MM-DD.md`:
сколько разложил, какие правила добавил, что осталось спорным.
```

- [ ] **Step 2: Commit**

```bash
git add file-organizer/layer2_prompt.md
git commit -m "feat(file-organizer): промпт дневного слоя 2"
```

---

### Task 9: Регистрация в Task Scheduler (фаза 2 — НЕ запускать до конца обучения)

**Files:** нет (системная задача). Выполнять только после явного подтверждения пользователя, что фаза обучения завершена.

- [ ] **Step 1: Слой 1 каждые 15 минут**

Run (PowerShell, от пользователя):
```powershell
schtasks /Create /TN "FileOrganizerLayer1" /SC MINUTE /MO 15 ^
  /TR "python C:\Users\User\.claude\file-organizer\file_router.py" /F
```
Expected: `SUCCESS: The scheduled task "FileOrganizerLayer1" has successfully been created.`

- [ ] **Step 2: Слой 2 раз в день (09:30)**

Run (PowerShell):
```powershell
schtasks /Create /TN "FileOrganizerLayer2" /SC DAILY /ST 09:30 ^
  /TR "claude -p \"$(Get-Content C:\Users\User\.claude\file-organizer\layer2_prompt.md -Raw)\"" /F
```
Expected: `SUCCESS: ...`
(Точная форма вызова `claude -p` уточняется при настройке — headless-режим с разрешением на запись в указанные папки.)

- [ ] **Step 3: Проверка**

Run: `schtasks /Query /TN "FileOrganizerLayer1"` и `schtasks /Query /TN "FileOrganizerLayer2"`
Expected: обе задачи в списке, статус Ready.

- [ ] **Step 4: Боевой прогон + проверка отката**

Run: `python C:\Users\User\.claude\file-organizer\file_router.py`
затем сверить раскладку и проверить `python file_router.py --undo` на одном прогоне.

---

## Self-Review

**Spec coverage:**
- Источники (4) → config.yaml (Task 1), iter_candidates (Task 5). ✓
- Слой 1 regex/приоритет/unsorted → match.py (Task 2), run() (Task 6). ✓
- Слой 2 понимание + дозапись правил + отчёт → layer2_prompt.md (Task 8). ✓
- Манифест из реального Downloads → Task 7. ✓
- Что не трогаем (.md, README, settings, recent, locked) → should_ignore/iter_candidates (Task 5); расширения-allowlist (уточнение). ✓
- Журнал/откат/без перезаписи/dry-run → move.py (Tasks 3–4), CLI (Task 6). ✓
- Фаза обучения → Task 7 (интерактив) + Task 9 отложен до подтверждения. ✓
- Размещение + .gitignore рантайма → Task 1. ✓
- Тестирование (dry-run, тест-кейсы имён, undo) → тесты в Tasks 2–6 + Task 7/9. ✓

**Placeholder scan:** код приведён в каждом шаге; единственное намеренное уточнение — точная форма вызова `claude -p` в Task 9 (системная зависимость от окружения), помечено явно.

**Type consistency:** `safe_move(..., run_id=...)` един во всех вызовах (Tasks 3,4,6); `match_file` возвращает project-dict с `name`/`dest`, и так используется в `run()`; `iter_candidates(sources, min_age_seconds, now)` сигнатура едина в тестах и CLI. ✓
