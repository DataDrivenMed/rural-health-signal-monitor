import feedparser
import datetime as dt
import json
from pathlib import Path

# Simple selection of rural-relevant feeds.
# You can add more later.
RSS_FEEDS = {
    "KFF_Health_News": "https://kffhealthnews.org/feed/",  # All KFF Health News content 
    "RHIhub_News": "https://www.ruralhealthinfo.org/rss/news/topics/rural-health-services.xml",  # example topic feed 
    # You can later add a CMS-specific RSS URL once you identify the exact endpoint.
}

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def fetch_all():
    items = []
    for name, url in RSS_FEEDS.items():
        print(f"[INFO] Fetching {name} from {url}")
        feed = feedparser.parse(url)
        for entry in feed.entries[:15]:  # limit per source
            items.append({
                "source": name,
                "title": entry.get("title", ""),
                "summary": entry.get("summary", "") or entry.get("description", ""),
                "published": entry.get("published", ""),
                "link": entry.get("link", "")
            })
    return items

if __name__ == "__main__":
    today = dt.date.today().isoformat()
    items = fetch_all()
    out_path = DATA_DIR / f"rss_{today}.json"
    with out_path.open("w") as f:
        json.dump(items, f, indent=2)
    print(f"[INFO] Saved {len(items)} items to {out_path}")
