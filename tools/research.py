#!/usr/bin/env python3.12
# -*- coding: UTF-8 -*-
"""研究工具：HN Algolia + GitHub API"""

import json
import time
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.parse import quote
from urllib.error import URLError


def http_get_json(url, timeout=10, retries=2):
    """HTTP GET with retry"""
    for attempt in range(retries + 1):
        try:
            req = Request(url, headers={"User-Agent": "DailyAINews/1.0"})
            with urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            if attempt < retries:
                time.sleep(1.5)
                continue
            print(f"[http] Error: {url}: {e}")
            return None


def search_hackernews(query, hits_per_page=15, days_back=3):
    """搜索 Hacker News（带日期过滤）"""
    since_ts = int(time.time() - (days_back * 86400))
    url = (
        f"https://hn.algolia.com/api/v1/search"
        f"?query={quote(query)}"
        f"&tags=story"
        f"&hitsPerPage={hits_per_page}"
        f"&numericFilters=created_at_i>{since_ts}"
    )
    data = http_get_json(url)
    if not data:
        return []

    results = []
    for hit in data.get("hits", []):
        created_at = hit.get("created_at_i", 0)
        story_url = hit.get("url", "")
        if not story_url or "ycombinator.com" in story_url:
            story_url = f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"

        results.append({
            "source": "hackernews",
            "title": hit.get("title", ""),
            "url": story_url,
            "points": hit.get("points", 0),
            "comments": hit.get("num_comments", 0),
            "author": hit.get("author", ""),
            "date": datetime.fromtimestamp(created_at).strftime("%Y-%m-%d") if created_at else "",
            "hn_id": hit.get("objectID", ""),
        })

    results.sort(key=lambda x: x.get("points", 0), reverse=True)
    return results


def search_github(query, days_back=3, per_page=10):
    """搜索 GitHub trending 仓库"""
    since = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    url = (
        f"https://api.github.com/search/repositories"
        f"?q={quote(query)}+created:>{since}"
        f"&sort=stars&order=desc&per_page={per_page}"
    )
    data = http_get_json(url)
    if not data:
        return []

    results = []
    for repo in data.get("items", []):
        results.append({
            "source": "github",
            "title": repo.get("full_name", ""),
            "url": repo.get("html_url", ""),
            "description": repo.get("description", "") or "",
            "stars": repo.get("stargazers_count", 0),
            "language": repo.get("language", ""),
            "date": repo.get("created_at", "")[:10],
        })

    return results


def research_ai_hotspots(days_back=3):
    """综合研究AI领域当日热点"""
    all_results = []

    # 核心AI关键词搜索
    core_queries = [
        ("AI artificial intelligence", 15),
        ("large language model LLM", 10),
        ("machine learning deep learning", 10),
        ("GPT OpenAI Claude Gemini", 10),
        ("AI research paper breakthrough", 8),
    ]

    for query, hits in core_queries:
        hn = search_hackernews(query, hits_per_page=hits, days_back=days_back)
        all_results.extend(hn)
        time.sleep(1.5)

    # GitHub trending
    gh = search_github("AI artificial intelligence", days_back=days_back, per_page=10)
    all_results.extend(gh)

    # 偏生物医药方向
    bio_queries = [
        ("AI drug discovery biology", 8),
        ("AI medical healthcare clinical", 8),
        ("AI protein genomics", 5),
    ]
    for query, hits in bio_queries:
        hn = search_hackernews(query, hits_per_page=hits, days_back=days_back)
        all_results.extend(hn)
        time.sleep(1.5)

    # 去重
    seen = set()
    unique = []
    for r in all_results:
        key = r.get("url", "") or r.get("title", "")
        if key and key not in seen:
            seen.add(key)
            unique.append(r)

    # 按热度排序（points + comments 加权）
    def hot_score(r):
        return r.get("points", 0) + r.get("comments", 0) * 2

    unique.sort(key=hot_score, reverse=True)

    print(f"[research] Found {len(unique)} unique items")
    return unique
