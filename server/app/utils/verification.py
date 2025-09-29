import logging
from urllib.parse import urlparse

logger = logging.getLogger("dronewatch.verify")

SAFE_DOMAINS = {"politi.dk","reuters.com","dr.dk","nrk.no","aftonbladet.se","svt.se"}

def normalize_domain(url: str) -> str:
    try:
        d = urlparse(str(url)).netloc.lower()
        return d.split(":")[0].replace("www.","")
    except Exception:
        return ""

def score_source(domain: str, declared_type: str | None) -> int:
    base = 1
    if domain in SAFE_DOMAINS:
        base = 3
    if declared_type == "police" or declared_type == "notam":
        base = 4
    return base

def validate_article_fields(title: str, occurred_at, lat: float, lon: float) -> None:
    if not title or not occurred_at:
        raise ValueError("Missing required fields")
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Invalid coordinates")