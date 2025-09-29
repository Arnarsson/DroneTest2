"""
Generic RSS feed parser
"""
import feedparser
import dateutil.parser
from datetime import datetime, timezone
from typing import Iterator, Dict, Optional
from bs4 import BeautifulSoup
import re

def parse_rss_feed(feed_url: str) -> Iterator[Dict]:
    """
    Parse RSS feed and yield normalized items
    """
    try:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:50]:  # Limit to recent 50 entries
            # Extract basic fields
            title = entry.get("title", "").strip()
            link = entry.get("link", "")

            # Clean summary/description
            summary_raw = entry.get("summary") or entry.get("description", "")
            summary = clean_html(summary_raw)

            # Parse publication date
            published_str = entry.get("published") or entry.get("updated")
            published_iso = None
            if published_str:
                try:
                    dt = dateutil.parser.parse(published_str)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    published_iso = dt.isoformat()
                except:
                    pass

            yield {
                "title": title,
                "url": link,
                "summary": summary,
                "published_iso": published_iso,
                "raw": entry  # Keep raw for debugging
            }

    except Exception as e:
        print(f"Error parsing RSS feed {feed_url}: {e}")
        return

def clean_html(html_text: str) -> str:
    """Remove HTML tags and clean text"""
    if not html_text:
        return ""

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_text, "lxml")

    # Remove script and style elements
    for element in soup(["script", "style"]):
        element.decompose()

    # Get text
    text = soup.get_text(" ", strip=True)

    # Clean whitespace
    text = re.sub(r'\s+', ' ', text)

    return text.strip()