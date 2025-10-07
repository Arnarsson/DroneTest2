#!/usr/bin/env python3
"""
Test script for Danish police HTML scraping
"""
import requests
import json
import re
from bs4 import BeautifulSoup

url = "https://politi.dk/nyhedsliste"
params = {
    'fromDate': '2025/9/2',
    'toDate': '2025/10/7',
    'newsType': 'Alle',
    'page': 1,
    'district': 'Koebenhavns-Politi'
}

print("Fetching page...")
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'da,en-US;q=0.7,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}
response = requests.get(url, params=params, headers=headers, timeout=15)
print(f"Status: {response.status_code}")

html_content = response.text

# Extract JSON from ng-init
print("\nSearching for ng-init...")
ng_init_pattern = r'ng-init="init\(({.*?})\)"'
match = re.search(ng_init_pattern, html_content, re.DOTALL)

if not match:
    print("❌ No ng-init found!")
    print("\nSearching for 'ng-init' in HTML...")
    if 'ng-init' in html_content:
        print("✓ ng-init exists in HTML")
        # Find the section
        start = html_content.find('ng-init')
        print(f"First occurrence at position {start}")
        print(html_content[start:start+200])
    else:
        print("❌ No ng-init at all in HTML")
else:
    print("✓ Found ng-init JSON!")
    json_str = match.group(1)
    print(f"\nJSON length: {len(json_str)} characters")

    # Decode HTML entities
    json_str = json_str.replace('&quot;', '"').replace('&amp;', '&').replace('&#248;', 'ø').replace('&#229;', 'å').replace('&#230;', 'æ')

    try:
        data = json.loads(json_str)
        print("✓ JSON parsed successfully!")

        news_list = data.get('AllNews', {}).get('NewsList', [])
        print(f"\nFound {len(news_list)} news items:")

        for i, item in enumerate(news_list[:3]):
            print(f"\n{i+1}. {item.get('Headline', 'No headline')}")
            print(f"   Link: {item.get('Link', 'No link')}")
            print(f"   Summary: {item.get('Manchet', 'No summary')[:100]}...")

    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error: {e}")
        print(f"First 500 chars of JSON string:")
        print(json_str[:500])
