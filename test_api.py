#!/usr/bin/env python3
"""Test API endpoints and diagnose issues"""
import requests
import json

API_BASE = "https://dronewatchv2.vercel.app/api"

def test_endpoint(name, url):
    print(f"\nTesting {name}: {url}")
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)[:500]}")
        else:
            print(f"Error: {response.text[:500]}")
    except Exception as e:
        print(f"Exception: {e}")

# Test endpoints
test_endpoint("Root", f"{API_BASE}/")
test_endpoint("Health", f"{API_BASE}/healthz")
test_endpoint("Incidents", f"{API_BASE}/incidents")

print("\n" + "="*50)
print("Frontend URL: https://dronewatchv2.vercel.app/")
print("API URL: https://dronewatchv2.vercel.app/api")
print("\nTo debug with Chrome DevTools:")
print("1. Open https://dronewatchv2.vercel.app/ in Chrome")
print("2. Press F12 to open DevTools")
print("3. Go to Network tab")
print("4. Look for failed API requests")
print("5. Check Console tab for JavaScript errors")