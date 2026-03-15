"""
AI Safety News Monitor
======================
Scrapes AI safety and superintelligence news daily from 10+ sources,
summarises headlines, and produces a structured daily digest.

Mirrors the core responsibility described in the ControlAI Media Relations
JD: "Produce daily news roundups to keep the entire team at the forefront
of AI news developments."

Sources covered:
  - MIT Technology Review
  - The Guardian (Technology)
  - Wired (AI)
  - BBC Technology
  - TechCrunch (AI)
  - VentureBeat (AI)
  - AI Safety Newsletter (80,000 Hours)
  - Future of Life Institute
  - Alignment Forum (RSS)
  - DeepMind Blog

Author: Atrija Haldar
"""

import requests
import feedparser
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
import re
import time

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Configuration ──────────────────────────────────────────────────────────────

AI_SAFETY_KEYWORDS = [
    "artificial intelligence", "AI safety", "superintelligence",
    "alignment", "AGI", "large language model", "LLM", "GPT",
    "machine learning", "deep learning", "AI risk", "AI governance",
    "AI regulation", "existential risk", "AI policy", "OpenAI",
    "Anthropic", "DeepMind", "AI Act", "frontier AI",
    "transformative AI", "AI control", "AI ethics"
]

RSS_FEEDS = {
    "MIT Technology Review":     "https://www.technologyreview.com/feed/",
    "The Guardian Technology":   "https://www.theguardian.com/uk/technology/rss",
    "Wired":                     "https://www.wired.com/feed/rss",
    "BBC Technology":            "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "TechCrunch":                "https://techcrunch.com/feed/",
    "VentureBeat":               "https://feeds.feedburner.com/venturebeat/SZYF",
    "Future of Life Institute":  "https://futureoflife.org/feed/",
    "80000 Hours":               "https://80000hours.org/feed/",
    "AI Alignment Forum":        "https://www.alignmentforum.org/feed.xml",
}

LOOKBACK_HOURS = 24   # Only include articles from the last 24 hours
MAX_PER_SOURCE = 5    # Max articles per source in digest


# ── 1. Feed fetching ───────────────────────────────────────────────────────────

def fetch_feed(source_name: str, url: str) -> list:
    """
    Fetches and parses an RSS feed.
    Returns list of article dicts with title, summary, link, published.
    """
    try:
        feed    = feedparser.parse(url)
        entries = []

        for entry in feed.entries[:20]:
            title   = entry.get("title", "").strip()
            summary = entry.get("summary", entry.get("description", "")).strip()
            link    = entry.get("link", "")

            # Parse published date
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                published = datetime(*entry.updated_parsed[:6])
            else:
                published = datetime.utcnow()

            entries.append({
                "source":    source_name,
                "title":     title,
                "summary":   clean_html(summary)[:300],
                "link":      link,
                "published": published,
            })

        return entries

    except Exception as e:
        print(f"  Warning: Could not fetch {source_name}: {e}")
        return []


def clean_html(text: str) -> str:
    """Strips HTML tags from text."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_all_feeds(feeds: dict) -> list:
    """Fetches all RSS feeds and returns combined article list."""
    print(f"Fetching {len(feeds)} news sources...")
    all_articles = []

    for source, url in feeds.items():
        articles = fetch_feed(source, url)
        print(f"  {source:<35} {len(articles)} articles fetched")
        all_articles.extend(articles)
        time.sleep(0.3)  # polite crawl delay

    print(f"\n  Total articles fetched: {len(all_articles)}")
    return all_articles


# ── 2. Relevance filtering ─────────────────────────────────────────────────────

def is_ai_safety_relevant(article: dict) -> bool:
    """
    Returns True if the article title or summary contains
    at least one AI safety keyword.
    """
    text = (article["title"] + " " + article["summary"]).lower()
    return any(kw.lower() in text for kw in AI_SAFETY_KEYWORDS)


def is_recent(article: dict, hours: int = LOOKBACK_HOURS) -> bool:
    """Returns True if article was published within the last N hours."""
    if not article["published"]:
        return True
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    return article["published"] >= cutoff


def filter_articles(articles: list) -> list:
    """Filters to recent, AI-safety-relevant articles."""
    filtered = [
        a for a in articles
        if is_ai_safety_relevant(a) and is_recent(a)
    ]
    print(f"  Relevant articles (last {LOOKBACK_HOURS}hrs): {len(filtered)}")
    return filtered


# ── 3. Categorisation ──────────────────────────────────────────────────────────

CATEGORIES = {
    "Superintelligence & Existential Risk": [
        "superintelligence", "existential risk", "x-risk", "agi",
        "alignment", "control problem", "AI control", "extinction"
    ],
    "AI Regulation & Policy": [
        "regulation", "policy", "legislation", "government", "parliament",
        "congress", "senate", "AI Act", "executive order", "ban", "law"
    ],
    "AI Capabilities & Research": [
        "GPT", "Claude", "Gemini", "LLM", "large language model",
        "benchmark", "capabilities", "model", "training", "research"
    ],
    "Industry & Companies": [
        "OpenAI", "Anthropic", "DeepMind", "Google", "Microsoft",
        "Meta AI", "startup", "funding", "investment", "product"
    ],
    "Ethics & Society": [
        "ethics", "bias", "fairness", "privacy", "surveillance",
        "misinformation", "deepfake", "jobs", "workforce", "society"
    ],
}


def categorise_article(article: dict) -> str:
    """Assigns an article to the most relevant category."""
    text = (article["title"] + " " + article["summary"]).lower()
    scores = defaultdict(int)

    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw.lower() in text:
                scores[category] += 1

    if scores:
        return max(scores, key=scores.get)
    return "General AI News"


def categorise_all(articles: list) -> dict:
    """Groups articles by category."""
    categorised = defaultdict(list)
    for article in articles:
        cat = categorise_article(article)
        categorised[cat].append(article)
    return dict(categorised)


# ── 4. Digest generation ───────────────────────────────────────────────────────

def generate_digest(categorised: dict) -> str:
    """
    Produces a formatted daily digest string.
    Format mirrors a real media team briefing note.
    """
    today   = datetime.utcnow().strftime("%A %d %B %Y")
    lines   = []

    lines.append("=" * 70)
    lines.append(f"  AI SAFETY & SUPERINTELLIGENCE DAILY DIGEST")
    lines.append(f"  {today} | Generated by AI Safety News Monitor")
    lines.append("=" * 70)

    total = sum(len(v) for v in categorised.values())
    lines.append(f"\n  {total} relevant articles across "
                 f"{len(categorised)} categories\n")

    # Priority order for categories
    priority = [
        "Superintelligence & Existential Risk",
        "AI Regulation & Policy",
        "AI Capabilities & Research",
        "Industry & Companies",
        "Ethics & Society",
        "General AI News",
    ]

    for category in priority:
        articles = categorised.get(category, [])
        if not articles:
            continue

        lines.append(f"\n── {category.upper()} ({len(articles)} articles) ──")
        lines.append("─" * 70)

        # Sort by published date, most recent first
        articles_sorted = sorted(
            articles,
            key=lambda x: x["published"] or datetime.min,
            reverse=True
        )[:MAX_PER_SOURCE]

        for i, article in enumerate(articles_sorted, 1):
            pub_str = article["published"].strftime("%H:%M UTC") \
                if article["published"] else "unknown time"

            lines.append(f"\n  {i}. {article['title']}")
            lines.append(f"     Source: {article['source']} | {pub_str}")
            if article["summary"]:
                lines.append(f"     {article['summary'][:200]}...")
            lines.append(f"     Link: {article['link']}")

    lines.append("\n" + "=" * 70)
    lines.append("  End of digest")
    lines.append("=" * 70)

    return "\n".join(lines)


# ── 5. Export ──────────────────────────────────────────────────────────────────

def export_digest(digest: str, categorised: dict):
    """Saves digest as txt and structured JSON."""
    date_str = datetime.utcnow().strftime("%Y-%m-%d")

    # Text digest
    txt_path = f"{OUTPUT_DIR}/digest_{date_str}.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(digest)

    # JSON for downstream processing
    json_data = {
        "date":       date_str,
        "generated":  datetime.utcnow().isoformat(),
        "categories": {
            cat: [
                {
                    "title":     a["title"],
                    "source":    a["source"],
                    "link":      a["link"],
                    "published": a["published"].isoformat()
                    if a["published"] else None,
                    "summary":   a["summary"],
                }
                for a in articles
            ]
            for cat, articles in categorised.items()
        }
    }
    json_path = f"{OUTPUT_DIR}/digest_{date_str}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)

    print(f"\n  Saved: {txt_path}")
    print(f"  Saved: {json_path}")


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("AI Safety News Monitor")
    print("=" * 40)

    articles    = fetch_all_feeds(RSS_FEEDS)
    filtered    = filter_articles(articles)
    categorised = categorise_all(filtered)
    digest      = generate_digest(categorised)
    export_digest(digest, categorised)

    print("\n" + digest[:2000])  # Preview first 2000 chars
    print("\nFull digest saved to /output")
