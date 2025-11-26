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
    This is our 'rule-based AI' instead of calling an external model.
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
        "la ", " ms ", " ar ", " al ",
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


def format_item(item):
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


def section_from_items(title, items, fallback_msg):
    """Build a Markdown section from a list of items."""
    if not items:
        return f"## {title}\n\n- {fallback_msg}\n\n"

    lines = [f"## {title}\n"]
    for it in items[:10]:  # cap list length
        lines.append(f"- {format_item(it)}")
    lines.append("")  # blank line at end
    return "\n".join(lines)


def build_digest(items):
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

    # Sections
    sections = []

    sections.append(
        section_from_items(
            "What Changed in Rural Health Policy Today",
            items,
            "No rural-relevant news items were detected today.",
        )
    )

    sections.append(
        section_from_items(
            "Top Risks for Rural Hospitals and Clinics",
            categories["risk"],
            "No obvious risk-related headlines detected in today's feeds.",
        )
    )

    sections.append(
        section_from_items(
            "Opportunities & Funding Signals",
            categories["opportunity"],
            "No clear grant/funding/payment opportunities detected today.",
        )
    )

    sections.append(
        section_from_items(
            "Legislation & Regulations to Watch",
            categories["legislation"],
            "No major legislative or regulatory items detected by keyword scan.",
        )
    )

    sections.append(
        section_from_items(
            "Signals for Rural GME and Training Pipelines",
            categories["gme"],
            "No explicit GME/residency pipeline items detected today.",
        )
    )

    sections.append(
        section_from_items(
            "Notes for Louisiana / Deep South (LA, MS, AR, AL)",
            categories["deep_south"],
            "No items explicitly mentioning Louisiana, Mississippi, Arkansas, or Alabama.",
        )
    )

    return "\n".join(header + sections)


if __name__ == "__main__":
    items = load_latest_items()
    print(f"[INFO] Loaded {len(items)} news items")

    digest_md = build_digest(items)
    digest_path = DOCS_DIR / "daily_digest.md"

    with digest_path.open("w", encoding="utf-8") as f:
        f.write(digest_md)

    print(f"[INFO] Updated digest at {digest_path}")
