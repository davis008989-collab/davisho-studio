#!/usr/bin/env python3
"""Fetch digital trends from multiple sources."""
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

def fetch_rss_manual(url, source_name, limit=8):
    """Manual RSS parsing without feedparser."""
    trends = []
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
            timeout=15
        )
        with urllib.request.urlopen(req) as resp:
            content = resp.read()
            content_str = content.decode('utf-8', errors='ignore')
            
            # Parse RSS items manually
            items = []
            in_item = False
            current_item = {}
            
            # Simple XML parsing approach
            try:
                root = ET.fromstring(content)
                for item in root.iter('item'):
                    title = None
                    link = None
                    for child in item:
                        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                        if tag == 'title':
                            title = (child.text or '').strip()
                        elif tag == 'link':
                            link = (child.text or '').strip()
                    if title:
                        items.append({'title': title, 'link': link or url})
                    if len(items) >= limit:
                        break
            except ET.ParseError as e:
                print(f"    XML parse error for {source_name}: {e}")
                return trends
            
            for i, entry in enumerate(items):
                trends.append({
                    "rank": i + 1,
                    "title": entry['title'][:80],
                    "source": source_name,
                    "heat": max(95 - i * 5, 55),
                    "url": entry['link']
                })
    except urllib.error.URLError as e:
        print(f"    URL error for {source_name}: {e}")
    except Exception as e:
        print(f"    Unexpected error for {source_name}: {type(e).__name__}: {e}")
    return trends

def fetch_with_feedparser(url, source_name, limit=8):
    """Try feedparser first, fallback to manual parser."""
    try:
        import feedparser
        trends = []
        print(f"    Trying feedparser for {source_name}...")
        feed = feedparser.parse(url)
        
        if feed.bozo and hasattr(feed, 'bozo_exception'):
            print(f"    Feedparser warning for {source_name}: {feed.bozo_exception}")
        
        entries = feed.entries[:limit] if hasattr(feed, 'entries') else []
        print(f"    Feedparser found {len(entries)} entries for {source_name}")
        
        for i, entry in enumerate(entries):
            title = entry.title if hasattr(entry, 'title') else ''
            link = entry.link if hasattr(entry, 'link') else url
            trends.append({
                "rank": i + 1,
                "title": title[:80],
                "source": source_name,
                "heat": max(95 - i * 5, 55),
                "url": link
            })
        return trends
    except ImportError:
        print(f"    feedparser not available, using manual parser for {source_name}")
        return fetch_rss_manual(url, source_name, limit)
    except Exception as e:
        print(f"    feedparser error for {source_name}: {type(e).__name__}: {e}")
        print(f"    Falling back to manual parser for {source_name}")
        return fetch_rss_manual(url, source_name, limit)

def fetch_ithome():
    return fetch_with_feedparser("https://www.ithome.com/rss/", "IT之家", 8)

def fetch_sspai():
    return fetch_with_feedparser("https://sspai.com/feed", "少数派", 6)

def fetch_ifanr():
    return fetch_with_feedparser("https://www.ifanr.com/feed", "爱范儿", 6)

def fetch_36kr():
    return fetch_with_feedparser("https://36kr.com/feed", "36氪", 6)

def fetch_coolapk():
    return fetch_with_feedparser("https://rsshub.app/coolapk/tuwen", "酷安", 6)

def fetch_zhihu():
    return fetch_with_feedparser("https://rsshub.app/zhihu/hotlist", "知乎", 6)

def fetch_weibo():
    return fetch_with_feedparser("https://rsshub.app/weibo/search/hot", "微博", 6)

def get_fallback_trends():
    return [
        {"rank": 1, "title": "华为Mate80爆料：麒麟9030+全系直屏", "source": "IT之家", "heat": 98, "url": "https://www.ithome.com/"},
        {"rank": 2, "title": "荣耀WIN2曝光：2nm+10000mAh电池", "source": "微博", "heat": 95, "url": "https://weibo.com/"},
        {"rank": 3, "title": "小米17 Ultra首发2亿像素连续光变", "source": "IT之家", "heat": 92, "url": "https://www.ithome.com/"},
        {"rank": 4, "title": "努比亚Z90：全球首款AI智能体手机", "source": "36氪", "heat": 88, "url": "https://36kr.com/"},
        {"rank": 5, "title": "REDMI K90至尊版暂定4月发布", "source": "IT之家", "heat": 86, "url": "https://www.ithome.com/"},
        {"rank": 6, "title": "vivo X300 Ultra超广角断层领先", "source": "少数派", "heat": 84, "url": "https://sspai.com/"},
        {"rank": 7, "title": "国补+以旧换新：荣耀500 Pro下探3000", "source": "爱范儿", "heat": 82, "url": "https://www.ifanr.com/"},
        {"rank": 8, "title": "iPhone Air带动eSIM倒逼国产跟进", "source": "知乎", "heat": 78, "url": "https://www.zhihu.com/"},
        {"rank": 9, "title": "酷安热帖：这手机续航真的顶", "source": "酷安", "heat": 76, "url": "https://www.coolapk.com/"},
        {"rank": 10, "title": "数码闲聊站：某厂折叠屏又有新料", "source": "微博", "heat": 74, "url": "https://weibo.com/"},
    ]

def generate_ideas(trends):
    ideas = []
    keywords = [t["title"] for t in trends[:5]]
    
    templates = [
        {"type": "爆料前瞻", "typeColor": "#8b5cf6", "typeBg": "#f5f3ff",
         "title_tpl": "{keyword}这配置，你冲不冲？", "heat": 96},
        {"type": "对比测评", "typeColor": "#3b82f6", "typeBg": "#eff6ff",
         "title_tpl": "{keyword} vs 上一代，升级了个寂寞？", "heat": 92},
        {"type": "价格红利", "typeColor": "#10b981", "typeBg": "#ecfdf5",
         "title_tpl": "{keyword}这价格，国补后真香警告", "heat": 88},
        {"type": "体验分享", "typeColor": "#f59e0b", "typeBg": "#fffbeb",
         "title_tpl": "{keyword}用了7天，说点大实话", "heat": 85},
        {"type": "争议话题", "typeColor": "#ef4444", "typeBg": "#fef2f2",
         "title_tpl": "{keyword}是智商税？我不同意", "heat": 90},
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
    print(f"Fetching trends from multiple sources...")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    all_trends = []
    
    sources = [
        ("IT之家", fetch_ithome),
        ("少数派", fetch_sspai),
        ("爱范儿", fetch_ifanr),
        ("36氪", fetch_36kr),
        ("酷安", fetch_coolapk),
        ("知乎", fetch_zhihu),
        ("微博", fetch_weibo),
    ]
    
    for name, fetch_func in sources:
        try:
            print(f"\n  Fetching {name}...")
            trends = fetch_func()
            print(f"  {name}: {len(trends)} items")
            all_trends.extend(trends)
        except Exception as e:
            print(f"  {name}: CRITICAL ERROR - {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    if not all_trends:
        print("\nAll sources failed, using fallback data")
        all_trends = get_fallback_trends()
    
    all_trends.sort(key=lambda x: x["heat"], reverse=True)
    for i, t in enumerate(all_trends):
        t["rank"] = i + 1
    
    all_trends = all_trends[:20]
    
    ideas = generate_ideas(all_trends)
    
    data = {
        "updated_at": datetime.now().isoformat(),
        "trends": all_trends,
        "ideas": ideas
    }
    
    with open("data/trends.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== SUCCESS ===")
    print(f"Total: {len(all_trends)} trends, {len(ideas)} ideas")
    print(f"Saved to data/trends.json")

if __name__ == "__main__":
    main()
