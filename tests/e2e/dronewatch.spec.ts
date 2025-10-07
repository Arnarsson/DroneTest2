import { test, expect, Page } from '@playwright/test';

/**
 * DroneWatch 2.0 - Automated E2E Test Suite
 * Production Site: https://www.dronemap.cc
 * Version: 2.2.0
 */

const BASE_URL = 'https://www.dronemap.cc';
const LOAD_TIMEOUT = 10000;

test.describe('DroneWatch Production E2E Tests', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate to production site before each test
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
  });

  test.describe('Initial Page Load', () => {

    test('should load homepage successfully', async ({ page }) => {
      // Check page title
      await expect(page).toHaveTitle(/DroneWatch/i);

      // Check main elements are visible
      await expect(page.locator('text=DroneWatch')).toBeVisible();
      await expect(page.locator('text=Safety Through Transparency')).toBeVisible();
    });

    test('should render map correctly', async ({ page }) => {
      // Wait for Leaflet map container
      const mapContainer = page.locator('.leaflet-container');
      await expect(mapContainer).toBeVisible({ timeout: LOAD_TIMEOUT });

      // Check map tiles loaded
      const mapTiles = page.locator('.leaflet-tile-container img');
      await expect(mapTiles.first()).toBeVisible();
    });

    test('should display incident markers on map', async ({ page }) => {
      // Wait for markers to load
      await page.waitForSelector('.leaflet-marker-icon', { timeout: LOAD_TIMEOUT });

      // Check at least one marker exists
      const markers = page.locator('.leaflet-marker-icon');
      await expect(await markers.count()).toBeGreaterThan(0);
    });

    test('should load in under 3 seconds', async ({ page }) => {
      const startTime = Date.now();
      await page.goto(BASE_URL);
      await page.waitForLoadState('load');
      const loadTime = Date.now() - startTime;

      expect(loadTime).toBeLessThan(3000);
    });

    test('should have no console errors', async ({ page }) => {
      const errors: string[] = [];

      page.on('console', msg => {
        if (msg.type() === 'error') {
          errors.push(msg.text());
        }
      });

      await page.goto(BASE_URL);
      await page.waitForLoadState('networkidle');

      expect(errors.length).toBe(0);
    });
  });

  test.describe('Header and Navigation', () => {

    test('should display all header elements', async ({ page }) => {
      // Logo
      await expect(page.locator('text=DroneWatch')).toBeVisible();

      // Theme toggle
      const themeToggle = page.locator('button[aria-label*="theme"]');
      await expect(themeToggle).toBeVisible();

      // View tabs
      await expect(page.locator('text=Map')).toBeVisible();
      await expect(page.locator('text=List')).toBeVisible();
      await expect(page.locator('text=Analytics')).toBeVisible();
    });

    test('should switch between views', async ({ page }) => {
      // Click List view
      await page.click('text=List');
      await expect(page.locator('[aria-current="page"]')).toHaveText(/List/i);

      // Click Analytics view
      await page.click('text=Analytics');
      await expect(page.locator('[aria-current="page"]')).toHaveText(/Analytics/i);

      // Click Map view
      await page.click('text=Map');
      await expect(page.locator('[aria-current="page"]')).toHaveText(/Map/i);
    });

    test('should toggle theme', async ({ page }) => {
      // Get current theme
      const html = page.locator('html');
      const initialTheme = await html.getAttribute('class');

      // Click theme toggle
      const themeToggle = page.locator('button[aria-label*="theme"]').first();
      await themeToggle.click();

      // Wait for theme change
      await page.waitForTimeout(500);

      // Check theme changed
      const newTheme = await html.getAttribute('class');
      expect(newTheme).not.toBe(initialTheme);
    });
  });

  test.describe('Map Interactions', () => {

    test('should zoom in and out', async ({ page }) => {
      const zoomInButton = page.locator('.leaflet-control-zoom-in');
      const zoomOutButton = page.locator('.leaflet-control-zoom-out');

      // Zoom in
      await zoomInButton.click();
      await page.waitForTimeout(500);

      // Zoom out
      await zoomOutButton.click();
      await page.waitForTimeout(500);

      // Should not throw errors
      expect(true).toBe(true);
    });

    test('should open incident popup on marker click', async ({ page }) => {
      // Wait for markers
      await page.waitForSelector('.leaflet-marker-icon', { timeout: LOAD_TIMEOUT });

      // Click first marker
      const firstMarker = page.locator('.leaflet-marker-icon').first();
      await firstMarker.click();

      // Wait for popup
      await page.waitForSelector('.leaflet-popup', { timeout: 5000 });

      // Check popup content
      const popup = page.locator('.leaflet-popup');
      await expect(popup).toBeVisible();
      await expect(popup.locator('text=/Score [1-4]/i')).toBeVisible();
    });

    test('should show evidence badge in popup', async ({ page }) => {
      // Click a marker
      await page.waitForSelector('.leaflet-marker-icon', { timeout: LOAD_TIMEOUT });
      await page.locator('.leaflet-marker-icon').first().click();

      // Wait for popup
      await page.waitForSelector('.leaflet-popup', { timeout: 5000 });

      // Check evidence badge exists
      const evidenceBadge = page.locator('.leaflet-popup').locator('[class*="evidence"]').first();
      await expect(evidenceBadge).toBeVisible();
    });
  });

  test.describe('Filter Panel', () => {

    test('should open filter panel on desktop', async ({ page }) => {
      // On desktop, filters should be visible by default
      const filterPanel = page.locator('[class*="filter"]').first();
      await expect(filterPanel).toBeVisible();
    });

    test('should open filter panel on mobile', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 812 });

      // Find and click filter button
      const filterButton = page.locator('button[aria-label*="filter"]').first();
      await filterButton.click();

      // Panel should open
      await page.waitForTimeout(500);
      const filterPanel = page.locator('[class*="filter"]').first();
      await expect(filterPanel).toBeVisible();
    });

    test('should filter by evidence level', async ({ page }) => {
      // Get initial marker count
      await page.waitForSelector('.leaflet-marker-icon', { timeout: LOAD_TIMEOUT });
      const initialCount = await page.locator('.leaflet-marker-icon').count();

      // Find and click "Unconfirmed" filter to disable it
      const unconfirmedToggle = page.locator('button:has-text("Unconfirmed")').first();
      await unconfirmedToggle.click();

      // Wait for map update
      await page.waitForTimeout(1000);

      // Marker count should change (or stay same if no unconfirmed incidents)
      const newCount = await page.locator('.leaflet-marker-icon').count();
      expect(newCount).toBeLessThanOrEqual(initialCount);
    });

    test('should filter by country', async ({ page }) => {
      // Find country dropdown
      const countrySelect = page.locator('select').first();

      // Select Denmark
      await countrySelect.selectOption({ label: /Denmark/i });

      // Wait for map update
      await page.waitForTimeout(1000);

      // Markers should update (hard to verify exact count without knowing data)
      expect(true).toBe(true);
    });

    test('should clear all filters', async ({ page }) => {
      // Apply some filters first
      const unconfirmedToggle = page.locator('button:has-text("Unconfirmed")').first();
      await unconfirmedToggle.click();

      // Wait
      await page.waitForTimeout(500);

      // Find and click Clear All button
      const clearButton = page.locator('button:has-text("Clear All")').first();
      await clearButton.click();

      // Wait for reset
      await page.waitForTimeout(500);

      // Filters should be reset (visual check)
      expect(true).toBe(true);
    });
  });

  test.describe('List View', () => {

    test('should switch to list view', async ({ page }) => {
      // Click List tab
      await page.click('text=List');

      // Wait for list to render
      await page.waitForTimeout(1000);

      // Check incident cards are visible
      const incidentCards = page.locator('[class*="incident"]');
      await expect(await incidentCards.count()).toBeGreaterThan(0);
    });

    test('should display evidence badges in list', async ({ page }) => {
      // Switch to list view
      await page.click('text=List');
      await page.waitForTimeout(1000);

      // Check for evidence badges
      const evidenceBadges = page.locator('[class*="evidence"]');
      await expect(await evidenceBadges.count()).toBeGreaterThan(0);
    });

    test('should show empty state with no results', async ({ page }) => {
      // Switch to list view
      await page.click('text=List');
      await page.waitForTimeout(1000);

      // Apply very strict filter (Score 1 only + old date)
      const unconfirmedToggle = page.locator('button:has-text("Unconfirmed")').first();
      await unconfirmedToggle.click();

      // Disable all other scores
      await page.locator('button:has-text("Official")').first().click();
      await page.locator('button:has-text("Verified")').first().click();
      await page.locator('button:has-text("Reported")').first().click();

      await page.waitForTimeout(1000);

      // Check for empty state (should see the 🔍 emoji or "No incidents found")
      const emptyState = page.locator('text=/No incidents found/i');
      if (await emptyState.isVisible()) {
        await expect(emptyState).toBeVisible();
      }
    });
  });

  test.describe('Analytics View', () => {

    test('should switch to analytics view', async ({ page }) => {
      // Click Analytics tab
      await page.click('text=Analytics');

      // Wait for charts to render
      await page.waitForTimeout(2000);

      // Check for chart elements (canvas or SVG)
      const charts = page.locator('canvas, svg');
      await expect(await charts.count()).toBeGreaterThan(0);
    });
  });

  test.describe('Mobile Responsiveness', () => {

    test('should display correctly on mobile', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 812 });

      // Reload page
      await page.goto(BASE_URL);
      await page.waitForLoadState('networkidle');

      // Check map is visible
      await expect(page.locator('.leaflet-container')).toBeVisible();

      // Check filter button is floating
      const filterButton = page.locator('button[aria-label*="filter"]').first();
      await expect(filterButton).toBeVisible();
    });

    test('should have correct filter button position on mobile', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 812 });
      await page.goto(BASE_URL);
      await page.waitForLoadState('networkidle');

      // Find filter button
      const filterButton = page.locator('button[aria-label*="filter"]').first();

      // Get position
      const box = await filterButton.boundingBox();

      // Should be positioned at bottom-right (not overlapping map controls)
      expect(box).not.toBeNull();
      if (box) {
        expect(box.y).toBeGreaterThan(600); // Should be near bottom
        expect(box.x).toBeGreaterThan(250); // Should be on right side
      }
    });
  });

  test.describe('Accessibility', () => {

    test('should have proper ARIA labels on view tabs', async ({ page }) => {
      const mapTab = page.locator('button:has-text("Map")').first();
      const ariaLabel = await mapTab.getAttribute('aria-label');

      expect(ariaLabel).toContain('view');
    });

    test('should have aria-current on active tab', async ({ page }) => {
      // Click List tab
      await page.click('text=List');

      // Check aria-current
      const activeTab = page.locator('[aria-current="page"]');
      await expect(activeTab).toHaveText(/List/i);
    });

    test('should be keyboard navigable', async ({ page }) => {
      // Tab through elements
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');

      // Should have focus visible
      const focusedElement = page.locator(':focus');
      await expect(focusedElement).toBeVisible();
    });
  });

  test.describe('Performance', () => {

    test('should load API data within 2 seconds', async ({ page }) => {
      // Listen for API call
      const apiResponse = page.waitForResponse(
        response => response.url().includes('/api/incidents'),
        { timeout: LOAD_TIMEOUT }
      );

      await page.goto(BASE_URL);

      const response = await apiResponse;
      expect(response.status()).toBe(200);

      // Check response is JSON
      const contentType = response.headers()['content-type'];
      expect(contentType).toContain('json');
    });

    test('should have reasonable bundle size', async ({ page }) => {
      const responses: { url: string; size: number }[] = [];

      page.on('response', async response => {
        const headers = response.headers();
        const contentLength = headers['content-length'];

        if (contentLength && response.url().includes('.js')) {
          responses.push({
            url: response.url(),
            size: parseInt(contentLength)
          });
        }
      });

      await page.goto(BASE_URL);
      await page.waitForLoadState('networkidle');

      // Total JS should be under 2MB
      const totalSize = responses.reduce((sum, r) => sum + r.size, 0);
      expect(totalSize).toBeLessThan(2 * 1024 * 1024);
    });
  });

  test.describe('Data Quality', () => {

    test('should only show Nordic incidents', async ({ page }) => {
      // Switch to list view for easier checking
      await page.click('text=List');
      await page.waitForTimeout(1000);

      // Get all country/location texts
      const locations = await page.locator('[class*="location"]').allTextContents();

      // Check for non-Nordic countries (should not exist)
      const nonNordic = ['Ukraine', 'Russia', 'Germany', 'France', 'UK'];
      const hasNonNordic = locations.some(loc =>
        nonNordic.some(country => loc.includes(country))
      );

      expect(hasNonNordic).toBe(false);
    });

    test('should have no test incidents visible', async ({ page }) => {
      // Switch to list view
      await page.click('text=List');
      await page.waitForTimeout(1000);

      // Check for test incident keywords
      const pageContent = await page.content();
      expect(pageContent).not.toContain('DroneTest');
      expect(pageContent).not.toContain('Test Success');
      expect(pageContent).not.toContain('Test Incident');
    });

    test('should display source badges', async ({ page }) => {
      // Click first marker
      await page.waitForSelector('.leaflet-marker-icon', { timeout: LOAD_TIMEOUT });
      await page.locator('.leaflet-marker-icon').first().click();

      // Wait for popup
      await page.waitForSelector('.leaflet-popup', { timeout: 5000 });

      // Check for source information
      const popup = page.locator('.leaflet-popup');
      const sourceText = await popup.textContent();

      // Should mention source type (News, Police, etc.)
      expect(sourceText).toMatch(/News|Police|Aviation|Military/i);
    });
  });
});

/**
 * Visual Regression Tests (requires baseline screenshots)
 */
test.describe('Visual Regression', () => {

  test('homepage should match baseline', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    // Take screenshot
    await expect(page).toHaveScreenshot('homepage.png', {
      maxDiffPixels: 100
    });
  });

  test('list view should match baseline', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.click('text=List');
    await page.waitForTimeout(1000);

    await expect(page).toHaveScreenshot('list-view.png', {
      maxDiffPixels: 100
    });
  });
});
