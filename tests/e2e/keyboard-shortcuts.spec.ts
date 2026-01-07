import { test, expect } from '@playwright/test';

/**
 * DroneWatch 2.0 - Keyboard Shortcuts E2E Tests
 * Tests keyboard shortcuts for view switching and filter panel toggle
 */

const BASE_URL = 'https://www.dronemap.cc';
const LOAD_TIMEOUT = 10000;

test.describe('Keyboard Shortcuts E2E Tests', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate to production site before each test
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
    // Wait for the app to be fully loaded and interactive
    await expect(page.locator('.leaflet-container')).toBeVisible({ timeout: LOAD_TIMEOUT });
  });

  test.describe('View Switching with Keyboard', () => {

    test('should switch to List view when pressing "2"', async ({ page }) => {
      // Verify we start on Map view
      await expect(page.locator('[aria-current="page"]')).toHaveText(/Map/i);

      // Press '2' to switch to List view
      await page.keyboard.press('2');

      // Wait for view change
      await page.waitForTimeout(500);

      // Verify List view is now active
      await expect(page.locator('[aria-current="page"]')).toHaveText(/List/i);
    });

    test('should switch to Analytics view when pressing "3"', async ({ page }) => {
      // Press '3' to switch to Analytics view
      await page.keyboard.press('3');

      // Wait for view change
      await page.waitForTimeout(500);

      // Verify Analytics view is now active
      await expect(page.locator('[aria-current="page"]')).toHaveText(/Analytics/i);
    });

    test('should switch to Map view when pressing "1"', async ({ page }) => {
      // First switch to a different view
      await page.keyboard.press('2');
      await page.waitForTimeout(500);
      await expect(page.locator('[aria-current="page"]')).toHaveText(/List/i);

      // Press '1' to switch back to Map view
      await page.keyboard.press('1');
      await page.waitForTimeout(500);

      // Verify Map view is now active
      await expect(page.locator('[aria-current="page"]')).toHaveText(/Map/i);
    });

    test('should cycle through all views using keyboard', async ({ page }) => {
      // Start at Map (default)
      await expect(page.locator('[aria-current="page"]')).toHaveText(/Map/i);

      // Press '2' -> List
      await page.keyboard.press('2');
      await page.waitForTimeout(300);
      await expect(page.locator('[aria-current="page"]')).toHaveText(/List/i);

      // Press '3' -> Analytics
      await page.keyboard.press('3');
      await page.waitForTimeout(300);
      await expect(page.locator('[aria-current="page"]')).toHaveText(/Analytics/i);

      // Press '1' -> Map
      await page.keyboard.press('1');
      await page.waitForTimeout(300);
      await expect(page.locator('[aria-current="page"]')).toHaveText(/Map/i);
    });

    test('should handle rapid keyboard presses', async ({ page }) => {
      // Rapidly press keys
      await page.keyboard.press('2');
      await page.keyboard.press('3');
      await page.keyboard.press('1');
      await page.keyboard.press('2');

      // Wait for final state
      await page.waitForTimeout(500);

      // Should end up on List view (last pressed was '2')
      await expect(page.locator('[aria-current="page"]')).toHaveText(/List/i);
    });
  });

  test.describe('Filter Panel Toggle with Keyboard', () => {

    test('should toggle filter panel with "f" key on mobile', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 812 });
      await page.goto(BASE_URL);
      await page.waitForLoadState('networkidle');

      // Find the filter toggle button
      const filterButton = page.locator('button[aria-label*="filter"]').first();
      await expect(filterButton).toBeVisible();

      // Press 'f' to open filter panel
      await page.keyboard.press('f');
      await page.waitForTimeout(500);

      // Filter panel should be visible (check for filter panel content)
      const filterPanel = page.locator('[class*="filter"]').first();
      await expect(filterPanel).toBeVisible();

      // Press 'f' again to close
      await page.keyboard.press('f');
      await page.waitForTimeout(500);
    });

    test('should toggle filter panel with uppercase "F" key', async ({ page }) => {
      // Set mobile viewport for better visibility of toggle
      await page.setViewportSize({ width: 375, height: 812 });
      await page.goto(BASE_URL);
      await page.waitForLoadState('networkidle');

      // Press 'F' (uppercase, as if Shift is held but not as a modifier)
      await page.keyboard.press('F');
      await page.waitForTimeout(500);

      // Filter panel should be visible
      const filterPanel = page.locator('[class*="filter"]').first();
      await expect(filterPanel).toBeVisible();
    });
  });

  test.describe('Input Field Protection', () => {

    test('should not trigger shortcuts when typing in country filter select', async ({ page }) => {
      // Switch to list view first for easier access
      await page.click('text=List');
      await page.waitForTimeout(500);

      // Find the country select dropdown
      const countrySelect = page.locator('select').first();

      if (await countrySelect.isVisible()) {
        // Focus on the select
        await countrySelect.focus();

        // Try pressing '1' while focused on select
        await page.keyboard.press('1');
        await page.waitForTimeout(300);

        // Should NOT have switched to Map view - should still be on List
        await expect(page.locator('[aria-current="page"]')).toHaveText(/List/i);
      }
    });

    test('should not trigger shortcuts when typing in search/text inputs', async ({ page }) => {
      // Switch to list view
      await page.keyboard.press('2');
      await page.waitForTimeout(500);
      await expect(page.locator('[aria-current="page"]')).toHaveText(/List/i);

      // Find any input element (like search box if present)
      const inputs = page.locator('input[type="text"], input[type="search"]');
      const inputCount = await inputs.count();

      if (inputCount > 0) {
        // Focus on the first input
        await inputs.first().focus();

        // Try pressing view switching keys while in input
        await page.keyboard.type('123');
        await page.waitForTimeout(300);

        // Should still be on List view (shortcuts should be ignored)
        await expect(page.locator('[aria-current="page"]')).toHaveText(/List/i);
      }
    });
  });

  test.describe('Modifier Keys', () => {

    test('should not trigger shortcuts when Ctrl is held', async ({ page }) => {
      // Start at Map
      await expect(page.locator('[aria-current="page"]')).toHaveText(/Map/i);

      // Press Ctrl+2 (should not switch view)
      await page.keyboard.press('Control+2');
      await page.waitForTimeout(300);

      // Should still be on Map view
      await expect(page.locator('[aria-current="page"]')).toHaveText(/Map/i);
    });

    test('should not trigger shortcuts when Meta/Cmd is held', async ({ page }) => {
      // Start at Map
      await expect(page.locator('[aria-current="page"]')).toHaveText(/Map/i);

      // Press Meta+2 (should not switch view)
      await page.keyboard.press('Meta+2');
      await page.waitForTimeout(300);

      // Should still be on Map view
      await expect(page.locator('[aria-current="page"]')).toHaveText(/Map/i);
    });

    test('should not trigger shortcuts when Alt is held', async ({ page }) => {
      // Start at Map
      await expect(page.locator('[aria-current="page"]')).toHaveText(/Map/i);

      // Press Alt+2 (should not switch view)
      await page.keyboard.press('Alt+2');
      await page.waitForTimeout(300);

      // Should still be on Map view
      await expect(page.locator('[aria-current="page"]')).toHaveText(/Map/i);
    });
  });

  test.describe('Keyboard Shortcuts Help', () => {

    test('should display keyboard shortcuts help popover', async ({ page }) => {
      // Find the keyboard shortcuts help button
      const helpButton = page.locator('button[aria-label="Show keyboard shortcuts"]');

      // Verify button exists
      await expect(helpButton).toBeVisible();

      // Click to open the popover
      await helpButton.click();
      await page.waitForTimeout(300);

      // Verify popover content is visible
      await expect(page.locator('text=Keyboard Shortcuts')).toBeVisible();
      await expect(page.locator('text=Map View')).toBeVisible();
      await expect(page.locator('text=List View')).toBeVisible();
      await expect(page.locator('text=Analytics View')).toBeVisible();
      await expect(page.locator('text=Toggle Filters')).toBeVisible();
    });

    test('should close keyboard shortcuts help on Escape', async ({ page }) => {
      // Open the help popover
      const helpButton = page.locator('button[aria-label="Show keyboard shortcuts"]');
      await helpButton.click();
      await page.waitForTimeout(300);

      // Verify it's open
      await expect(page.locator('text=Keyboard Shortcuts')).toBeVisible();

      // Press Escape to close
      await page.keyboard.press('Escape');
      await page.waitForTimeout(300);

      // Verify popover is closed (help button should still be visible, but not the popover content)
      await expect(helpButton).toBeVisible();
      // The detailed content should no longer be visible
      await expect(page.locator('role=tooltip >> text=Map View')).not.toBeVisible();
    });
  });

  test.describe('Keyboard Hints Visibility', () => {

    test('should display keyboard shortcut hints on view tabs', async ({ page }) => {
      // Look for kbd elements in the view tabs
      const mapTabKbd = page.locator('button:has-text("MAP") kbd');
      const listTabKbd = page.locator('button:has-text("LIST") kbd');
      const analyticsTabKbd = page.locator('button:has-text("ANALYTICS") kbd');

      // Verify the keyboard hints are visible
      await expect(mapTabKbd.first()).toBeVisible();
      await expect(listTabKbd.first()).toBeVisible();
      await expect(analyticsTabKbd.first()).toBeVisible();

      // Verify the correct keys are displayed
      await expect(mapTabKbd.first()).toHaveText('1');
      await expect(listTabKbd.first()).toHaveText('2');
      await expect(analyticsTabKbd.first()).toHaveText('3');
    });

    test('should have aria-keyshortcuts attributes on tabs', async ({ page }) => {
      // Check aria-keyshortcuts attributes
      const mapTab = page.locator('button[aria-keyshortcuts="1"]').first();
      const listTab = page.locator('button[aria-keyshortcuts="2"]').first();
      const analyticsTab = page.locator('button[aria-keyshortcuts="3"]').first();

      await expect(mapTab).toBeVisible();
      await expect(listTab).toBeVisible();
      await expect(analyticsTab).toBeVisible();
    });
  });

  test.describe('Integration with Mouse Navigation', () => {

    test('should work with combined keyboard and mouse navigation', async ({ page }) => {
      // Start at Map
      await expect(page.locator('[aria-current="page"]')).toHaveText(/Map/i);

      // Click to go to List
      await page.click('text=List');
      await page.waitForTimeout(300);
      await expect(page.locator('[aria-current="page"]')).toHaveText(/List/i);

      // Use keyboard to go to Analytics
      await page.keyboard.press('3');
      await page.waitForTimeout(300);
      await expect(page.locator('[aria-current="page"]')).toHaveText(/Analytics/i);

      // Click to go to Map
      await page.click('text=Map');
      await page.waitForTimeout(300);
      await expect(page.locator('[aria-current="page"]')).toHaveText(/Map/i);

      // Use keyboard to go to List
      await page.keyboard.press('2');
      await page.waitForTimeout(300);
      await expect(page.locator('[aria-current="page"]')).toHaveText(/List/i);
    });
  });

  test.describe('Cross-Browser Keyboard Support', () => {

    test('should handle both numpad and regular number keys', async ({ page }) => {
      // Test regular number key
      await page.keyboard.press('2');
      await page.waitForTimeout(300);
      await expect(page.locator('[aria-current="page"]')).toHaveText(/List/i);

      // Return to Map
      await page.keyboard.press('1');
      await page.waitForTimeout(300);
      await expect(page.locator('[aria-current="page"]')).toHaveText(/Map/i);

      // Test numpad key (if supported by browser)
      await page.keyboard.press('Numpad2');
      await page.waitForTimeout(300);
      // Note: numpad might not trigger the shortcut depending on implementation
      // This tests that it doesn't cause errors
    });
  });
});
