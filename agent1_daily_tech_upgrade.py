"""DailyTechUpgradeAgent: a local, deterministic prototype.

The ranking function can later be replaced by an RSS/search connector and the
summary fields can later be generated and verified by an LLM.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from live_retrieval import fetch_live_articles
from memory_store import record_article_brief


BASE_DIR = Path(__file__).parent


def load_json(filename: str) -> Any:
    with open(BASE_DIR / filename, encoding="utf-8") as handle:
        return json.load(handle)


def rank_articles(articles: list[dict[str, Any]], profile: dict[str, Any]) -> list[dict[str, Any]]:
    interests = {item.lower() for item in profile.get("interests", [])}
    growth_areas = {item.lower() for item in profile.get("growth_areas", [])}

    def score(article: dict[str, Any]) -> tuple[int, str]:
        searchable = " ".join([
            article.get("title", ""),
            article.get("description", ""),
            " ".join(article.get("topics", [])),
        ]).lower()
        topics = {
            item for item in interests | growth_areas
            if re.search(r"\b" + re.escape(item) + r"\b", searchable)
        }
        interest_score = len(topics & interests) * 3
        growth_score = len(topics & growth_areas) * 2
        priority_terms = {"healthcare", "data science", "data quality", "machine learning", "rag", "evaluation"}
        priority_score = sum(4 for item in priority_terms if re.search(r"\b" + re.escape(item) + r"\b", searchable))
        return interest_score + growth_score + priority_score, article["date"]

    return sorted(articles, key=score, reverse=True)[:3]


def normalize_live_article(article: dict[str, Any]) -> dict[str, Any]:
    description = article.get("description", "")
    first_sentence = re.split(r"(?<=[.!?])\s+", description.strip())[0] if description else ""
    short_summary = " ".join(re.split(r"(?<=[.!?])\s+", description.strip())[:2])
    if len(short_summary) > 220:
        short_summary = short_summary[:217].rsplit(" ", 1)[0] + "..."
    return {
        **article,
        "summary": description or "Read the linked article and extract its main technical contribution.",
        "short_summary": short_summary or "Read the linked article and identify its method, evidence, and limitation.",
        "why_it_matters": "Connect the article's method to healthcare data quality, model evaluation, or trustworthy AI.",
        "takeaways": [
            first_sentence or "Identify the main technical method or system described.",
            "Check what data, evaluation method, or limitation the author reports.",
            "Connect the idea to healthcare data quality or trustworthy AI.",
        ],
        "minutes": 5,
    }


def build_learning_brief(profile: dict[str, Any], articles: list[dict[str, Any]]) -> str:
    daily_minutes = int(profile.get("daily_minutes", 15))
    # A realistic 15-minute session uses one article as the deep dive and
    # two as short scans. The user still receives all three recommendations.
    deep_dive_minutes = max(6, round(daily_minutes * 0.5))
    scan_minutes = max(2, round(daily_minutes * 0.2))
    reflection_minutes = max(1, daily_minutes - deep_dive_minutes - (scan_minutes * 2))
    lines = [
        f"{daily_minutes}-minute technical learning brief for {profile.get('career_goal', 'your career goal')}",
        "Focus: healthcare AI, data quality, RAG, and trustworthy evaluation.",
        f"Plan: 1 deep dive ({deep_dive_minutes} min) + 2 quick scans ({scan_minutes} min each) + {reflection_minutes} min reflection.",
        "",
    ]
    for index, article in enumerate(articles, start=1):
        role = "DEEP DIVE" if index == 1 else "QUICK SCAN"
        allotted = deep_dive_minutes if index == 1 else scan_minutes
        summary = article.get("short_summary") or article.get("summary", "")
        if not article.get("short_summary") and len(summary) > 220:
            summary = summary[:217].rsplit(" ", 1)[0] + "..."
        lines.extend([
            f"{index}. {role} — {article['title']}",
            f"   {article['source']} | {article['date']} | {allotted} min",
            f"   {article['url']}",
            f"   Summary: {summary}",
            f"   Why it matters: {article.get('why_it_matters', 'Connect this idea to healthcare data quality and trustworthy AI.')}",
            f"   Takeaway: {article['takeaways'][0]}",
            "",
        ])
    lines.append("Career connection: These readings build the ability to evaluate healthcare data and trustworthy AI systems.")
    lines.append(f"Reflection ({reflection_minutes} min): What data-quality risk could affect the main technique? Write one sentence and one mitigation.")
    return "\n".join(lines)


def generate_daily_brief() -> str:
    profile = load_json("user_profile.json")
    live_articles = [normalize_live_article(item) for item in fetch_live_articles()]
    fallback_articles = load_json("articles.json")
    seen_urls: set[str] = set()
    candidates = []
    for item in live_articles + fallback_articles:
        if item.get("url") not in seen_urls:
            candidates.append(item)
            seen_urls.add(item.get("url", ""))
    articles = rank_articles(candidates, profile)
    if len(articles) < 3:
        selected_urls = {item.get("url") for item in articles}
        articles.extend(item for item in fallback_articles if item.get("url") not in selected_urls)
        articles = articles[:3]
    record_article_brief(articles)
    return build_learning_brief(profile, articles)


if __name__ == "__main__":
    print(generate_daily_brief())
