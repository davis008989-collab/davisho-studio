#!/usr/bin/env python3
"""Fetch digital trends from IT之家, 酷安, and other sources."""
import json
import re
import urllib.request
from datetime import datetime
import feedparser
from bs4 import BeautifulSoup

def fetch_ithome():
    """Fetch IT之家 hot news."""
    trends = []
    try:
        url = "https://www.ithome.com/"
        headers = {"User-Agent": "Mozilla/5.0"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser')
        # Find hot news items
        items = soup.select('.new-list-1 li, .new-list-2 li')[:10]
        for i, item in enumerate(items):
            a = item.find('a')
            if a:
                title = a.get_text(strip=True)
                if title and len(title) > 5:
                    trends.append({
                        "rank": i + 1,
                        "title": title,
                        "source": "IT之家",
                        "heat": max(95 - i * 5, 60),
                        "url": a.get('href', '')
                    })
    except Exception as e:
        print(f"IT之家 fetch error: {e}")
    return trends

def fetch_ithome_rss():
    """Fetch IT之家 RSS as fallback."""
    trends = []
    try:
        feed = feedparser.parse("https://www.ithome.com/rss/")
        for i, entry in enumerate(feed.entries[:8]):
            trends.append({
                "rank": i + 1,
                "title": entry.title,
                "source": "IT之家",
                "heat": max(95 - i * 6, 55),
                "url": entry.link
            })
    except Exception as e:
        print(f"IT之家 RSS error: {e}")
    return trends

def fetch_coolapk():
    """Fetch 酷安 hot topics."""
    trends = []
    try:
        url = "https://www.coolapk.com/"
        headers = {"User-Agent": "Mozilla/5.0"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser')
        # Try to find article titles
        items = soup.find_all(['h2', 'h3', 'h4'], limit=10)
        for i, item in enumerate(items):
            title = item.get_text(strip=True)
            if title and len(title) > 5 and len(title) < 60:
                trends.append({
                    "rank": i + 1,
                    "title": title,
                    "source": "酷安",
                    "heat": max(90 - i * 5, 50),
                    "url": ""
                })
    except Exception as e:
        print(f"酷安 fetch error: {e}")
    return trends

def generate_ideas(trends):
    """Generate 5 topic ideas based on trends."""
    ideas = []
    
    # Idea templates based on trend keywords
    keywords = [t["title"] for t in trends[:5]]
    
    templates = [
        {"type": "爆料前瞻", "typeColor": "#8b5cf6", "typeBg": "#f5f3ff",
         "title_tpl": "{keyword}这配置，你冲不冲？🔥", "heat": 96},
        {"type": "对比测评", "typeColor": "#3b82f6", "typeBg": "#eff6ff",
         "title_tpl": "{keyword} vs 上一代，升级了个寂寞？📱", "heat": 92},
        {"type": "价格红利", "typeColor": "#10b981", "typeBg": "#ecfdf5",
         "title_tpl": "{keyword}这价格，国补后真香警告💰", "heat": 88},
        {"type": "体验分享", "typeColor": "#f59e0b", "typeBg": "#fffbeb",
         "title_tpl": "{keyword}用了7天，说点大实话✨", "heat": 85},
        {"type": "争议话题", "typeColor": "#ef4444", "typeBg": "#fef2f2",
         "title_tpl": "{keyword}是智商税？我不同意🤔", "heat": 90},
    ]
    
    for i, tpl in enumerate(templates):
        keyword = keywords[i] if i < len(keywords) else "数码新品"
        # Extract short keyword (first 10-15 chars)
        short_kw = keyword[:15] if len(keyword) > 15 else keyword
        title = tpl["title_tpl"].format(keyword=short_kw)
        ideas.append({
            "id": i + 1,
            "type": tpl["type"],
            "typeColor": tpl["typeColor"],
            "typeBg": tpl["typeBg"],
            "title": title,
            "direction": f"围绕{short_kw}展开，抓住用户痛点和好奇心",
            "hook": "评论区见，你同意吗？",
            "format": "图文/短视频",
            "heat": tpl["heat"],
            "tag": short_kw.replace(' ', '')[:6]
        })
    
    return ideas

def main():
    print("Fetching trends...")
    
    # Fetch from multiple sources
    trends = fetch_ithome_rss()
    if not trends:
        trends = fetch_ithome()
    
    coolapk_trends = fetch_coolapk()
    
    # Merge and sort
    all_trends = trends + coolapk_trends
    all_trends.sort(key=lambda x: x["heat"], reverse=True)
    
    # Re-rank
    for i, t in enumerate(all_trends):
        t["rank"] = i + 1
    
    # Keep top 10
    all_trends = all_trends[:10]
    
    # Generate ideas
    ideas = generate_ideas(all_trends)
    
    # Save data
    data = {
        "updated_at": datetime.now().isoformat(),
        "trends": all_trends,
        "ideas": ideas
    }
    
    with open("data/trends.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(all_trends)} trends and {len(ideas)} ideas.")

if __name__ == "__main__":
    main()
