"""
Deduplication utilities
"""
import hashlib
import json
from datetime import datetime
from typing import Optional

def incident_hash(
    title: str,
    location: Optional[str],
    occurred_iso: Optional[str],
    country: str = "DK"
) -> str:
    """
    Generate consistent hash for incident deduplication
    Rounds time to nearest hour to catch near-duplicates
    """
    # Normalize components
    title_norm = (title or "").strip().lower()[:100]
    location_norm = (location or "").strip().lower()[:50]

    # Round time to hour
    time_norm = ""
    if occurred_iso:
        try:
            dt = datetime.fromisoformat(occurred_iso.replace("Z", "+00:00"))
            time_norm = dt.strftime("%Y-%m-%d-%H")
        except:
            time_norm = occurred_iso[:13] if occurred_iso else ""

    # Create hash
    content = f"{title_norm}|{location_norm}|{time_norm}|{country}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

class DedupCache:
    """Simple in-memory deduplication cache"""

    def __init__(self, max_size: int = 10000):
        self.cache = {}
        self.max_size = max_size

    def has_seen(self, key: str) -> bool:
        """Check if key has been seen"""
        return key in self.cache

    def mark_seen(self, key: str):
        """Mark key as seen"""
        self.cache[key] = datetime.utcnow().isoformat()

        # Prune old entries if too large
        if len(self.cache) > self.max_size:
            # Remove oldest 20%
            sorted_keys = sorted(self.cache.items(), key=lambda x: x[1])
            remove_count = self.max_size // 5
            for key, _ in sorted_keys[:remove_count]:
                del self.cache[key]

    def save_to_file(self, filepath: str):
        """Persist cache to file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.cache, f)
        except Exception as e:
            print(f"Failed to save cache: {e}")

    def load_from_file(self, filepath: str):
        """Load cache from file"""
        try:
            with open(filepath, 'r') as f:
                self.cache = json.load(f)
        except FileNotFoundError:
            self.cache = {}
        except Exception as e:
            print(f"Failed to load cache: {e}")
            self.cache = {}