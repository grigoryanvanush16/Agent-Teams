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
