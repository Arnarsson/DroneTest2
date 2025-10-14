import feedparser

feed = feedparser.parse("https://polisen.se/aktuellt/rss/stockholms-lan/handelser-rss---stockholms-lan/")
print(f"Total entries: {len(feed.entries)}")
print("\nFirst 5 entries:")
for entry in feed.entries[:5]:
    print(f"- {entry.title}")
    print(f"  Published: {entry.get('published', 'N/A')}")
    print()
