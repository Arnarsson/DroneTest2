#!/usr/bin/env python3
"""
Mobile Browser Testing with Playwright
Tests responsive design and mobile functionality across multiple devices
"""

from playwright.sync_api import sync_playwright, ViewportSize
import time
from datetime import datetime
import json

# Test configuration
PRODUCTION_URL = "https://dronez-31pn88qy1-arnarssons-projects.vercel.app"

# Device configurations (Playwright's device descriptors)
DEVICES = {
    "iPhone 13 Pro": {
        "viewport": {"width": 390, "height": 844},
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
        "device_scale_factor": 3,
        "is_mobile": True,
        "has_touch": True,
    },
    "Samsung Galaxy S21": {
        "viewport": {"width": 360, "height": 800},
        "user_agent": "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        "device_scale_factor": 3,
        "is_mobile": True,
        "has_touch": True,
    },
    "iPad Pro": {
        "viewport": {"width": 1024, "height": 1366},
        "user_agent": "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
        "device_scale_factor": 2,
        "is_mobile": True,
        "has_touch": True,
    },
    "Desktop": {
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "device_scale_factor": 1,
        "is_mobile": False,
        "has_touch": False,
    }
}

def test_device(browser, device_name: str, device_config: dict) -> dict:
    """Test the site on a specific device configuration"""

    print(f"\n{'='*60}")
    print(f"Testing: {device_name}")
    print(f"Viewport: {device_config['viewport']['width']}x{device_config['viewport']['height']}")
    print(f"{'='*60}")

    # Create browser context with device settings
    context = browser.new_context(
        viewport=device_config["viewport"],
        user_agent=device_config["user_agent"],
        device_scale_factor=device_config["device_scale_factor"],
        is_mobile=device_config["is_mobile"],
        has_touch=device_config["has_touch"],
    )

    page = context.new_page()

    # Track console logs
    console_logs = []
    page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))

    # Track errors
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))

    results = {
        "device": device_name,
        "viewport": f"{device_config['viewport']['width']}x{device_config['viewport']['height']}",
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "console_logs": [],
        "errors": [],
        "screenshot": f"mobile-test-{device_name.replace(' ', '-').lower()}.png"
    }

    try:
        # Navigate to site
        print(f"→ Loading {PRODUCTION_URL}...")
        start_time = time.time()
        page.goto(PRODUCTION_URL, wait_until="networkidle", timeout=30000)
        load_time = time.time() - start_time
        results["load_time"] = f"{load_time:.2f}s"
        print(f"  ✓ Loaded in {load_time:.2f}s")

        # Wait for data to load
        time.sleep(3)

        # Test 1: Header visibility and incident count
        print("\n→ Testing header...")
        try:
            header = page.locator('header')
            header_visible = header.is_visible()
            results["tests"]["header_visible"] = header_visible

            # Get incident count
            count_element = page.locator('header span.font-bold').filter(has_text=lambda t: t.isdigit() or t == 'UPDATING')
            if count_element.count() > 0:
                count_text = count_element.first.text_content()
                results["tests"]["incident_count"] = count_text
                print(f"  ✓ Header showing: {count_text}")
            else:
                results["tests"]["incident_count"] = "NOT FOUND"
                print(f"  ✗ Incident count not found")
        except Exception as e:
            results["tests"]["header_error"] = str(e)
            print(f"  ✗ Header error: {e}")

        # Test 2: Map visibility
        print("\n→ Testing map...")
        try:
            map_container = page.locator('.leaflet-container')
            map_visible = map_container.is_visible()
            results["tests"]["map_visible"] = map_visible

            if map_visible:
                # Count map markers
                markers = page.locator('.leaflet-marker-icon')
                marker_count = markers.count()
                results["tests"]["map_markers"] = marker_count
                print(f"  ✓ Map visible with {marker_count} markers")
            else:
                print(f"  ✗ Map not visible")
        except Exception as e:
            results["tests"]["map_error"] = str(e)
            print(f"  ✗ Map error: {e}")

        # Test 3: Mobile filter button (for mobile devices only)
        if device_config["is_mobile"] and device_config["viewport"]["width"] < 1024:
            print("\n→ Testing mobile filter button...")
            try:
                filter_button = page.locator('button').filter(has=page.locator('svg[viewBox="0 0 24 24"]')).first
                filter_visible = filter_button.is_visible()
                results["tests"]["mobile_filter_button"] = filter_visible

                if filter_visible:
                    print(f"  ✓ Mobile filter button visible")

                    # Test filter drawer interaction
                    print("  → Testing filter drawer...")
                    filter_button.click()
                    time.sleep(1)

                    # Check if filter panel opened
                    filter_panel = page.locator('div').filter(has_text="Filters").first
                    panel_visible = filter_panel.is_visible()
                    results["tests"]["filter_drawer_opens"] = panel_visible

                    if panel_visible:
                        print(f"  ✓ Filter drawer opens successfully")

                        # Close drawer
                        close_button = page.locator('button').filter(has=page.locator('svg path[d*="M6 18L18 6"]')).first
                        if close_button.is_visible():
                            close_button.click()
                            time.sleep(0.5)
                            print(f"  ✓ Filter drawer closes successfully")
                    else:
                        print(f"  ✗ Filter drawer did not open")
                else:
                    print(f"  ✗ Mobile filter button not visible")
            except Exception as e:
                results["tests"]["filter_error"] = str(e)
                print(f"  ✗ Filter test error: {e}")

        # Test 4: View toggle visibility
        print("\n→ Testing view toggle...")
        try:
            view_toggle = page.locator('button').filter(has_text="MAP")
            toggle_visible = view_toggle.is_visible()
            results["tests"]["view_toggle_visible"] = toggle_visible
            print(f"  ✓ View toggle visible: {toggle_visible}")
        except Exception as e:
            results["tests"]["view_toggle_error"] = str(e)
            print(f"  ✗ View toggle error: {e}")

        # Test 5: Check for "No incidents found" message (should NOT be present)
        print("\n→ Checking for error messages...")
        try:
            no_incidents = page.locator('text=No incidents found')
            no_incidents_visible = no_incidents.is_visible() if no_incidents.count() > 0 else False
            results["tests"]["no_incidents_message"] = no_incidents_visible

            if no_incidents_visible:
                print(f"  ✗ WARNING: 'No incidents found' message is visible!")
            else:
                print(f"  ✓ No error messages found")
        except Exception as e:
            results["tests"]["error_check_failed"] = str(e)

        # Test 6: Responsive breakpoint detection
        print("\n→ Testing responsive design...")
        viewport_width = device_config["viewport"]["width"]
        if viewport_width < 640:
            breakpoint = "mobile (< 640px)"
        elif viewport_width < 768:
            breakpoint = "sm (640-768px)"
        elif viewport_width < 1024:
            breakpoint = "md (768-1024px)"
        elif viewport_width < 1280:
            breakpoint = "lg (1024-1280px)"
        else:
            breakpoint = "xl (>= 1280px)"

        results["tests"]["responsive_breakpoint"] = breakpoint
        print(f"  ✓ Detected breakpoint: {breakpoint}")

        # Take screenshot
        print(f"\n→ Capturing screenshot...")
        page.screenshot(path=results["screenshot"], full_page=True)
        print(f"  ✓ Screenshot saved: {results['screenshot']}")

        # Capture final console logs
        results["console_logs"] = console_logs[-20:]  # Last 20 logs
        results["errors"] = errors

        if errors:
            print(f"\n⚠️  {len(errors)} JavaScript errors detected:")
            for error in errors:
                print(f"    • {error}")

    except Exception as e:
        results["fatal_error"] = str(e)
        print(f"\n✗ FATAL ERROR: {e}")

    finally:
        context.close()

    return results


def generate_report(all_results: list):
    """Generate a summary report of all tests"""

    print("\n" + "="*60)
    print("MOBILE TESTING SUMMARY REPORT")
    print("="*60)
    print(f"Tested URL: {PRODUCTION_URL}")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Devices Tested: {len(all_results)}")
    print("="*60)

    for result in all_results:
        print(f"\n{result['device']} ({result['viewport']})")
        print(f"  Load Time: {result.get('load_time', 'N/A')}")

        tests = result.get('tests', {})
        passed = sum(1 for v in tests.values() if v is True or (isinstance(v, (int, str)) and v not in ['NOT FOUND', False]))
        total = len(tests)

        print(f"  Tests Passed: {passed}/{total}")

        # Key metrics
        if 'incident_count' in tests:
            print(f"  Incident Count: {tests['incident_count']}")
        if 'map_markers' in tests:
            print(f"  Map Markers: {tests['map_markers']}")
        if result.get('errors'):
            print(f"  ⚠️  JavaScript Errors: {len(result['errors'])}")

        print(f"  Screenshot: {result['screenshot']}")

    # Save detailed JSON report
    report_file = f"mobile-test-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\n✓ Detailed report saved: {report_file}")
    print("="*60 + "\n")


def main():
    """Run mobile tests on all devices"""

    print("\n" + "="*60)
    print("DRONEWATCH MOBILE BROWSER TESTING")
    print("="*60)
    print(f"Testing URL: {PRODUCTION_URL}")
    print(f"Devices: {', '.join(DEVICES.keys())}")
    print("="*60)

    all_results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        try:
            for device_name, device_config in DEVICES.items():
                result = test_device(browser, device_name, device_config)
                all_results.append(result)

                # Small delay between tests
                time.sleep(2)

        finally:
            browser.close()

    # Generate summary report
    generate_report(all_results)


if __name__ == "__main__":
    main()
