# Pipeline: YouTube Outlier Analysis

## Обзор

5 агентов работают последовательно в tmux. Каждый агент создаёт артефакт и передаёт работу следующему через SendMessage.

## Схема

```
coordinator (lead)
     │
     ▼
 scraper ──→ agent-runtime/shared/raw-data.json
     │        Apify: streamers/youtube-scraper
     │        EN + RU ключевые слова батчами по 10
     │        Fallback: apify/google-search-scraper
     ▼
 analyst ──→ agent-runtime/shared/outliers.json
     │        Фильтрация: AI-релевантность, min views, freshness
     │        Outlier Score = views / channel_avg_views
     │        Категоризация: Claude, GPT, Agents, Coding...
     ▼
 transcript-analyst ──→ agent-runtime/shared/transcript-analysis.json
     │        Supadata API: скачивает субтитры топ-15 outliers
     │        Маркетинговый анализ каждого транскрипта:
     │          • Хук (первые 30 сек)
     │          • Формат контента (туториал, обзор, сравнение)
     │          • Главный тезис + топ-5 ключевых слов
     │          • Целевая аудитория и тон
     │          • Уникальный угол подачи
     │          • Почему стал outlier (гипотеза)
     │          • Реплицируемость: высокая / средняя / низкая
     │          • Actionable takeaways
     ▼
 reporter ──→ Google Sheet + PDF
     │        Sheet 1: EN Outliers (данные)
     │        Sheet 2: RU Outliers (данные)
     │        Sheet 3: Dashboard (bar chart топ-10, pie chart по категориям)
     │        Sheet 4: Маркетинговый анализ транскриптов
     │        + agent-runtime/outputs/report.pdf
     ▼
 coordinator ──→ agent-runtime/outputs/briefing.md
              Финальный брифинг: метрики, тренды,
              инсайты из транскриптов, рекомендации
```

## Агенты

| # | Агент | Файл | Входные данные | Выходные данные |
|---|-------|------|----------------|-----------------|
| 1 | coordinator | `.claude/agents/coordinator.md` | Задание от пользователя | plan.md, status.md, briefing.md |
| 2 | scraper | `.claude/agents/scraper.md` | Ключевые слова, рынки | raw-data.json, scraper-log.md |
| 3 | analyst | `.claude/agents/analyst.md` | raw-data.json | outliers.json, analysis-summary.md |
| 4 | transcript-analyst | `.claude/agents/transcript-analyst.md` | outliers.json | transcript-analysis.json, transcript-summary.md |
| 5 | reporter | `.claude/agents/reporter.md` | outliers.json, transcript-analysis.json | Google Sheet, report.pdf |

## Коммуникация между агентами

Каждый агент по завершении:
1. Сохраняет артефакт в `agent-runtime/shared/` или `agent-runtime/outputs/`
2. Отправляет `SendMessage` следующему агенту с кратким саммари
3. Все handoff видны в tmux split-pane

```
coordinator ──SendMessage──→ scraper
                             "Собери данные по темам: AI coding, Claude Code. Рынки: EN, RU"

scraper     ──SendMessage──→ analyst
                             "Готово: 342 видео в raw-data.json"

analyst     ──SendMessage──→ transcript-analyst
                             "Готово: 47 outliers в outliers.json. Топ: 'Claude Code tutorial' 12.3x"

transcript-analyst ──SendMessage──→ reporter
                             "Готово: 12 транскриптов проанализировано. Главный паттерн: tutorial-формат"

reporter    ──SendMessage──→ coordinator
                             "Готово: Google Sheet [ссылка], PDF создан"
```

## Структура agent-runtime/

```
agent-runtime/
├── shared/                          # Рабочие данные между агентами
│   ├── raw-data.json                # Сырые данные от scraper
│   ├── scraper-log.md               # Лог работы scraper
│   ├── outliers.json                # Отфильтрованные outliers от analyst
│   ├── analysis-summary.md          # Текстовый анализ от analyst
│   ├── transcript-analysis.json     # Маркетинговый анализ от transcript-analyst
│   └── transcript-summary.md        # Текстовый саммари от transcript-analyst
├── state/                           # Состояние pipeline
│   ├── plan.md                      # План работы (от coordinator)
│   └── status.md                    # Текущий статус каждого этапа
├── messages/                        # Handoff-сообщения между агентами
└── outputs/                         # Финальные результаты
    ├── briefing.md                  # Финальный брифинг (от coordinator)
    ├── report.pdf                   # PDF-отчёт (от reporter)
    ├── google-sheet-url.txt         # Ссылка на Google Sheet
    └── reporter-log.md              # Лог reporter
```

## Технические зависимости

| Сервис | Переменная окружения | Назначение |
|--------|---------------------|------------|
| Apify | `APIFY_TOKEN` / `APIFY_API_KEY` | Парсинг YouTube через streamers/youtube-scraper |
| Supadata | `SUPADATA_API_KEY` | Скачивание субтитров YouTube-видео |
| Google Sheets | MCP (подключен) | Создание таблиц с данными и графиками |

## Пороговые значения (analyst)

| Параметр | Значение |
|----------|----------|
| Мин. просмотры | 15,000 |
| Макс. подписчики | 2,000,000 |
| Мин. outlier score | 2.0x |
| Макс. возраст видео | 21 день |
| Макс. транскриптов | 15 (для экономии кредитов Supadata) |

## Запуск

```bash
# 1. Открыть tmux
tmux new -s claude-agent-team

# 2. Запустить Claude Code
claude

# 3. Дать задание
```

```text
Создай Agent Team для анализа YouTube outliers.
Используй роли coordinator, scraper, analyst, transcript-analyst и reporter.
Тема: AI coding tools 2026. Рынки: EN и RU.
```
