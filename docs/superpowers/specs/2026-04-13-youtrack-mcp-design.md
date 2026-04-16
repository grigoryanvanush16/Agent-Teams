# YouTrack MCP Server — Design Spec

**Date:** 2026-04-13
**Status:** Approved

## Overview

MCP-сервер для работы с YouTrack (проект DataInsights) через Claude Code. Python + FastMCP, монолитная архитектура. Поддержка stdio и HTTP транспортов.

## Requirements

- Полное управление задачами (CRUD, смена статуса, поиск)
- Комментарии и вложения
- Agile-доски и спринты
- Отчёты: time tracking, workload, распределение по статусам
- Аутентификация через permanent token
- Транспорт: stdio (разработка) + HTTP (продакшен)
- Scope: проект DataInsights (hardcoded)

## Architecture

### Project Structure

```
youtrack-mcp/
├── server.py          # FastMCP сервер + все инструменты (~22 tools)
├── client.py          # YouTrack REST API клиент (httpx async)
├── requirements.txt   # fastmcp, httpx
└── README.md          # Настройка и подключение
```

### YouTrack API Client (`client.py`)

Async-класс на `httpx.AsyncClient`:

- **Base URL:** `https://youtrack.moedelo.org/youtrack/api`
- **Auth:** `Bearer {YOUTRACK_TOKEN}` из env
- **Methods:** `get()`, `post()`, `delete()` — обёртки с обработкой ошибок и пагинацией
- **Project:** `DataInsights` (hardcoded default)
- **Fields parameter:** YouTrack API требует явного указания возвращаемых полей через `fields` query param — клиент определяет разумные defaults для каждого типа сущности

### Tools (`server.py`) — 5 groups, 22 tools

#### Issues (7)

| Tool | Description | YouTrack API |
|------|-------------|--------------|
| `issue_create` | Создать задачу (summary, description, type, priority, assignee) | `POST /issues` |
| `issue_get` | Получить задачу по ID | `GET /issues/{id}` |
| `issue_update` | Обновить поля задачи | `POST /issues/{id}` |
| `issue_delete` | Удалить задачу | `DELETE /issues/{id}` |
| `issue_search` | Поиск по query-языку YouTrack | `GET /issues?query=` |
| `issue_list` | Список задач проекта с фильтрацией | `GET /issues?query=project:DataInsights` |
| `issue_change_state` | Сменить статус задачи | `POST /issues/{id}` (update State field) |

#### Comments (3)

| Tool | Description | YouTrack API |
|------|-------------|--------------|
| `comment_add` | Добавить комментарий к задаче | `POST /issues/{id}/comments` |
| `comment_list` | Список комментариев задачи | `GET /issues/{id}/comments` |
| `comment_delete` | Удалить комментарий | `DELETE /issues/{id}/comments/{commentId}` |

#### Agile (5)

| Tool | Description | YouTrack API |
|------|-------------|--------------|
| `agile_list_boards` | Список agile-досок | `GET /agiles` |
| `agile_get_board` | Получить доску с swimlanes | `GET /agiles/{id}` |
| `agile_get_sprint` | Текущий спринт доски | `GET /agiles/{id}/sprints?query=current` |
| `agile_list_sprints` | Все спринты доски | `GET /agiles/{id}/sprints` |
| `agile_move_issue` | Переместить задачу в спринт | `POST /issues/{id}` (update sprint) |

#### Reports (4)

| Tool | Description | YouTrack API |
|------|-------------|--------------|
| `report_time_tracking` | Трекинг времени по задаче | `GET /issues/{id}/timeTracking/workItems` |
| `report_add_work_item` | Добавить запись о работе | `POST /issues/{id}/timeTracking/workItems` |
| `report_workload` | Нагрузка по исполнителям (агрегация) | `GET /issues?query=...` + агрегация |
| `report_issues_by_state` | Распределение задач по статусам | `GET /issues?query=...` + группировка |

#### Attachments (3)

| Tool | Description | YouTrack API |
|------|-------------|--------------|
| `attachment_upload` | Прикрепить файл к задаче | `POST /issues/{id}/attachments` |
| `attachment_list` | Список вложений задачи | `GET /issues/{id}/attachments` |
| `attachment_download` | Скачать вложение | `GET /issues/{id}/attachments/{attachId}/content` |

### Transport

FastMCP поддерживает оба транспорта из коробки:

- **stdio:** `python server.py` (default) — для Claude Code subprocess
- **HTTP:** `python server.py --http --port 8080` — для удалённого доступа

### Configuration

Env-переменные:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `YOUTRACK_TOKEN` | Yes | — | Permanent token из профиля YouTrack |
| `YOUTRACK_URL` | No | `https://youtrack.moedelo.org/youtrack` | Base URL инстанса |

### Custom Fields (DataInsights)

Кастомные поля проекта, которые поддерживаются в `issue_create` и `issue_update`:

- **Приоритет запроса** — приоритет
- **Заказчик** — кто запросил
- **Тип задач** — Data Request, Exploratory Analysis, Dashboard Development, A/B Test, ML Model, Bug

### Error Handling

- HTTP 401 → сообщение о невалидном токене
- HTTP 404 → задача/сущность не найдена
- HTTP 400 → невалидные параметры (вернуть текст ошибки YouTrack)
- Timeout: 30s per request

### Claude Code Integration

Пример `.mcp.json` для подключения:

```json
{
  "mcpServers": {
    "youtrack": {
      "command": "python",
      "args": ["c:/Users/User/.claude/youtrack-mcp/server.py"],
      "env": {
        "YOUTRACK_TOKEN": "${YOUTRACK_TOKEN}"
      }
    }
  }
}
```
