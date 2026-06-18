import re
from pathlib import Path

import yaml


def load_manifest(path):
    """Читает projects.yaml -> список проектов. Нет файла -> []."""
    p = Path(path)
    if not p.exists():
        return []
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def match_file(filename, manifest):
    """Имя файла -> словарь проекта или None.

    Регистронезависимый regex-поиск по keywords. Первый проект
    в порядке манифеста, у которого совпал хоть один keyword, выигрывает.
    """
    for project in manifest:
        for keyword in project.get("keywords", []):
            if re.search(keyword, filename, re.IGNORECASE):
                return project
    return None
