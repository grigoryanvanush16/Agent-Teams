#!/usr/bin/env python3
"""Apify YouTube Scraper — собирает данные по ключевым словам."""

import json
import time
import requests
from datetime import datetime

API_KEYS = [
    "APIFY_API_TOKEN_REDACTED",
    "APIFY_API_TOKEN_REDACTED",
    "APIFY_API_TOKEN_REDACTED",
]

ACTOR_ID = "streamers~youtube-scraper"
BASE_URL = f"https://api.apify.com/v2/acts/{ACTOR_ID}/run-sync-get-dataset-items"

EN_KEYWORDS = [
    "AI agents",
    "AI agent framework",
    "autonomous AI agents",
    "Claude agent",
    "GPT agent",
    "AI agent tutorial",
    "build AI agent",
    "AI agent 2026",
]

RU_KEYWORDS = [
    "ИИ агенты",
    "AI агенты",
    "автономные агенты",
]

FIELDS = [
    "title", "url", "id", "viewCount", "likes", "commentsCount",
    "duration", "date", "channelName", "channelUrl",
    "numberOfSubscribers", "text",
]

log_lines = []

def log(msg):
    print(msg)
    log_lines.append(msg)

def run_batch(keywords, batch_name, api_key_idx=0):
    """Run scraper for a batch of keywords."""
    run_input = {
        "searchQueries": keywords,
        "maxResults": 15,
        "maxResultsShorts": 0,
        "maxResultStreams": 0,
    }

    for i in range(api_key_idx, len(API_KEYS)):
        token = API_KEYS[i]
        log(f"[{batch_name}] Попытка с API ключом #{i+1}...")
        try:
            resp = requests.post(
                BASE_URL,
                params={"token": token},
                json=run_input,
                timeout=300,
            )
            if resp.status_code in (200, 201):
                items = resp.json()
                log(f"[{batch_name}] Успех! Получено {len(items)} видео")
                return items
            else:
                log(f"[{batch_name}] Ключ #{i+1} вернул статус {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            log(f"[{batch_name}] Ключ #{i+1} ошибка: {e}")

    log(f"[{batch_name}] ВСЕ КЛЮЧИ ИСЧЕРПАНЫ")
    return []

def extract_fields(item):
    """Extract needed fields from raw item."""
    return {
        "title": item.get("title", ""),
        "url": item.get("url", ""),
        "video_id": item.get("id", ""),
        "viewCount": item.get("viewCount", 0),
        "likes": item.get("likes", 0),
        "commentsCount": item.get("commentsCount", 0),
        "duration": item.get("duration", ""),
        "date": item.get("date", ""),
        "channelName": item.get("channelName", ""),
        "channelUrl": item.get("channelUrl", ""),
        "numberOfSubscribers": item.get("numberOfSubscribers", 0),
        "text": item.get("text", ""),
    }

def main():
    log(f"=== Apify YouTube Scraper ===")
    log(f"Время запуска: {datetime.now().isoformat()}")
    log(f"EN ключевых слов: {len(EN_KEYWORDS)}")
    log(f"RU ключевых слов: {len(RU_KEYWORDS)}")
    log("")

    all_videos = []

    # EN batch
    log("--- Batch EN ---")
    en_items = run_batch(EN_KEYWORDS, "EN")
    all_videos.extend(en_items)
    log("")

    # RU batch
    log("--- Batch RU ---")
    ru_items = run_batch(RU_KEYWORDS, "RU")
    all_videos.extend(ru_items)
    log("")

    # Extract fields
    processed = [extract_fields(v) for v in all_videos]

    # Deduplicate by video_id
    seen = set()
    unique = []
    for v in processed:
        vid = v.get("video_id", "")
        if vid and vid not in seen:
            seen.add(vid)
            unique.append(v)
        elif not vid:
            unique.append(v)

    log(f"Всего собрано: {len(processed)} видео")
    log(f"После дедупликации: {len(unique)} уникальных видео")
    log(f"Дубликатов удалено: {len(processed) - len(unique)}")

    # Save raw-data.json
    output_path = "/Users/macbook/Documents/VScode/EDU/Agent Teams/agent-runtime/shared/raw-data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    log(f"\nДанные сохранены в {output_path}")

    # Save scraper-log.md
    log_path = "/Users/macbook/Documents/VScode/EDU/Agent Teams/agent-runtime/shared/scraper-log.md"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("# Scraper Log\n\n")
        f.write(f"**Дата:** {datetime.now().isoformat()}\n\n")
        f.write(f"**EN keywords:** {len(EN_KEYWORDS)}\n")
        f.write(f"**RU keywords:** {len(RU_KEYWORDS)}\n\n")
        f.write(f"**EN видео найдено:** {len(en_items)}\n")
        f.write(f"**RU видео найдено:** {len(ru_items)}\n")
        f.write(f"**Всего после дедупликации:** {len(unique)}\n\n")
        f.write("## Лог выполнения\n\n```\n")
        f.write("\n".join(log_lines))
        f.write("\n```\n")
    log(f"Лог сохранён в {log_path}")

if __name__ == "__main__":
    main()
