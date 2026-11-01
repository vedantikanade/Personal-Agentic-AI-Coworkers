"""Small standard-library retrieval layer for live technical and career data."""

from __future__ import annotations

import html
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from typing import Any


HEADERS = {"User-Agent": "SJSU-Agentic-AI-Coworker/1.0"}

RSS_FEEDS = {
    "OpenAI": "https://openai.com/blog/rss.xml",
    "Anthropic": "https://www.anthropic.com/rss.xml",
    "Google AI": "https://blog.research.google/feeds/posts/default/-/Machine%20Learning?alt=rss",
    "AWS Machine Learning": "https://aws.amazon.com/blogs/machine-learning/feed/",
    "Microsoft Research": "https://www.microsoft.com/en-us/research/feed/",
}


def fetch_text(url: str, timeout: int = 5) -> str:
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def clean_text(value: str) -> str:
    value = html.unescape(re.sub(r"<[^>]+>", " ", value or ""))
    return re.sub(r"\s+", " ", value).strip()


def parse_feed(source: str, xml_text: str) -> list[dict[str, Any]]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    items = []
    for entry in root.findall(".//item") + root.findall(".//{http://www.w3.org/2005/Atom}entry"):
        def get(*names: str) -> str:
            for name in names:
                child = entry.find(name)
                if child is not None and child.text:
                    return child.text
            return ""

        link = get("link", "{http://www.w3.org/2005/Atom}link")
        if not link:
            atom_link = entry.find("{http://www.w3.org/2005/Atom}link")
            link = atom_link.attrib.get("href", "") if atom_link is not None else ""
        title = clean_text(get("title", "{http://www.w3.org/2005/Atom}title"))
        description = clean_text(get("description", "summary", "{http://www.w3.org/2005/Atom}summary", "{http://www.w3.org/2005/Atom}content"))
        date = get("pubDate", "published", "updated", "{http://www.w3.org/2005/Atom}published", "{http://www.w3.org/2005/Atom}updated")[:10]
        if title and link:
            items.append({"title": title, "source": source, "url": link, "date": date or "recent", "description": description})
    return items


def fetch_live_articles() -> list[dict[str, Any]]:
    articles: list[dict[str, Any]] = []
    for source, url in RSS_FEEDS.items():
        try:
            articles.extend(parse_feed(source, fetch_text(url)))
        except Exception:
            continue
    return articles


class SearchParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.results: list[dict[str, str]] = []
        self._current: dict[str, str] | None = None
        self._capture = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "a" and "result__a" in attributes.get("class", ""):
            self._current = {"title": "", "url": attributes.get("href", "") or ""}
            self._capture = True

    def handle_data(self, data: str) -> None:
        if self._capture and self._current is not None:
            self._current["title"] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._current is not None:
            self._current["title"] = clean_text(self._current["title"])
            self.results.append(self._current)
            self._current = None
            self._capture = False


def search_opportunities(query: str) -> list[dict[str, str]]:
    """Retrieve public search results; failures return an empty list safely."""
    url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    try:
        parser = SearchParser()
        parser.feed(fetch_text(url))
        return parser.results[:8]
    except Exception:
        return []
