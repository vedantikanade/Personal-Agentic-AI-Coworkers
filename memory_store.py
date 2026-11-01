"""Tiny JSON-backed memory layer shared by both coworkers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).parent
MEMORY_FILE = BASE_DIR / "memory.json"

def load_memory() -> dict[str, Any]:
    if not MEMORY_FILE.exists():
        return {"article_history": [], "coaching_sessions": [], "reflections": []}
    with open(MEMORY_FILE, encoding="utf-8") as handle:
        return json.load(handle)

def save_memory(memory: dict[str, Any]) -> None:
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as handle:
            json.dump(memory, handle, indent=2)
    except OSError:
        # A read-only folder should not prevent either agent from running.
        return

def record_article_brief(articles: list[dict[str, Any]]) -> None:
    memory = load_memory()
    timestamp = datetime.now(timezone.utc).isoformat()
    for article in articles:
        record = {"timestamp": timestamp, "title": article.get("title"), "url": article.get("url"), "source": article.get("source")}
        if not any(item.get("url") == record["url"] for item in memory["article_history"]):
            memory["article_history"].append(record)
    save_memory(memory)

def record_coaching_session(report: dict[str, Any]) -> None:
    memory = load_memory()
    memory["coaching_sessions"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "score": report.get("overall_score_out_of_5"),
        "strengths": report.get("strengths", []),
        "knowledge_gaps": report.get("knowledge_gaps", []),
    })
    save_memory(memory)
