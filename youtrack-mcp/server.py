import os
import sys
from mcp.server.fastmcp import FastMCP
from client import (
    YouTrackClient,
    ISSUE_FIELDS,
    PROJECT_ID,
    YOUTRACK_URL,
    COMMENT_FIELDS,
    SPRINT_FIELDS,
    AGILE_FIELDS,
    WORK_ITEM_FIELDS,
    ATTACHMENT_FIELDS,
)

mcp = FastMCP("youtrack_mcp")
client = YouTrackClient()


def _format_issue(issue: dict) -> str:
    """Форматирует словарь задачи в читаемую строку."""
    lines = []
    lines.append(f"ID: {issue.get('idReadable', issue.get('id', '?'))}")
    lines.append(f"Тема: {issue.get('summary', '')}")

    desc = issue.get("description", "")
    if desc:
        lines.append(f"Описание: {desc[:300]}{'...' if len(desc) > 300 else ''}")

    # Разобрать кастомные поля
    custom_fields = issue.get("customFields", [])
    for field in custom_fields:
        name = field.get("name", "")
        value = field.get("value")
        if value is None:
            continue
        if isinstance(value, dict):
            display = value.get("name") or value.get("login") or value.get("text") or ""
        elif isinstance(value, list):
            display = ", ".join(
                v.get("name", "") if isinstance(v, dict) else str(v) for v in value
            )
        else:
            display = str(value)
        if display:
            lines.append(f"{name}: {display}")

    created = issue.get("created")
    if created:
        lines.append(f"Создана: {created}")
    updated = issue.get("updated")
    if updated:
        lines.append(f"Обновлена: {updated}")

    return "\n".join(lines)


@mcp.tool()
async def issue_create(
    summary: str,
    description: str = "",
    type: str = "Data Request",
    priority: str = "Normal",
    assignee: str = "",
) -> str:
    """Создаёт новую задачу в проекте DataInsights.

    Параметры:
    - summary: краткое название задачи (обязательно)
    - description: подробное описание задачи
    - type: тип задачи, например "Data Request", "Bug", "Feature" (по умолчанию "Data Request")
    - priority: приоритет, например "Normal", "High", "Critical" (по умолчанию "Normal")
    - assignee: логин исполнителя (опционально)
    """
    custom_fields = [
        {
            "name": "Тип задач",
            "$type": "SingleEnumIssueCustomField",
            "value": {"name": type},
        },
        {
            "name": "Приоритет запроса",
            "$type": "SingleEnumIssueCustomField",
            "value": {"name": priority},
        },
    ]
    if assignee:
        custom_fields.append(
            {
                "name": "Assignee",
                "$type": "SingleUserIssueCustomField",
                "value": {"login": assignee},
            }
        )

    body = {
        "project": {"id": PROJECT_ID},
        "summary": summary,
        "description": description,
        "customFields": custom_fields,
    }
    result = await client.post(f"issues?fields={ISSUE_FIELDS}", json=body)
    return _format_issue(result)


@mcp.tool()
async def issue_get(issue_id: str) -> str:
    """Возвращает полную информацию о задаче по её ID.

    Параметры:
    - issue_id: идентификатор задачи, например "DataInsights-42"
    """
    result = await client.get(f"issues/{issue_id}", params={"fields": ISSUE_FIELDS})
    return _format_issue(result)


@mcp.tool()
async def issue_update(
    issue_id: str,
    summary: str = "",
    description: str = "",
    type: str = "",
    priority: str = "",
    assignee: str = "",
) -> str:
    """Обновляет поля существующей задачи. Передавай только те поля, которые нужно изменить.

    Параметры:
    - issue_id: идентификатор задачи, например "DataInsights-42"
    - summary: новое название задачи (оставь пустым, чтобы не менять)
    - description: новое описание (оставь пустым, чтобы не менять)
    - type: новый тип задачи (оставь пустым, чтобы не менять)
    - priority: новый приоритет (оставь пустым, чтобы не менять)
    - assignee: логин нового исполнителя (оставь пустым, чтобы не менять)
    """
    body: dict = {}
    if summary:
        body["summary"] = summary
    if description:
        body["description"] = description

    custom_fields = []
    if type:
        custom_fields.append(
            {
                "name": "Тип задач",
                "$type": "SingleEnumIssueCustomField",
                "value": {"name": type},
            }
        )
    if priority:
        custom_fields.append(
            {
                "name": "Приоритет запроса",
                "$type": "SingleEnumIssueCustomField",
                "value": {"name": priority},
            }
        )
    if assignee:
        custom_fields.append(
            {
                "name": "Assignee",
                "$type": "SingleUserIssueCustomField",
                "value": {"login": assignee},
            }
        )
    if custom_fields:
        body["customFields"] = custom_fields

    await client.post(f"issues/{issue_id}?fields={ISSUE_FIELDS}", json=body)
    result = await client.get(f"issues/{issue_id}", params={"fields": ISSUE_FIELDS})
    return _format_issue(result)


@mcp.tool()
async def issue_delete(issue_id: str) -> str:
    """Удаляет задачу безвозвратно.

    Параметры:
    - issue_id: идентификатор задачи, например "DataInsights-42"
    """
    await client.delete(f"issues/{issue_id}")
    return f"Задача {issue_id} успешно удалена."


@mcp.tool()
async def issue_search(query: str, top: int = 20) -> str:
    """Ищет задачи в проекте DataInsights по произвольному запросу YouTrack.

    Параметры:
    - query: строка поиска в синтаксисе YouTrack, например "Assignee: me State: Open"
    - top: максимальное количество результатов (по умолчанию 20)
    """
    full_query = f"project: {PROJECT_ID} {query}".strip()
    results = await client.get(
        "issues",
        params={"query": full_query, "fields": ISSUE_FIELDS, "$top": top},
    )
    if not results:
        return "Задачи не найдены."
    return "\n---\n".join(_format_issue(issue) for issue in results)


@mcp.tool()
async def issue_list(
    state: str = "",
    assignee: str = "",
    type: str = "",
    top: int = 20,
) -> str:
    """Возвращает список задач проекта DataInsights с фильтрацией по статусу, исполнителю и типу.

    Параметры:
    - state: статус задачи, например "Open", "In Progress", "Done" (оставь пустым для всех)
    - assignee: логин исполнителя (оставь пустым для всех)
    - type: тип задачи, например "Data Request" (оставь пустым для всех)
    - top: максимальное количество результатов (по умолчанию 20)
    """
    parts = [f"project: {PROJECT_ID}"]
    if state:
        parts.append(f"State: {{{state}}}")
    if assignee:
        parts.append(f"Assignee: {assignee}")
    if type:
        parts.append(f"Тип задач: {{{type}}}")

    full_query = " ".join(parts)
    results = await client.get(
        "issues",
        params={"query": full_query, "fields": ISSUE_FIELDS, "$top": top},
    )
    if not results:
        return "Задачи не найдены."
    return "\n---\n".join(_format_issue(issue) for issue in results)


@mcp.tool()
async def issue_change_state(issue_id: str, state: str) -> str:
    """Изменяет статус (колонку) задачи в проекте DataInsights.

    Параметры:
    - issue_id: идентификатор задачи, например "DataInsights-42"
    - state: новый статус, например "Open", "In Progress", "Done", "Cancelled"
    """
    body = {
        "customFields": [
            {
                "name": "Столбцы для проекта Data&Insights",
                "$type": "StateIssueCustomField",
                "value": {"name": state},
            }
        ]
    }
    await client.post(f"issues/{issue_id}?fields={ISSUE_FIELDS}", json=body)
    result = await client.get(f"issues/{issue_id}", params={"fields": ISSUE_FIELDS})
    return _format_issue(result)


# ── Comment tools ────────────────────────────────────────────────────────────


@mcp.tool(name="comment_add")
async def comment_add(issue_id: str, text: str) -> str:
    """Добавляет комментарий к задаче.

    Параметры:
    - issue_id: идентификатор задачи, например "DataInsights-42"
    - text: текст комментария
    """
    result = await client.post(
        f"issues/{issue_id}/comments?fields={COMMENT_FIELDS}",
        json={"text": text},
    )
    author = ""
    if result:
        author_obj = result.get("author") or {}
        author = author_obj.get("name") or author_obj.get("login") or ""
    preview = text[:100] + ("..." if len(text) > 100 else "")
    return f"Комментарий добавлен. Автор: {author}. Текст: {preview}"


@mcp.tool(name="comment_list")
async def comment_list(issue_id: str) -> str:
    """Возвращает список всех комментариев к задаче.

    Параметры:
    - issue_id: идентификатор задачи, например "DataInsights-42"
    """
    results = await client.get(
        f"issues/{issue_id}/comments",
        params={"fields": COMMENT_FIELDS},
    )
    if not results:
        return "Комментарии не найдены."
    lines = []
    for c in results:
        author_obj = c.get("author") or {}
        author = author_obj.get("name") or author_obj.get("login") or "?"
        cid = c.get("id", "?")
        text = c.get("text", "")
        lines.append(f"**{author}** ({cid}): {text}")
    return "\n---\n".join(lines)


@mcp.tool(name="comment_delete")
async def comment_delete(issue_id: str, comment_id: str) -> str:
    """Удаляет комментарий к задаче.

    Параметры:
    - issue_id: идентификатор задачи, например "DataInsights-42"
    - comment_id: идентификатор комментария
    """
    await client.delete(f"issues/{issue_id}/comments/{comment_id}")
    return f"Комментарий {comment_id} к задаче {issue_id} успешно удалён."


# ── Agile tools ───────────────────────────────────────────────────────────────


@mcp.tool(name="agile_list_boards")
async def agile_list_boards() -> str:
    """Возвращает список всех agile-досок в YouTrack."""
    results = await client.get(
        "agiles",
        params={"fields": AGILE_FIELDS, "$top": 50},
    )
    if not results:
        return "Доски не найдены."
    lines = []
    for board in results:
        name = board.get("name", "?")
        bid = board.get("id", "?")
        projects = board.get("projects") or []
        proj_names = ", ".join(p.get("shortName", "") for p in projects) or "—"
        lines.append(f"**{name}** (id: {bid}) — projects: {proj_names}")
    return "\n".join(lines)


@mcp.tool(name="agile_get_board")
async def agile_get_board(board_id: str) -> str:
    """Возвращает детальную информацию об agile-доске: колонки и swim-lanes.

    Параметры:
    - board_id: идентификатор доски
    """
    fields = (
        "id,name,projects(id,shortName),"
        "columnSettings(columns(presentation)),"
        "swimlaneSettings(values(name))"
    )
    board = await client.get(f"agiles/{board_id}", params={"fields": fields})
    name = board.get("name", "?")
    bid = board.get("id", "?")

    projects = board.get("projects") or []
    proj_str = ", ".join(p.get("shortName", "") for p in projects) or "—"

    col_settings = board.get("columnSettings") or {}
    columns = col_settings.get("columns") or []
    col_str = " → ".join(c.get("presentation", "") for c in columns) or "—"

    swim_settings = board.get("swimlaneSettings") or {}
    swim_values = swim_settings.get("values") or []
    swim_str = "\n  - ".join(v.get("name", "") for v in swim_values) or "—"

    lines = [
        f"**{name}** (id: {bid})",
        f"Проекты: {proj_str}",
        f"Колонки: {col_str}",
        f"Swimlanes:\n  - {swim_str}" if swim_values else "Swimlanes: —",
    ]
    return "\n".join(lines)


@mcp.tool(name="agile_get_sprint")
async def agile_get_sprint(board_id: str) -> str:
    """Возвращает последний активный (неархивный) спринт доски.

    Параметры:
    - board_id: идентификатор доски
    """
    results = await client.get(
        f"agiles/{board_id}/sprints",
        params={"fields": SPRINT_FIELDS, "$top": 50},
    )
    if not results:
        return "Спринты не найдены."
    active = [s for s in results if not s.get("archived")]
    sprint = active[-1] if active else results[-1]

    name = sprint.get("name", "?")
    sid = sprint.get("id", "?")
    goal = sprint.get("goal") or "—"
    start = sprint.get("start") or "—"
    finish = sprint.get("finish") or "—"
    archived = sprint.get("archived", False)

    lines = [
        f"**{name}** (id: {sid})",
        f"Цель: {goal}",
        f"Начало: {start}",
        f"Конец: {finish}",
        f"Архивный: {'да' if archived else 'нет'}",
    ]
    return "\n".join(lines)


@mcp.tool(name="agile_list_sprints")
async def agile_list_sprints(board_id: str) -> str:
    """Возвращает все спринты доски.

    Параметры:
    - board_id: идентификатор доски
    """
    results = await client.get(
        f"agiles/{board_id}/sprints",
        params={"fields": SPRINT_FIELDS, "$top": 100},
    )
    if not results:
        return "Спринты не найдены."
    lines = []
    for s in results:
        name = s.get("name", "?")
        sid = s.get("id", "?")
        archived = "архивный" if s.get("archived") else "активный"
        start = s.get("start") or "—"
        finish = s.get("finish") or "—"
        lines.append(f"**{name}** (id: {sid}) [{archived}] {start} – {finish}")
    return "\n".join(lines)


@mcp.tool(name="agile_move_issue")
async def agile_move_issue(board_id: str, sprint_id: str, issue_id: str) -> str:
    """Перемещает задачу в указанный спринт доски.

    Параметры:
    - board_id: идентификатор доски
    - sprint_id: идентификатор спринта
    - issue_id: идентификатор задачи, например "DataInsights-42"
    """
    body = {
        "issues": [{"idReadable": issue_id}],
        "query": f"Board {board_id}: {{Sprint {sprint_id}}}",
    }
    await client.post("commands", json=body)
    return f"Задача {issue_id} перемещена в спринт {sprint_id} доски {board_id}."


# ── Report / time-tracking tools ──────────────────────────────────────────────


@mcp.tool(name="report_time_tracking")
async def report_time_tracking(issue_id: str) -> str:
    """Возвращает список трудозатрат (work items) по задаче и суммарное время.

    Параметры:
    - issue_id: идентификатор задачи, например "DataInsights-42"
    """
    results = await client.get(
        f"issues/{issue_id}/timeTracking/workItems",
        params={"fields": WORK_ITEM_FIELDS, "$top": 100},
    )
    if not results:
        return "Трудозатраты не найдены."
    lines = []
    total = 0
    for item in results:
        author_obj = item.get("author") or {}
        author = author_obj.get("name") or author_obj.get("login") or "?"
        duration = item.get("duration") or {}
        minutes = duration.get("minutes", 0)
        total += minutes
        type_obj = item.get("type") or {}
        wtype = type_obj.get("name") or "—"
        text = item.get("text") or "—"
        lines.append(f"{author} | {minutes} мин | {wtype} | {text}")
    lines.append(f"\nИтого: {total} мин ({total // 60} ч {total % 60} мин)")
    return "\n".join(lines)


@mcp.tool(name="report_add_work_item")
async def report_add_work_item(
    issue_id: str,
    duration_minutes: int,
    text: str = "",
    work_type: str = "Development",
) -> str:
    """Добавляет трудозатраты (work item) к задаче.

    Параметры:
    - issue_id: идентификатор задачи, например "DataInsights-42"
    - duration_minutes: количество минут
    - text: описание работы (опционально)
    - work_type: тип работы, например "Development", "Testing" (по умолчанию "Development")
    """
    body = {
        "duration": {"minutes": duration_minutes},
        "text": text,
        "type": {"name": work_type},
    }
    result = await client.post(
        f"issues/{issue_id}/timeTracking/workItems?fields={WORK_ITEM_FIELDS}",
        json=body,
    )
    wid = result.get("id", "?") if result else "?"
    return (
        f"Трудозатраты добавлены к задаче {issue_id}: "
        f"{duration_minutes} мин, тип «{work_type}». ID записи: {wid}."
    )


@mcp.tool(name="report_workload")
async def report_workload(top: int = 50) -> str:
    """Показывает нагрузку по исполнителям: количество незакрытых задач на каждого.

    Параметры:
    - top: максимальное количество задач для анализа (по умолчанию 50)
    """
    fields = (
        "id,idReadable,customFields(name,value(name,login,text))"
    )
    results = await client.get(
        "issues",
        params={
            "query": "project: DataInsights State: -Resolved,-Done,-Closed",
            "fields": fields,
            "$top": top,
        },
    )
    if not results:
        return "Задачи не найдены."
    counts: dict[str, int] = {}
    for issue in results:
        assignee = "Не назначен"
        for cf in issue.get("customFields") or []:
            if cf.get("name") == "Assignee":
                val = cf.get("value")
                if isinstance(val, dict):
                    assignee = val.get("name") or val.get("login") or "Не назначен"
                break
        counts[assignee] = counts.get(assignee, 0) + 1
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    lines = ["**Нагрузка по исполнителям:**"]
    for name, count in sorted_counts:
        bar = "█" * count
        lines.append(f"{name}: {count} задач {bar}")
    return "\n".join(lines)


@mcp.tool(name="report_issues_by_state")
async def report_issues_by_state() -> str:
    """Показывает распределение задач проекта DataInsights по статусам."""
    fields = "id,customFields(name,value(name))"
    results = await client.get(
        "issues",
        params={
            "query": "project: DataInsights",
            "fields": fields,
            "$top": 200,
        },
    )
    if not results:
        return "Задачи не найдены."
    counts: dict[str, int] = {}
    for issue in results:
        state = "Без статуса"
        for cf in issue.get("customFields") or []:
            if cf.get("name") == "Столбцы для проекта Data&Insights":
                val = cf.get("value")
                if isinstance(val, dict):
                    state = val.get("name") or "Без статуса"
                break
        counts[state] = counts.get(state, 0) + 1
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    lines = ["**Задачи по статусам:**"]
    for state, count in sorted_counts:
        bar = "█" * min(count, 40)
        lines.append(f"{state}: {count} {bar}")
    return "\n".join(lines)


# ── Attachment tools ──────────────────────────────────────────────────────────


@mcp.tool(name="attachment_list")
async def attachment_list(issue_id: str) -> str:
    """Возвращает список вложений к задаче.

    Параметры:
    - issue_id: идентификатор задачи, например "DataInsights-42"
    """
    results = await client.get(
        f"issues/{issue_id}/attachments",
        params={"fields": ATTACHMENT_FIELDS},
    )
    if not results:
        return "Вложения не найдены."
    lines = []
    for att in results:
        name = att.get("name", "?")
        size_bytes = att.get("size") or 0
        size_kb = round(size_bytes / 1024, 1)
        mime = att.get("mimeType") or "—"
        author_obj = att.get("author") or {}
        author = author_obj.get("name") or author_obj.get("login") or "?"
        aid = att.get("id", "?")
        lines.append(f"{name} (id: {aid}) | {size_kb} KB | {mime} | {author}")
    return "\n".join(lines)


@mcp.tool(name="attachment_upload")
async def attachment_upload(issue_id: str, file_path: str) -> str:
    """Загружает файл как вложение к задаче.

    Параметры:
    - issue_id: идентификатор задачи, например "DataInsights-42"
    - file_path: абсолютный путь к файлу на диске
    """
    if not os.path.exists(file_path):
        return f"Файл не найден: {file_path}"
    filename = os.path.basename(file_path)
    await client.upload(f"issues/{issue_id}/attachments", file_path)
    return f"Файл «{filename}» успешно загружен как вложение к задаче {issue_id}."


@mcp.tool(name="attachment_download")
async def attachment_download(issue_id: str, attachment_id: str, save_to: str) -> str:
    """Скачивает вложение задачи на диск.

    Параметры:
    - issue_id: идентификатор задачи, например "DataInsights-42"
    - attachment_id: идентификатор вложения
    - save_to: путь для сохранения файла (директория или полный путь)
    """
    results = await client.get(
        f"issues/{issue_id}/attachments",
        params={"fields": ATTACHMENT_FIELDS},
    )
    att = next((a for a in (results or []) if a.get("id") == attachment_id), None)
    if att is None:
        return f"Вложение {attachment_id} не найдено у задачи {issue_id}."

    filename = att.get("name", attachment_id)
    url = att.get("url", "")
    if url and not url.startswith("http"):
        url = f"{YOUTRACK_URL}{url}"

    dest = save_to
    if os.path.isdir(save_to):
        dest = os.path.join(save_to, filename)

    await client.download(url, dest)
    return f"Файл «{filename}» сохранён: {dest}"


if __name__ == "__main__":
    transport = "http" if "--http" in sys.argv else "stdio"
    port = 8080
    for i, arg in enumerate(sys.argv):
        if arg == "--port" and i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])
    if transport == "http":
        mcp.run(transport="http", host="0.0.0.0", port=port)
    else:
        mcp.run()
