# YouTrack MCP Server — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** MCP-сервер на Python/FastMCP для полноценной работы с YouTrack (проект DataInsights) — issues, comments, agile, time tracking, attachments.

**Architecture:** Монолитный сервер из двух файлов: `client.py` (async YouTrack REST API клиент на httpx) и `server.py` (FastMCP с ~22 инструментами в 5 группах). Транспорт: stdio по умолчанию, HTTP через флаг.

**Tech Stack:** Python 3.11+, FastMCP (mcp[cli]), httpx, Pydantic

**Spec:** `docs/superpowers/specs/2026-04-13-youtrack-mcp-design.md`

---

### Task 1: Project scaffolding and API client

**Files:**
- Create: `youtrack-mcp/requirements.txt`
- Create: `youtrack-mcp/client.py`
- Create: `youtrack-mcp/server.py` (minimal shell)

- [ ] **Step 1: Create project directory and requirements.txt**

```bash
mkdir -p youtrack-mcp
```

`youtrack-mcp/requirements.txt`:
```
mcp[cli]>=1.0.0
httpx>=0.27.0
```

- [ ] **Step 2: Install dependencies**

```bash
cd youtrack-mcp && pip install -r requirements.txt
```

- [ ] **Step 3: Write the API client**

`youtrack-mcp/client.py`:
```python
import os
import httpx

YOUTRACK_URL = os.environ.get("YOUTRACK_URL", "https://youtrack.moedelo.org/youtrack")
YOUTRACK_TOKEN = os.environ.get("YOUTRACK_TOKEN", "")
PROJECT_ID = "DataInsights"

ISSUE_FIELDS = (
    "id,idReadable,summary,description,created,updated,resolved,"
    "customFields(name,value(name,login,text,minutes))"
)
COMMENT_FIELDS = "id,text,author(login,name),created,updated"
SPRINT_FIELDS = "id,name,goal,start,finish,archived"
AGILE_FIELDS = "id,name,projects(id,shortName)"
WORK_ITEM_FIELDS = "id,date,duration(minutes),author(login,name),text,type(name)"
ATTACHMENT_FIELDS = "id,name,size,mimeType,url,created,author(login,name)"


class YouTrackClient:
    def __init__(self):
        if not YOUTRACK_TOKEN:
            raise ValueError("YOUTRACK_TOKEN environment variable is required")
        self._base = f"{YOUTRACK_URL}/api"
        self._headers = {
            "Authorization": f"Bearer {YOUTRACK_TOKEN}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def get(self, path, params=None):
        async with httpx.AsyncClient(timeout=30.0) as c:
            r = await c.get(f"{self._base}/{path}", headers=self._headers, params=params or {})
            r.raise_for_status()
            return r.json()

    async def post(self, path, json=None):
        async with httpx.AsyncClient(timeout=30.0) as c:
            r = await c.post(f"{self._base}/{path}", headers=self._headers, json=json)
            r.raise_for_status()
            return r.json() if r.status_code == 200 and r.content else None

    async def delete(self, path):
        async with httpx.AsyncClient(timeout=30.0) as c:
            r = await c.delete(f"{self._base}/{path}", headers=self._headers)
            r.raise_for_status()
            return True

    async def upload(self, path, file_path):
        import mimetypes
        mime = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        filename = os.path.basename(file_path)
        async with httpx.AsyncClient(timeout=60.0) as c:
            with open(file_path, "rb") as f:
                r = await c.post(
                    f"{self._base}/{path}",
                    headers={"Authorization": f"Bearer {YOUTRACK_TOKEN}"},
                    files={"file": (filename, f, mime)},
                )
            r.raise_for_status()
            return r.json() if r.content else None

    async def download(self, url, save_to):
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as c:
            r = await c.get(url, headers={"Authorization": f"Bearer {YOUTRACK_TOKEN}"})
            r.raise_for_status()
            with open(save_to, "wb") as f:
                f.write(r.content)
            return save_to
```

- [ ] **Step 4: Write minimal server shell**

`youtrack-mcp/server.py`:
```python
import sys
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("youtrack_mcp")

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
```

- [ ] **Step 5: Verify server starts and commit**

```bash
cd youtrack-mcp && python -c "import server; print('OK')"
git add youtrack-mcp/ && git commit -m "feat(youtrack-mcp): scaffold project with API client and server shell"
```

---

### Task 2: Issue tools (7 tools)

**Files:**
- Modify: `youtrack-mcp/server.py`

- [ ] **Step 1: Add helper and 7 issue tools**

Add `_format_issue` helper, then tools: `issue_create`, `issue_get`, `issue_update`, `issue_delete`, `issue_search`, `issue_list`, `issue_change_state`.

Each tool uses `YouTrackClient` from `client.py`. Custom fields for DataInsights:
- State field: `"Столбцы для проекта Data&Insights"` (StateIssueCustomField)
- Type: `"Тип задач"` (SingleEnumIssueCustomField)
- Priority: `"Приоритет запроса"` (SingleEnumIssueCustomField)
- Assignee: `"Assignee"` (SingleUserIssueCustomField)

All searches auto-prepend `project: DataInsights`.

- [ ] **Step 2: Commit**

```bash
git add youtrack-mcp/server.py
git commit -m "feat(youtrack-mcp): add 7 issue management tools"
```

---

### Task 3: Comment tools (3 tools)

**Files:**
- Modify: `youtrack-mcp/server.py`

- [ ] **Step 1: Add `comment_add`, `comment_list`, `comment_delete`**

Use endpoints: `POST/GET/DELETE /issues/{id}/comments`

- [ ] **Step 2: Commit**

```bash
git commit -m "feat(youtrack-mcp): add 3 comment tools"
```

---

### Task 4: Agile tools (5 tools)

**Files:**
- Modify: `youtrack-mcp/server.py`

- [ ] **Step 1: Add `agile_list_boards`, `agile_get_board`, `agile_get_sprint`, `agile_list_sprints`, `agile_move_issue`**

Use endpoints: `GET /agiles`, `GET /agiles/{id}`, `GET /agiles/{id}/sprints`. Move via `POST /commands`.

- [ ] **Step 2: Commit**

```bash
git commit -m "feat(youtrack-mcp): add 5 agile tools"
```

---

### Task 5: Report / time tracking tools (4 tools)

**Files:**
- Modify: `youtrack-mcp/server.py`

- [ ] **Step 1: Add `report_time_tracking`, `report_add_work_item`, `report_workload`, `report_issues_by_state`**

Time tracking: `GET/POST /issues/{id}/timeTracking/workItems`. Workload and state reports: aggregate from `GET /issues` queries.

- [ ] **Step 2: Commit**

```bash
git commit -m "feat(youtrack-mcp): add 4 report and time tracking tools"
```

---

### Task 6: Attachment tools (3 tools)

**Files:**
- Modify: `youtrack-mcp/server.py`

- [ ] **Step 1: Add `attachment_list`, `attachment_upload`, `attachment_download`**

Use endpoints: `GET/POST /issues/{id}/attachments`. Download via attachment URL with auth header.

- [ ] **Step 2: Commit**

```bash
git commit -m "feat(youtrack-mcp): add 3 attachment tools"
```

---

### Task 7: Integration and README

**Files:**
- Create: `youtrack-mcp/README.md`
- Modify: `.mcp.json`

- [ ] **Step 1: Write README with setup instructions and tool list**
- [ ] **Step 2: Add MCP config to `.mcp.json`**

```json
{
  "mcpServers": {
    "youtrack": {
      "command": "python",
      "args": ["c:/Users/User/.claude/youtrack-mcp/server.py"],
      "env": { "YOUTRACK_TOKEN": "${YOUTRACK_TOKEN}" }
    }
  }
}
```

- [ ] **Step 3: Smoke test import**

```bash
cd youtrack-mcp && python -c "from server import mcp; print('OK')"
```

- [ ] **Step 4: Commit**

```bash
git commit -m "feat(youtrack-mcp): add README and MCP config"
```
