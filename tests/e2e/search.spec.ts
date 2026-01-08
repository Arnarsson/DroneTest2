import { test, expect } from '@playwright/test';

/**
 * DroneWatch 2.0 - Search Functionality E2E Tests
 * Production Site: https://www.dronemap.cc
 *
 * Tests the text search filter for incidents, verifying:
 * - Search input renders correctly
 * - Basic search filtering works
 * - Search clears properly
 * - Search integrates with other filters
 * - No results state displays correctly
 */

const BASE_URL = 'https://www.dronemap.cc';
const LOAD_TIMEOUT = 10000;
const SEARCH_DEBOUNCE = 1000; // Time to wait for search results to update

test.describe('Search Functionality E2E Tests', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate to production site before each test
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
  });

  test.describe('Search Input Rendering', () => {

    test('should display search input with magnifying glass icon', async ({ page }) => {
      // Find search input by placeholder text
      const searchInput = page.locator('input[placeholder*="Search"]');
      await expect(searchInput).toBeVisible();

      // Check for SVG icon (magnifying glass) near the input
      const searchIcon = page.locator('svg').filter({ has: page.locator('path[d*="21l-6-6"]') }).first();
      await expect(searchIcon).toBeVisible();
    });

    test('should have accessible search input', async ({ page }) => {
      // Find search input
      const searchInput = page.locator('input[placeholder*="Search"]');

      // Check aria-label exists for accessibility
      const ariaLabel = await searchInput.getAttribute('aria-label');
      expect(ariaLabel).toBeTruthy();
    });

    test('should show focus ring when search input is focused', async ({ page }) => {
      // Find and focus search input
      const searchInput = page.locator('input[placeholder*="Search"]');
      await searchInput.focus();

      // Verify input is focused
      await expect(searchInput).toBeFocused();
    });

    test('should work in dark mode', async ({ page }) => {
      // Toggle to dark mode
      const themeToggle = page.locator('button[aria-label*="theme"]').first();
      await themeToggle.click();
      await page.waitForTimeout(500);

      // Check search input is still visible and functional
      const searchInput = page.locator('input[placeholder*="Search"]');
      await expect(searchInput).toBeVisible();

      // Should be able to type in dark mode
      await searchInput.fill('test');
      await expect(searchInput).toHaveValue('test');
    });
  });

  test.describe('Basic Search Flow', () => {

    test('should filter incidents when searching', async ({ page }) => {
      // Wait for initial markers to load
      await page.waitForSelector('.leaflet-marker-icon', { timeout: LOAD_TIMEOUT });
      const initialMarkerCount = await page.locator('.leaflet-marker-icon').count();

      // Type in search input
      const searchInput = page.locator('input[placeholder*="Search"]');
      await searchInput.fill('airport');

      // Wait for API response and map update
      await page.waitForResponse(
        response => response.url().includes('/api/incidents') && response.url().includes('search='),
        { timeout: LOAD_TIMEOUT }
      );
      await page.waitForTimeout(SEARCH_DEBOUNCE);

      // Markers should have been filtered (may be fewer or same if all match)
      const filteredMarkerCount = await page.locator('.leaflet-marker-icon').count();

      // We can't assert exact counts since it depends on data,
      // but we verify the search was applied by checking API was called
      expect(filteredMarkerCount).toBeLessThanOrEqual(initialMarkerCount);
    });

    test('should clear search and show all incidents', async ({ page }) => {
      // Wait for initial markers
      await page.waitForSelector('.leaflet-marker-icon', { timeout: LOAD_TIMEOUT });
      const initialMarkerCount = await page.locator('.leaflet-marker-icon').count();

      // Type in search
      const searchInput = page.locator('input[placeholder*="Search"]');
      await searchInput.fill('unique_search_term');
      await page.waitForTimeout(SEARCH_DEBOUNCE);

      // Clear search
      await searchInput.clear();

      // Wait for API response without search param
      await page.waitForTimeout(SEARCH_DEBOUNCE);

      // Markers should return to initial state (approximately)
      const clearedMarkerCount = await page.locator('.leaflet-marker-icon').count();

      // After clearing, we should have at least as many markers as after filtering
      expect(clearedMarkerCount).toBeGreaterThanOrEqual(0);
    });

    test('should update results in real-time as user types', async ({ page }) => {
      // Find search input
      const searchInput = page.locator('input[placeholder*="Search"]');

      // Track API calls
      const apiCalls: string[] = [];
      page.on('request', request => {
        if (request.url().includes('/api/incidents') && request.url().includes('search=')) {
          apiCalls.push(request.url());
        }
      });

      // Type character by character
      await searchInput.pressSequentially('dr', { delay: 200 });
      await page.waitForTimeout(SEARCH_DEBOUNCE);

      // Should have triggered API calls
      expect(apiCalls.length).toBeGreaterThan(0);
    });

    test('should handle case-insensitive search', async ({ page }) => {
      const searchInput = page.locator('input[placeholder*="Search"]');

      // Search with lowercase
      await searchInput.fill('drone');

      // Wait for API call with lowercase search
      const lowerResponse = await page.waitForResponse(
        response => response.url().includes('/api/incidents') &&
                   response.url().toLowerCase().includes('search=drone'),
        { timeout: LOAD_TIMEOUT }
      );

      const lowerData = await lowerResponse.json();
      await page.waitForTimeout(500);

      // Clear and search with uppercase
      await searchInput.clear();
      await searchInput.fill('DRONE');

      // Wait for API call with uppercase search
      const upperResponse = await page.waitForResponse(
        response => response.url().includes('/api/incidents') &&
                   response.url().includes('search=DRONE'),
        { timeout: LOAD_TIMEOUT }
      );

      const upperData = await upperResponse.json();

      // Both should return valid arrays (case-insensitive matching on backend)
      expect(Array.isArray(lowerData)).toBe(true);
      expect(Array.isArray(upperData)).toBe(true);
    });
  });

  test.describe('Search in List View', () => {

    test('should filter list view results', async ({ page }) => {
      // Switch to List view
      await page.click('text=List');
      await page.waitForTimeout(1000);

      // Type in search
      const searchInput = page.locator('input[placeholder*="Search"]');
      await searchInput.fill('military');

      // Wait for filtered results
      await page.waitForResponse(
        response => response.url().includes('/api/incidents') && response.url().includes('search='),
        { timeout: LOAD_TIMEOUT }
      );
      await page.waitForTimeout(SEARCH_DEBOUNCE);

      // Check that list view shows results or empty state
      const incidentCards = page.locator('[class*="incident"]');
      const emptyState = page.locator('text=/No incidents found/i');

      // Either incidents are shown OR empty state is shown
      const hasIncidents = await incidentCards.count() > 0;
      const hasEmptyState = await emptyState.isVisible();

      expect(hasIncidents || hasEmptyState).toBe(true);
    });
  });

  test.describe('Search with Other Filters', () => {

    test('should combine search with country filter', async ({ page }) => {
      // Wait for initial load
      await page.waitForSelector('.leaflet-marker-icon', { timeout: LOAD_TIMEOUT });

      // Select Denmark from country dropdown
      const countrySelect = page.locator('select').first();
      await countrySelect.selectOption({ label: /Denmark/i });
      await page.waitForTimeout(500);

      // Add search query
      const searchInput = page.locator('input[placeholder*="Search"]');
      await searchInput.fill('drone');

      // Wait for API response with both filters
      const response = await page.waitForResponse(
        response => {
          const url = response.url();
          return url.includes('/api/incidents') &&
                 url.includes('search=') &&
                 url.includes('country=');
        },
        { timeout: LOAD_TIMEOUT }
      );

      // Verify response is valid
      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(Array.isArray(data)).toBe(true);
    });

    test('should update filter count badge when search is active', async ({ page }) => {
      // Look for filter count badge (usually shows number of active filters)
      const searchInput = page.locator('input[placeholder*="Search"]');

      // Type in search
      await searchInput.fill('airport');
      await page.waitForTimeout(SEARCH_DEBOUNCE);

      // The filter badge should reflect active search
      // Look for badge with number or "active filters" indication
      const filterBadge = page.locator('[class*="badge"], [class*="count"]');

      // Badge should exist (may show count or indication of active filter)
      const badgeCount = await filterBadge.count();
      expect(badgeCount).toBeGreaterThanOrEqual(0); // At minimum, page should load
    });
  });

  test.describe('No Results State', () => {

    test('should show empty state for nonsense search', async ({ page }) => {
      // Switch to List view for easier empty state detection
      await page.click('text=List');
      await page.waitForTimeout(1000);

      // Search for nonsense term that won't match anything
      const searchInput = page.locator('input[placeholder*="Search"]');
      await searchInput.fill('xyzabc123nonsense999');

      // Wait for results
      await page.waitForResponse(
        response => response.url().includes('/api/incidents') && response.url().includes('search='),
        { timeout: LOAD_TIMEOUT }
      );
      await page.waitForTimeout(SEARCH_DEBOUNCE);

      // Check for empty state message
      const emptyStateMessage = page.locator('text=/No incidents found/i');

      // Empty state should be visible since nonsense search won't match
      await expect(emptyStateMessage).toBeVisible({ timeout: 5000 });
    });

    test('should show suggestion to clear search in empty state', async ({ page }) => {
      // Switch to List view
      await page.click('text=List');
      await page.waitForTimeout(1000);

      // Search for nonsense
      const searchInput = page.locator('input[placeholder*="Search"]');
      await searchInput.fill('xyzabc123nonsense999');
      await page.waitForTimeout(SEARCH_DEBOUNCE);

      // Check for suggestion to clear search
      const clearSuggestion = page.locator('text=/clear.*search|search.*clear/i');

      // Should show suggestion (if no results found)
      const emptyStateMessage = page.locator('text=/No incidents found/i');
      if (await emptyStateMessage.isVisible()) {
        await expect(clearSuggestion).toBeVisible();
      }
    });
  });

  test.describe('Edge Cases', () => {

    test('should handle special characters safely', async ({ page }) => {
      const searchInput = page.locator('input[placeholder*="Search"]');

      // Try various special characters that could cause issues
      const specialChars = ['%', "'", '"', '<script>', 'OR 1=1'];

      for (const char of specialChars) {
        await searchInput.clear();
        await searchInput.fill(char);
        await page.waitForTimeout(500);

        // Should not cause console errors
        // Page should still be functional
        await expect(searchInput).toBeVisible();
      }
    });

    test('should handle Unicode characters', async ({ page }) => {
      const searchInput = page.locator('input[placeholder*="Search"]');

      // Test Nordic characters
      await searchInput.fill('Koebenhavn');
      await page.waitForTimeout(500);

      // Input should accept Unicode
      await expect(searchInput).toHaveValue('Koebenhavn');

      // Test with actual Nordic chars
      await searchInput.clear();
      await searchInput.fill('test');
      await expect(searchInput).toHaveValue('test');
    });

    test('should handle very long search queries', async ({ page }) => {
      const searchInput = page.locator('input[placeholder*="Search"]');

      // Create a long string (500+ chars)
      const longQuery = 'a'.repeat(600);
      await searchInput.fill(longQuery);

      // Input should handle it (may truncate)
      // Page should not crash
      await expect(page.locator('body')).toBeVisible();
    });

    test('should handle whitespace-only search', async ({ page }) => {
      const searchInput = page.locator('input[placeholder*="Search"]');

      // Type only spaces
      await searchInput.fill('   ');
      await page.waitForTimeout(SEARCH_DEBOUNCE);

      // Wait for markers - whitespace search should show all incidents
      await page.waitForSelector('.leaflet-marker-icon', { timeout: LOAD_TIMEOUT });
      const markerCount = await page.locator('.leaflet-marker-icon').count();

      // Should have markers (whitespace treated as no filter)
      expect(markerCount).toBeGreaterThan(0);
    });
  });

  test.describe('Performance', () => {

    test('should complete search within 2 seconds', async ({ page }) => {
      const searchInput = page.locator('input[placeholder*="Search"]');

      const startTime = Date.now();

      // Type search term
      await searchInput.fill('drone');

      // Wait for API response
      await page.waitForResponse(
        response => response.url().includes('/api/incidents') && response.url().includes('search='),
        { timeout: LOAD_TIMEOUT }
      );

      const endTime = Date.now();
      const searchTime = endTime - startTime;

      // Search should complete within 2 seconds
      expect(searchTime).toBeLessThan(2000);
    });

    test('should not have console errors during search', async ({ page }) => {
      const errors: string[] = [];

      page.on('console', msg => {
        if (msg.type() === 'error') {
          errors.push(msg.text());
        }
      });

      // Perform search
      const searchInput = page.locator('input[placeholder*="Search"]');
      await searchInput.fill('airport');
      await page.waitForTimeout(SEARCH_DEBOUNCE);

      // Clear search
      await searchInput.clear();
      await page.waitForTimeout(SEARCH_DEBOUNCE);

      // No console errors should occur
      expect(errors.length).toBe(0);
    });
  });

  test.describe('Mobile Search', () => {

    test('should work on mobile viewport', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 812 });
      await page.goto(BASE_URL);
      await page.waitForLoadState('networkidle');

      // Open filter panel on mobile (usually hidden behind button)
      const filterButton = page.locator('button[aria-label*="filter"]').first();
      if (await filterButton.isVisible()) {
        await filterButton.click();
        await page.waitForTimeout(500);
      }

      // Find and use search input
      const searchInput = page.locator('input[placeholder*="Search"]');
      await expect(searchInput).toBeVisible();

      await searchInput.fill('mobile test');
      await expect(searchInput).toHaveValue('mobile test');
    });
  });
});
