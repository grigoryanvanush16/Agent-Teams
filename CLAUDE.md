# Claude Code — Рабочее пространство Вануш Григорян

## Обо мне

Руководитель аналитики в компании «Моё дело» (SaaS-бухгалтерия). Строю Data Warehouse, автоматизирую аналитику, управляю отчётностью Power BI.

Стек: SQL (T-SQL, PostgreSQL, MySQL), Power BI (DAX, TMDL/PBIP), Python, dbt.

## Предпочтения

- **Автономность**: делай сам максимум, спрашивай только по крупным решениям
- **Текст**: пиши как аналитик, не как AI. Без «Давайте рассмотрим», «Важно отметить», без шаблонных вводных
- **Ошибки**: перед финализацией сверяй с эталоном. Не повторяй одну и ту же ошибку
- **Ответы**: без саммари в конце — я сам вижу результат

## Проекты

### DWH (приоритет)

| Проект | Путь | Описание |
|--------|------|----------|
| **DWH архитектура** | `C:\Users\User\Desktop\МД\2.DWH\` | Roadmap, BRD, инвентаризация |
| **ТЗ для DWH** | `C:\Users\User\Desktop\МД\3.ТЗ_DWH\` | Технические задания DE |
| **DWH Production** | `C:\Users\User\Desktop\МД\4.DWH_Production\` | dbt-проект |

### Code Projects (`C:\Users\User\Projects\`)

| Проект | Описание |
|--------|----------|
| **renewals-powerbi** | Дашборд продлений (PBIP) |
| **youtrack-mcp** | MCP-сервер для YouTrack |
| **yandex-mail-mcp** | MCP-сервер для Яндекс.Почты |
| **telegram-mcp** | MCP-сервер для Telegram (third-party) |
| **mail-digest-bot** | Утренний дайджест писем в ЯМ (08:30 будни) |
| **sales-daily-bot** | Скрины Power BI в ЯМ (09:28 будни) |
| **mikhail-replacement** | Автоматизация задач Михаила (Power BI мониторинг, Excel-отчёты) |
| **mr-rybus-marketing** | Маркетинг кафе Mr.Рыбус (апр-июнь 2026) |
| **vanush-site** | Личный сайт (Next.js) |

Каждый проект содержит свой `CLAUDE.md` с локальным контекстом.

### AI Hub — центральное пространство агентов

Путь: `C:\Users\User\Desktop\МД\0.AI_Hub\`

| Папка | Назначение |
|-------|-----------|
| `context/` | Граф сущностей, процессы, команда |
| `inbox/` | Входящие данные: email, telegram, ya_messenger |
| `knowledge/` | База знаний: analysis, research, decisions |
| `eval/` | Лог сессий, оценки качества |
| `lessons/` | Ошибки и выводы агентов |
| `scripts/` | Детерминистические скрипты (validate_naming, check_tz) |

**Правила:**
- Финальные артефакты (ТЗ, dbt, дашборды) → проектные папки
- Скриншоты → `0.AI_Hub/knowledge/projects/<project>/`, не в корень `.claude/`
- Разбор накопившегося: `python "C:/Users/User/Desktop/МД/0.AI_Hub/scripts/sort_artifacts.py"`

## Инфраструктура — где живёт детально

- **Базы данных (10 источников)** — `.claude/rules/databases.md` (загружается при работе с SQL/Python)
- **DWH naming convention** — `.claude/rules/dwh-naming.md` (загружается при работе с моделями dbt)
- **Power BI conventions** — `.claude/rules/powerbi.md` (загружается при работе с TMDL/PBIP)

Полные доступы (логины+пароли): `C:\Users\User\Downloads\Доступы (1) (1).xlsx`

## Внешние системы

- **YouTrack** — таск-трекер (MCP подключён)
- **Power BI Desktop / Report Server** — дашборды

## Agent Teams

12 агентов в `.claude/agents/`. Можно вызывать напрямую или через Router.

| Доменные | Универсальные |
|----------|--------------|
| `dwh-architect` (Opus) | `router` (Opus) |
| `tz-writer` (Opus) | `deep-research` (Opus) |
| `data-analyst` (Opus) | `doc-analyzer` (Opus) |
| `powerbi-expert` (Opus) | `youtube-analyzer` (Opus) |
| | `parser` (Haiku) |
| | `news-digest` (Haiku) |
| | `report-generator` (Haiku) |
| | `meeting-notes` (Haiku) |

### MCP-зависимости

| MCP | Используется в | Fallback |
|-----|---------------|----------|
| Brave Search | deep-research, news-digest | WebSearch + WebFetch |
| Playwright | parser, powerbi-expert | WebFetch |
| YouTrack / Yandex Mail / Telegram | встроены | — |
| yt-dlp + whisper + ffmpeg | youtube-analyzer | обязательны |

### Runtime структура

```
agent-runtime/
├── shared/        # Промежуточные данные между агентами
├── outputs/       # Финальные результаты
└── state/         # Статус работы
```

Детальные роли агентов: `.claude/agents/`
