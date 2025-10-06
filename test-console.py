#!/usr/bin/env python3
"""Capture console logs from production site"""

from playwright.sync_api import sync_playwright
import time

def capture_console_logs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        console_logs = []

        # Capture console messages
        def handle_console(msg):
            log_entry = f"[{msg.type}] {msg.text}"
            console_logs.append(log_entry)
            print(log_entry)

        page.on("console", handle_console)

        print("Opening https://dronez-31pn88qy1-arnarssons-projects.vercel.app...")
        page.goto("https://dronez-31pn88qy1-arnarssons-projects.vercel.app", wait_until="networkidle")

        # Wait for data to load
        print("\nWaiting 5 seconds for data to load...\n")
        time.sleep(5)

        # Check what's on the page
        print("\n=== PAGE CONTENT ===")

        # Try to find incident count in header
        try:
            header_text = page.locator('header').inner_text()
            print(f"Header text: {header_text}")
        except:
            print("Could not read header")

        # Check for "No incidents found" message
        try:
            no_incidents = page.locator('text=No incidents found').count()
            print(f"\n'No incidents found' messages: {no_incidents}")
        except:
            pass

        # Check for map markers
        try:
            markers = page.locator('.leaflet-marker-icon').count()
            print(f"Map markers: {markers}")
        except:
            print("Could not count map markers")

        print("\n=== CONSOLE LOGS ===")
        for log in console_logs:
            print(log)

        browser.close()

if __name__ == "__main__":
    capture_console_logs()
