import os
import json
import datetime as dt
from pathlib import Path
from openai import OpenAI

DATA_DIR = Path("data")
DOCS_DIR = Path("docs")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_latest_items():
    today = dt.date.today().isoformat()
    file_path = DATA_DIR / f"rss_{today}.json"
    if not file_path.exists():
        raise FileNotFoundError(f"No RSS file found for today: {file_path}")
    with file_path.open() as f:
        return json.load(f)

def build_news_block(items):
    lines = []
    for i in items:
        lines.append(f"- [{i['source']}] {i['title']} — {i['summary']} (Link: {i['link']})")
    return "\n".join(lines)

def summarize(items):
    news_block = build_news_block(items)

    prompt = f"""
You are a senior rural health policy analyst.

You will read a list of news items (titles, short summaries, and links) from rural-relevant sources
(KFF Health News, Rural Health Information Hub, etc.). Identify what matters for:

- Rural hospitals (especially CAHs and small PPS hospitals)
- Rural clinics and FQHCs
- Rural GME and residency expansion (family medicine, psychiatry, OB, IM)
- Rural health workforce pipelines
- Medicaid and Medicare payment for rural providers

Please structure your response in Markdown sections:

1. **What Changed in Rural Health Policy Today**
2. **Top Risks for Rural Hospitals and Clinics**
3. **Opportunities & Funding Signals** (grants, payment models, workforce)
4. **Legislation & Regulations to Watch**
5. **Signals for Rural GME and Training Pipelines**
6. **Quick Notes for Louisiana / Deep South (if any)**

Be concise but analytic. Use bullet points, and if something is speculative, say so.

Here are the news items:

{news_block}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    items = load_latest_items()
    print(f"[INFO] Loaded {len(items)} news items")

    summary_md = summarize(items)

    today = dt.date.today().isoformat()
    digest_path = DOCS_DIR / "daily_digest.md"

    with digest_path.open("w") as f:
        f.write(f"# Rural Health Policy Digest — {today}\n\n")
        f.write(summary_md)

    print(f"[INFO] Updated digest at {digest_path}")
