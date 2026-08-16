#!/usr/bin/env python3
"""Fetch digital trends from multiple sources."""
import json
import urllib.request
from datetime import datetime
import feedparser

def fetch_rss(url, source_name, limit=8):
    """Fetch RSS feed and return trends."""
    trends = []
    try:
        feed = feedparser.parse(url)
        for i, entry in enumerate(feed.entries[:limit]):
            trends.append({
                "rank": i + 1,
                "title": entry.title,
                "source": source_name,
                "heat": max(95 - i * 5, 55),
                "url": entry.link
            })
    except Exception as e:
        print(f"{source_name} RSS error: {e}")
    return trends

def fetch_ithome():
    """Fetch IT之家 RSS."""
    return fetch_rss("https://www.ithome.com/rss/", "IT之家", 8)

def fetch_sspai():
    """Fetch 少数派 RSS - 数码生活."""
    return fetch_rss("https://sspai.com/feed", "少数派", 6)

def fetch_ifanr():
    """Fetch 爱范儿 RSS - 数码科技."""
    return fetch_rss("https://www.ifanr.com/feed", "爱范儿", 6)

def fetch_36kr():
    """Fetch 36氪 RSS - 科技创业."""
    return fetch_rss("https://36kr.com/feed", "36氪", 6)

def fetch_coolapk_rsshub():
    """Fetch 酷安 via RSSHub."""
    return fetch_rss("https://rsshub.app/coolapk/tuwen", "酷安", 6)

def fetch_zhihu_hot():
    """Fetch 知乎热榜 via RSSHub."""
    return fetch_rss("https://rsshub.app/zhihu/hotlist", "知乎", 6)

def fetch_weibo_hot():
    """Fetch 微博热搜 via RSSHub."""
    return fetch_rss("https://rsshub.app/weibo/search/hot", "微博", 6)

def generate_ideas(trends):
    """Generate 5 topic ideas based on trends."""
    ideas = []
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
    print("Fetching trends from multiple sources...")
    
    all_trends = []
    
    # Fetch from multiple sources
    sources = [
        ("IT之家", fetch_ithome),
        ("少数派", fetch_sspai),
        ("爱范儿", fetch_ifanr),
        ("36氪", fetch_36kr),
        ("酷安", fetch_coolapk_rsshub),
        ("知乎", fetch_zhihu_hot),
        ("微博", fetch_weibo_hot),
    ]
    
    for name, fetch_func in sources:
        try:
            trends = fetch_func()
            print(f"  {name}: {len(trends)} items")
            all_trends.extend(trends)
        except Exception as e:
            print(f"  {name}: failed - {e}")
    
    # Sort by heat and re-rank
    all_trends.sort(key=lambda x: x["heat"], reverse=True)
    for i, t in enumerate(all_trends):
        t["rank"] = i + 1
    
    # Keep top 20
    all_trends = all_trends[:20]
    
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
    
    print(f"\nTotal: {len(all_trends)} trends, {len(ideas)} ideas")
    print("Saved to data/trends.json")

if __name__ == "__main__":
    main()
