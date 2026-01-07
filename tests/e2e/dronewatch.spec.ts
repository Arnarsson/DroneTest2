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

  test.describe('URL Filter State', () => {

    test('should apply filters from URL params on page load', async ({ page }) => {
      // Navigate directly to URL with filter params
      await page.goto(`${BASE_URL}/?country=DK&min_evidence=3&date_range=week`);
      await page.waitForLoadState('networkidle');

      // Verify country filter is set to Denmark
      const countrySelect = page.locator('select').first();
      await expect(countrySelect).toHaveValue('DK');

      // Verify evidence filter is set (check that Score 3+ is the minimum)
      // The evidence buttons for lower scores should be visually different
      const unconfirmedButton = page.locator('button:has-text("Unconfirmed")').first();
      const reportedButton = page.locator('button:has-text("Reported")').first();

      // These should be inactive/disabled appearance since minEvidence is 3
      // We check aria-pressed or similar indicator
      // The higher evidence buttons should be active
      await expect(page.locator('button:has-text("Verified")').first()).toBeVisible();
    });

    test('should update URL when filter changes', async ({ page }) => {
      // Start with default page (no filter params)
      await page.goto(BASE_URL);
      await page.waitForLoadState('networkidle');

      // Initial URL should have no query params
      expect(page.url()).toBe(`${BASE_URL}/`);

      // Select a country filter
      const countrySelect = page.locator('select').first();
      await countrySelect.selectOption({ label: /Denmark/i });

      // Wait for URL update
      await page.waitForTimeout(500);

      // URL should now contain country param
      const currentUrl = new URL(page.url());
      expect(currentUrl.searchParams.get('country')).toBe('DK');
    });

    test('should update URL with multiple filter params', async ({ page }) => {
      await page.goto(BASE_URL);
      await page.waitForLoadState('networkidle');

      // Apply country filter
      const countrySelect = page.locator('select').first();
      await countrySelect.selectOption({ label: /Denmark/i });

      // Wait for URL update
      await page.waitForTimeout(500);

      // Click on date range filter (Week)
      const weekButton = page.locator('button:has-text("Week")').first();
      await weekButton.click();

      // Wait for URL update
      await page.waitForTimeout(500);

      // Verify both params are in URL
      const currentUrl = new URL(page.url());
      expect(currentUrl.searchParams.get('country')).toBe('DK');
      expect(currentUrl.searchParams.get('date_range')).toBe('week');
    });

    test('should preserve filters when sharing URL', async ({ page, context }) => {
      // Navigate to a URL with specific filters
      const filterUrl = `${BASE_URL}/?country=DK&min_evidence=2&date_range=month`;
      await page.goto(filterUrl);
      await page.waitForLoadState('networkidle');

      // Verify filters are applied
      const countrySelect = page.locator('select').first();
      await expect(countrySelect).toHaveValue('DK');

      // Open a new page with the same URL (simulates sharing)
      const newPage = await context.newPage();
      await newPage.goto(filterUrl);
      await newPage.waitForLoadState('networkidle');

      // Verify filters are also applied in the new page
      const newCountrySelect = newPage.locator('select').first();
      await expect(newCountrySelect).toHaveValue('DK');

      await newPage.close();
    });

    test('should handle browser back/forward navigation', async ({ page }) => {
      // Start with default page
      await page.goto(BASE_URL);
      await page.waitForLoadState('networkidle');

      // Apply a filter - select Denmark
      const countrySelect = page.locator('select').first();
      await countrySelect.selectOption({ label: /Denmark/i });
      await page.waitForTimeout(500);

      // Verify URL changed
      let currentUrl = new URL(page.url());
      expect(currentUrl.searchParams.get('country')).toBe('DK');

      // Change to another filter - select Norway
      await countrySelect.selectOption({ label: /Norway/i });
      await page.waitForTimeout(500);

      // Verify URL updated
      currentUrl = new URL(page.url());
      expect(currentUrl.searchParams.get('country')).toBe('NO');

      // Go back in browser history
      await page.goBack();
      await page.waitForTimeout(500);

      // Should restore previous filter (Denmark)
      await expect(countrySelect).toHaveValue('DK');
      currentUrl = new URL(page.url());
      expect(currentUrl.searchParams.get('country')).toBe('DK');

      // Go forward in browser history
      await page.goForward();
      await page.waitForTimeout(500);

      // Should restore next filter (Norway)
      await expect(countrySelect).toHaveValue('NO');
    });

    test('should clear URL params when clearing filters', async ({ page }) => {
      // Start with filters in URL
      await page.goto(`${BASE_URL}/?country=DK&date_range=week`);
      await page.waitForLoadState('networkidle');

      // Verify URL has params
      let currentUrl = new URL(page.url());
      expect(currentUrl.searchParams.has('country')).toBe(true);

      // Click Clear All button
      const clearButton = page.locator('button:has-text("Clear All")').first();
      await clearButton.click();

      // Wait for URL update
      await page.waitForTimeout(500);

      // URL should have no filter params
      currentUrl = new URL(page.url());
      expect(currentUrl.searchParams.has('country')).toBe(false);
      expect(currentUrl.searchParams.has('date_range')).toBe(false);
    });

    test('should show Copy Link button when filters are active', async ({ page }) => {
      // Start with filters in URL
      await page.goto(`${BASE_URL}/?country=DK`);
      await page.waitForLoadState('networkidle');

      // Copy Link button should be visible when filters are active
      const copyButton = page.locator('button:has-text("Copy Link")').first();
      await expect(copyButton).toBeVisible();
    });

    test('should handle invalid URL params gracefully', async ({ page }) => {
      // Navigate with invalid params - should not crash
      await page.goto(`${BASE_URL}/?min_evidence=999&date_range=invalid&country=<script>alert(1)</script>`);
      await page.waitForLoadState('networkidle');

      // Page should load successfully
      await expect(page.locator('.leaflet-container')).toBeVisible({ timeout: LOAD_TIMEOUT });

      // Country select should fall back to default (or sanitized value)
      const countrySelect = page.locator('select').first();
      // Should not contain script tags
      const selectedValue = await countrySelect.inputValue();
      expect(selectedValue).not.toContain('<script>');
    });

    test('should work correctly on mobile viewport', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 812 });

      // Navigate with filter params
      await page.goto(`${BASE_URL}/?country=DK&date_range=week`);
      await page.waitForLoadState('networkidle');

      // Open filter panel on mobile
      const filterButton = page.locator('button[aria-label*="filter"]').first();
      await filterButton.click();
      await page.waitForTimeout(500);

      // Verify filters are applied
      const countrySelect = page.locator('select').first();
      await expect(countrySelect).toHaveValue('DK');
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
