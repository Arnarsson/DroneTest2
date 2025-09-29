"""
Danish Police website scraper
"""
import httpx
import re
from datetime import datetime, timezone
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import dateutil.parser

def fetch_police_news(base_url: str) -> List[Dict]:
    """
    Fetch news items from Danish police website
    """
    items = []

    try:
        # Fetch news listing page
        response = httpx.get(base_url, timeout=30, follow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        # Find news links (adjust selectors as needed)
        for article in soup.select("article, .news-item, .teaser"):
            link_elem = article.select_one("a[href*='/nyhed/'], a.teaser__link")
            if not link_elem:
                continue

            href = link_elem.get("href", "")
            if not href:
                continue

            # Make absolute URL
            if not href.startswith("http"):
                href = f"https://politi.dk{href}"

            # Get title
            title = link_elem.get_text(" ", strip=True)
            if not title:
                title_elem = article.select_one("h2, h3, .title")
                if title_elem:
                    title = title_elem.get_text(" ", strip=True)

            # Get summary
            summary = ""
            summary_elem = article.select_one(".summary, .excerpt, .teaser__summary")
            if summary_elem:
                summary = summary_elem.get_text(" ", strip=True)

            # Check if drone-related
            full_text = (title + " " + summary).lower()
            if not any(kw in full_text for kw in ["drone", "dron", "uav"]):
                continue

            items.append({
                "title": title,
                "url": href,
                "summary": summary,
                "source_type": "police"
            })

    except Exception as e:
        print(f"Error fetching police news from {base_url}: {e}")

    return items

def fetch_police_article(url: str) -> Dict:
    """
    Fetch full article content from police website
    """
    try:
        response = httpx.get(url, timeout=30, follow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        # Extract article body
        article = soup.select_one("article, .content, .news-content, main")
        if not article:
            article = soup

        # Clean text
        for element in article(["script", "style", "nav", "header", "footer"]):
            element.decompose()

        text = article.get_text(" ", strip=True)

        # Extract time from Danish police format
        occurred_iso = extract_danish_datetime(text)

        # Extract quotes
        quote = extract_police_quote(text)

        return {
            "text": text[:3000],  # Limit length
            "quote": quote,
            "occurred_iso": occurred_iso
        }

    except Exception as e:
        print(f"Error fetching article {url}: {e}")
        return {"text": "", "quote": None, "occurred_iso": None}

def extract_danish_datetime(text: str) -> Optional[str]:
    """
    Extract datetime from Danish text
    Common patterns:
    - "lørdag aften kl. 21:44"
    - "25. december 2024 kl. 14:30"
    - "25/12-2024 kl. 14:30"
    """
    patterns = [
        # Full date with time
        r'(\d{1,2})\.\s*(\w+)\s+(\d{4})\s+kl\.?\s*(\d{1,2})[:\.](\d{2})',
        # Date slash format
        r'(\d{1,2})/(\d{1,2})-(\d{4})\s+kl\.?\s*(\d{1,2})[:\.](\d{2})',
        # Time with day name
        r'(mandag|tirsdag|onsdag|torsdag|fredag|lørdag|søndag)\s+\w*\s+kl\.?\s*(\d{1,2})[:\.](\d{2})',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                # Parse the matched datetime
                dt = dateutil.parser.parse(match.group(0), fuzzy=True)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.isoformat()
            except:
                continue

    # Fallback to current time
    return datetime.now(timezone.utc).isoformat()

def extract_police_quote(text: str) -> Optional[str]:
    """
    Extract official quote from police text
    """
    # Look for quotes or official statements
    patterns = [
        r'"([^"]{30,300})"',  # Quoted text
        r'»([^»]{30,300})»',  # Danish quotes
        r'(?:oplyser|fortæller|siger|meddeler)\s+(?:politiet|vagtchefen)[:\s]*([^.]{30,300})',
        r'(?:Politiet|Vagtchefen)\s+(?:oplyser|fortæller|siger)[:\s]*([^.]{30,300})',
        r'Der er\s+([^.]*(?:anmeldelse|anmeldt|indberettet)[^.]{10,200})',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            quote = match.group(1).strip()
            # Clean up quote
            quote = re.sub(r'\s+', ' ', quote)
            return quote[:300]  # Limit length

    # Fallback: find first sentence mentioning drone
    sentences = text.split('.')
    for sentence in sentences:
        if any(kw in sentence.lower() for kw in ["drone", "dron", "luftfartøj"]):
            return sentence.strip()[:300]

    return None