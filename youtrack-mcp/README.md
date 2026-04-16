# YouTrack MCP Server

MCP-сервер для работы с YouTrack (проект DataInsights). 22 инструмента: задачи, комментарии, agile-доски, time tracking, вложения.

## Установка

```bash
cd youtrack-mcp
pip install -r requirements.txt
```

## Настройка

```bash
export YOUTRACK_TOKEN="your-permanent-token"
```

Токен: YouTrack → Profile → Account Security → New Token.

## Запуск

```bash
# stdio (Claude Code)
python server.py

# HTTP
python server.py --http --port 8080
```

## Подключение к Claude Code

В `.mcp.json`:

```json
{
  "mcpServers": {
    "youtrack": {
      "command": "python",
      "args": ["c:/Users/User/.claude/youtrack-mcp/server.py"],
      "env": {
        "YOUTRACK_TOKEN": "your-token-here"
      }
    }
  }
}
```

## Инструменты (22)

### Issues (7)
| Tool | Описание |
|------|----------|
| `issue_create` | Создать задачу |
| `issue_get` | Получить задачу по ID |
| `issue_update` | Обновить поля задачи |
| `issue_delete` | Удалить задачу |
| `issue_search` | Поиск по query-языку YouTrack |
| `issue_list` | Список задач с фильтрацией |
| `issue_change_state` | Сменить статус |

### Comments (3)
| Tool | Описание |
|------|----------|
| `comment_add` | Добавить комментарий |
| `comment_list` | Список комментариев |
| `comment_delete` | Удалить комментарий |

### Agile (5)
| Tool | Описание |
|------|----------|
| `agile_list_boards` | Список досок |
| `agile_get_board` | Детали доски (колонки, swimlanes) |
| `agile_get_sprint` | Текущий спринт |
| `agile_list_sprints` | Все спринты |
| `agile_move_issue` | Переместить задачу в спринт |

### Reports (4)
| Tool | Описание |
|------|----------|
| `report_time_tracking` | Трекинг времени по задаче |
| `report_add_work_item` | Добавить запись о работе |
| `report_workload` | Нагрузка по исполнителям |
| `report_issues_by_state` | Распределение по статусам |

### Attachments (3)
| Tool | Описание |
|------|----------|
| `attachment_list` | Список вложений |
| `attachment_upload` | Прикрепить файл |
| `attachment_download` | Скачать вложение |

## Кастомные поля DataInsights

| Поле | Тип | Значения |
|------|-----|----------|
| Тип задач | SingleEnum | Data Request, Exploratory Analysis, Dashboard Development, A/B Test, ML Model, Bug |
| Приоритет запроса | SingleEnum | Critical, Major, Normal, Minor |
| Столбцы для проекта Data&Insights | State | Open, In Progress, Done, и т.д. |
| Assignee | SingleUser | login пользователя |
| Заказчик | SingleEnum | — |
