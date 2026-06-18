# File Organizer

Раскладывает входящие файлы (Downloads, Telegram, Я.Мессенджер, `.claude`, Desktop) по папкам проектов в `Desktop/МД/`. Два слоя: быстрый детерминированный (`file_router.py` + regex-манифест) и дневной осмысленный (`claude -p` по `layer2_prompt.md`).

Дизайн и план: `../.claude/docs/superpowers/specs/2026-06-18-file-organizer-design.md`, `../.claude/docs/superpowers/plans/2026-06-18-file-organizer.md`.

## Файлы
- `config.yaml` — источники, папка `_не_разобрано`, путь журнала, `min_age_seconds`.
- `projects.yaml` — манифест правил (`name` → `dest` → `keywords`). Порядок = приоритет.
- `file_router.py` — CLI слоя 1.
- `router/` — `match.py` (имя→проект), `move.py` (безопасный move + журнал + откат), `scan.py` (обход + фильтры).
- `layer2_prompt.md` — промпт дневного слоя 2.
- `journal.jsonl`, `reports/`, `_не_разобрано/` — рантайм (в `.gitignore`).

## Запуск (слой 1)
```bash
cd C:/Users/User/.claude/file-organizer

python file_router.py --dry-run         # показать раскладку, ничего не двигать
python file_router.py --matched-only     # двигать только сматченные, остальное оставить
python file_router.py --only renewals    # двигать только одно правило (приоритет по полному манифесту)
python file_router.py                     # полный прогон: сматченные → папки, прочее → _не_разобрано
python file_router.py --undo              # откатить последний прогон
python file_router.py --undo-since 2026-06-18  # откатить всё с даты
```

## Фазы
- **Обучение (сейчас):** Task Scheduler не включён. Гоняем вручную (`--dry-run`, `--matched-only`, `--only`), дотюниваем `projects.yaml` на реальных файлах. Неразобранное остаётся в источниках.
- **Авто (позже):** Task Scheduler — слой 1 каждые 15 мин, слой 2 раз в день. Несматченное уходит в `_не_разобрано/`, слой 2 разбирает и дописывает правила. См. Task 9 в плане.

## Гарантии
- Только перемещение, без удаления и перезаписи (коллизия → суффикс ` (2)`).
- Не трогает `.md`, `~$`-lock-файлы Excel, `README/CLAUDE.md/settings/.mcp`, свежие (<2 мин) и занятые файлы.
- Каждое перемещение — строка в `journal.jsonl`; откат через `--undo`.

## Тесты
```bash
cd C:/Users/User/.claude/file-organizer && python -m pytest -q
```
