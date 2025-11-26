import datetime as dt
import json
from pathlib import Path

DATA_DIR = Path("data")
DOCS_DIR = Path("docs")


def load_latest_items():
    """Load today's RSS JSON file written by fetch_rss.py."""
    today = dt.date.today().isoformat()
    file_path = DATA_DIR / f"rss_{today}.json"
    if not file_path.exists():
        raise FileNotFoundError(f"No RSS file found for today: {file_path}")
    with file_path.open() as f:
        return json.load(f)


def text_of(item):
    """Concatenate title + summary for keyword searching."""
    return f"{item.get('title','')} {item.get('summary','')}".lower()


def categorize_items(items):
    """
    Assign items to simple categories using keyword rules.
    This is our rule-based 'AI' instead of calling an external model.
    """

    categories = {
        "risk": [],
        "opportunity": [],
        "legislation": [],
        "gme": [],
        "deep_south": [],
    }

    # Keyword lists for simple classification
    risk_keywords = [
        "closure", "bankrupt", "insolvency", "financial distress",
        "risk", "crisis", "shortage", "underserved", "access problem",
        "cut", "reduction", "penalty",
    ]
    opportunity_keywords = [
        "grant", "funding", "award", "payment model", "demonstration",
        "pilot", "initiative", "program", "funded", "opportunity",
        "expansion", "increase", "bonus",
    ]
    legislation_keywords = [
        "bill", "law", "senate", "house", "congress", "regulation",
        "rule", "proposed rule", "final rule", "comment period",
        "cms", "medicare", "medicaid",
    ]
    gme_keywords = [
        "residency", "fellowship", "gme", "graduate medical education",
        "training program", "pipeline", "medical student",
        "resident physician", "teaching hospital",
    ]

    deep_south_keywords = [
        "louisiana", "mississippi", "arkansas", "alabama",
        " la ", " ms ", " ar ", " al ",
    ]

    for item in items:
        txt = text_of(item)

        if any(k in txt for k in risk_keywords):
            categories["risk"].append(item)

        if any(k in txt for k in opportunity_keywords):
            categories["opportunity"].append(item)

        if any(k in txt for k in legislation_keywords):
            categories["legislation"].append(item)

        if any(k in txt for k in gme_keywords):
            categories["gme"].append(item)

        if any(k in txt for k in deep_south_keywords):
            categories["deep_south"].append(item)

    return categories


def format_item_markdown(item):
    """Format a single news item as a Markdown bullet line."""
    source = item.get("source", "Unknown")
    title = item.get("title", "").strip()
    link = item.get("link", "").strip()
    published = item.get("published", "").strip()

    parts = [f"[{source}] {title}"]
    if published:
        parts.append(f"(_{published}_)")
    if link:
        parts.append(f"[Link]({link})")

    return " — ".join(parts)


def format_item_html(item):
    """Format a single news item as an HTML list item."""
    source = item.get("source", "Unknown")
    title = item.get("title", "").strip()
    link = item.get("link", "").strip()
    published = item.get("published", "").strip()

    text = f"<strong>{source}</strong>: {title}"
    if published:
        text += f" <em>({published})</em>"
    if link:
        text += f' <a href="{link}" target="_blank" rel="noopener noreferrer">Link</a>'

    return f"<li>{text}</li>"


def section_md_from_items(title, items, fallback_msg):
    """Build a Markdown section from a list of items."""
    if not items:
        return f"## {title}\n\n- {fallback_msg}\n\n"

    lines = [f"## {title}\n"]
    for it in items[:10]:  # cap list length
        lines.append(f"- {format_item_markdown(it)}")
    lines.append("")  # blank line at end
    return "\n".join(lines)


def section_html_from_items(title, items, fallback_msg):
    """Build an HTML section from a list of items."""
    if not items:
        return f"""
      <section class="digest-section">
        <h2>{title}</h2>
        <ul>
          <li>{fallback_msg}</li>
        </ul>
      </section>
    """

    lis = "\n".join(format_item_html(it) for it in items[:10])
    return f"""
      <section class="digest-section">
        <h2>{title}</h2>
        <ul>
{lis}
        </ul>
      </section>
    """


def build_digest_md(items):
    """Create the full Markdown digest string."""
    total = len(items)
    categories = categorize_items(items)

    header = [
        f"# Rural Health Policy Digest — {dt.date.today().isoformat()}",
        "",
        f"_Automated rule-based summary of {total} rural-relevant news items from multiple feeds._",
        "",
        "---",
        "",
    ]

    sections = []

    sections.append(
        section_md_from_items(
            "What Changed in Rural Health Policy Today",
            items,
            "No rural-relevant news items were detected today.",
        )
    )

    sections.append(
        section_md_from_items(
            "Top Risks for Rural Hospitals and Clinics",
            categories["risk"],
            "No obvious risk-related headlines detected in today's feeds.",
        )
    )

    sections.append(
        section_md_from_items(
            "Opportunities & Funding Signals",
            categories["opportunity"],
            "No clear grant/funding/payment opportunities detected today.",
        )
    )

    sections.append(
        section_md_from_items(
            "Legislation & Regulations to Watch",
            categories["legislation"],
            "No major legislative or regulatory items detected by keyword scan.",
        )
    )

    sections.append(
        section_md_from_items(
            "Signals for Rural GME and Training Pipelines",
            categories["gme"],
            "No explicit GME/residency pipeline items detected today.",
        )
    )

    sections.append(
        section_md_from_items(
            "Notes for Louisiana / Deep South (LA, MS, AR, AL)",
            categories["deep_south"],
            "No items explicitly mentioning Louisiana, Mississippi, Arkansas, or Alabama.",
        )
    )

    return "\n".join(header + sections)


def build_digest_html(items):
    """Create a full standalone HTML page for the digest."""
    total = len(items)
    categories = categorize_items(items)

    sections_html = []

    sections_html.append(
        section_html_from_items(
            "What Changed in Rural Health Policy Today",
            items,
            "No rural-relevant news items were detected today.",
        )
    )

    sections_html.append(
        section_html_from_items(
            "Top Risks for Rural Hospitals and Clinics",
            categories["risk"],
            "No obvious risk-related headlines detected in today's feeds.",
        )
    )

    sections_html.append(
        section_html_from_items(
            "Opportunities & Funding Signals",
            categories["opportunity"],
            "No clear grant/funding/payment opportunities detected today.",
        )
    )

    sections_html.append(
        section_html_from_items(
            "Legislation & Regulations to Watch",
            categories["legislation"],
            "No major legislative or regulatory items detected by keyword scan.",
        )
    )

    sections_html.append(
        section_html_from_items(
            "Signals for Rural GME and Training Pipelines",
            categories["gme"],
            "No explicit GME/residency pipeline items detected today.",
        )
    )

    sections_html.append(
        section_html_from_items(
            "Notes for Louisiana / Deep South (LA, MS, AR, AL)",
            categories["deep_south"],
            "No items explicitly mentioning Louisiana, Mississippi, Arkansas, or Alabama.",
        )
    )

    sections_joined = "\n".join(sections_html)

    today_str = dt.date.today().isoformat()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Rural Health Policy Digest — {today_str}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      max-width: 900px;
      margin: 32px auto;
      padding: 0 16px 40px 16px;
      background: #f5f7fb;
      color: #222;
    }}
    h1 {{
      color: #154360;
      margin-bottom: 0.25rem;
    }}
    h2 {{
      color: #1f4e79;
      margin-top: 1.4rem;
      margin-bottom: 0.4rem;
      font-size: 1.05rem;
    }}
    .subtle {{
      color: #555;
      font-size: 0.9rem;
    }}
    .digest-section {{
      background: #ffffff;
      border-radius: 12px;
      padding: 0.9rem 1rem;
      box-shadow: 0 3px 8px rgba(0,0,0,0.04);
      margin-top: 0.8rem;
    }}
    ul {{
      margin: 0.2rem 0 0 1.1rem;
      padding: 0;
      font-size: 0.9rem;
    }}
    li {{
      margin-bottom: 0.35rem;
    }}
    a {{
      color: #1f5b8a;
      text-decoration: none;
    }}
    a:hover {{
      text-decoration: underline;
    }}
    .back-link {{
      display: inline-block;
      margin-bottom: 0.6rem;
      font-size: 0.9rem;
    }}
  </style>
</head>
<body>
  <a href="./" class="back-link">← Back to Rural Health Signal Monitor</a>
  <h1>Rural Health Policy Digest</h1>
  <p class="subtle">
    Automated rule-based summary of {total} rural-relevant news items from multiple feeds.<br/>
    Date: {today_str}
  </p>

{sections_joined}

</body>
</html>
"""
    return html


def build_homepage_snippet_html(items):
    """
    Build a small HTML snippet for embedding on the homepage.
    Shows a 'snapshot' of a few key bullets.
    """
    categories = categorize_items(items)

    def top_n_lines(items_list, n=3):
        return "\n".join(format_item_html(it) for it in items_list[:n]) or "<li>No items detected.</li>"

    # Overall "what changed" – first few items from overall list
    what_changed = top_n_lines(items, 3)

    # Risks – from risk category
    risks = top_n_lines(categories["risk"], 3)

    # GME signals – from gme category
    gme = top_n_lines(categories["gme"], 3)

    today_str = dt.date.today().isoformat()

    snippet = f"""
<section>
  <h2>Today’s Rural Health Snapshot — {today_str}</h2>

  <div class="snapshot-block">
    <h3>What changed today?</h3>
    <ul>
{what_changed}
    </ul>
  </div>

  <div class="snapshot-block">
    <h3>Top risk signals</h3>
    <ul>
{risks}
    </ul>
  </div>

  <div class="snapshot-block">
    <h3>Signals for rural GME & pipelines</h3>
    <ul>
{gme}
    </ul>
  </div>
</section>
"""
    return snippet


if __name__ == "__main__":
    items = load_latest_items()
    print(f"[INFO] Loaded {len(items)} news items")

    # 1) Full Markdown digest (for GitHub / archive)
    digest_md = build_digest_md(items)
    md_path = DOCS_DIR / "daily_digest.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.write(digest_md)
    print(f"[INFO] Updated Markdown digest at {md_path}")

    # 2) Full HTML digest (for nice viewing)
    digest_html = build_digest_html(items)
    html_path = DOCS_DIR / "daily_digest.html"
    with html_path.open("w", encoding="utf-8") as f:
        f.write(digest_html)
    print(f"[INFO] Updated HTML digest at {html_path}")

    # 3) Homepage snapshot snippet
    snippet_html = build_homepage_snippet_html(items)
    snippet_path = DOCS_DIR / "digest_snippet.html"
    with snippet_path.open("w", encoding="utf-8") as f:
        f.write(snippet_html)
    print(f"[INFO] Updated homepage snippet at {snippet_path}")
