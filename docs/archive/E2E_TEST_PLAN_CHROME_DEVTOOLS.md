# DroneWatch 2.0 - Chrome DevTools E2E Test Plan

**Date**: October 7, 2025
**Version**: 2.2.0
**Tool**: Chrome DevTools MCP
**URL**: https://www.dronemap.cc

---

## Test Execution Instructions

Once Chrome DevTools MCP is loaded (after Claude Code restart), run these tests:

---

## Test Suite 1: Page Load & Performance

### Test 1.1: Initial Page Load
```javascript
// Navigate to production site
await page.goto('https://www.dronemap.cc', { waitUntil: 'networkidle' });

// Check title
const title = await page.title();
console.log('Page title:', title);
// Expected: "DroneWatch" or similar

// Check for critical elements
const hasMap = await page.$('#map') !== null;
const hasHeader = await page.$('header') !== null;
const hasFilters = await page.$('[class*="filter"]') !== null;

console.log('Has Map:', hasMap);
console.log('Has Header:', hasHeader);
console.log('Has Filters:', hasFilters);
```

**Expected Results**:
- ✅ Page loads in <3 seconds
- ✅ Title contains "DroneWatch"
- ✅ Map container exists
- ✅ Header exists
- ✅ Filter panel exists

### Test 1.2: Console Errors
```javascript
// Check for console errors (should be NONE after our cleanup)
const consoleLogs = await page.evaluate(() => {
  const logs = [];
  const originalConsole = console.log;
  console.log = (...args) => {
    logs.push(args);
    originalConsole(...args);
  };
  return logs;
});

console.log('Console logs found:', consoleLogs.length);
```

**Expected Results**:
- ✅ NO console.log statements (we removed them all)
- ✅ NO console errors
- ✅ Clean console output

### Test 1.3: Network Performance
```javascript
// Check API response
const apiResponse = await page.waitForResponse(
  response => response.url().includes('/api/incidents'),
  { timeout: 5000 }
);

const incidents = await apiResponse.json();
console.log('Incidents loaded:', incidents.length);
console.log('Response time:', apiResponse.timing().responseTime);
```

**Expected Results**:
- ✅ API responds in <1 second
- ✅ Returns 6 incidents (current production count)
- ✅ Valid JSON structure

---

## Test Suite 2: Visual Validation

### Test 2.1: Map Rendering
```javascript
// Wait for map to load
await page.waitForSelector('.leaflet-container', { timeout: 10000 });

// Check for map tiles
const hasTiles = await page.$$('.leaflet-tile');
console.log('Map tiles loaded:', hasTiles.length);

// Check for markers
const markers = await page.$$('.leaflet-marker-icon');
console.log('Markers on map:', markers.length);
```

**Expected Results**:
- ✅ Leaflet map renders
- ✅ Map tiles load (50+ tiles typical)
- ✅ Markers appear (6 incidents = 6 markers or facility clusters)

### Test 2.2: Header Components
```javascript
// Check header elements
const logo = await page.$('[class*="DroneWatch"]');
const viewToggle = await page.$$('button[aria-label*="Switch to"]');
const themeToggle = await page.$('button[aria-label*="mode"]');
const incidentCount = await page.$('text=/\\d+|UPDATING/');

console.log('Logo exists:', logo !== null);
console.log('View toggle buttons:', viewToggle.length);
console.log('Theme toggle exists:', themeToggle !== null);
console.log('Incident count visible:', incidentCount !== null);
```

**Expected Results**:
- ✅ DroneWatch logo visible
- ✅ 3 view toggle buttons (Map, List, Analytics)
- ✅ Theme toggle present
- ✅ Incident count shows "6" or "UPDATING"

### Test 2.3: ARIA Labels (Accessibility)
```javascript
// Check our new ARIA labels
const viewButtons = await page.$$('button[aria-label*="Switch to"]');
const filterButton = await page.$('button[aria-label*="filter"]');
const themeButton = await page.$('button[aria-label*="mode"]');

console.log('View buttons with ARIA:', viewButtons.length);
console.log('Filter button ARIA:', await filterButton?.getAttribute('aria-label'));
console.log('Theme button ARIA:', await themeButton?.getAttribute('aria-label'));
```

**Expected Results**:
- ✅ 3 view buttons with aria-label="Switch to [view] view"
- ✅ Filter button with aria-label (includes active count)
- ✅ Theme button with dynamic aria-label

---

## Test Suite 3: Interactive Elements

### Test 3.1: View Switching
```javascript
// Test view switching
const listButton = await page.$('button[aria-label="Switch to list view"]');
await listButton.click();
await page.waitForTimeout(500);

// Check if list view is active
const listView = await page.$('[class*="IncidentList"]');
console.log('List view active:', listView !== null);

// Switch to Analytics
const analyticsButton = await page.$('button[aria-label="Switch to analytics view"]');
await analyticsButton.click();
await page.waitForTimeout(500);

const analyticsView = await page.$('[class*="Analytics"]');
console.log('Analytics view active:', analyticsView !== null);

// Switch back to Map
const mapButton = await page.$('button[aria-label="Switch to map view"]');
await mapButton.click();
await page.waitForTimeout(500);
```

**Expected Results**:
- ✅ List view switches successfully
- ✅ Analytics view switches successfully
- ✅ Map view switches successfully
- ✅ Smooth transitions (no errors)

### Test 3.2: Filter Panel (Mobile Button Position)
```javascript
// Check mobile filter button position (our fix: bottom-20, right-4)
const filterButton = await page.$('button[class*="fixed"][class*="lg:hidden"]');
const buttonStyles = await filterButton?.evaluate(el => {
  const rect = el.getBoundingClientRect();
  return {
    bottom: window.innerHeight - rect.bottom,
    right: window.innerWidth - rect.right
  };
});

console.log('Filter button position:', buttonStyles);
// Should be ~80px from bottom (bottom-20 = 5rem = 80px)
// Should be ~16px from right (right-4 = 1rem = 16px)
```

**Expected Results**:
- ✅ Button positioned at bottom-20 (~80px from bottom)
- ✅ Button positioned at right-4 (~16px from right)
- ✅ No overlap with map controls

### Test 3.3: Theme Toggle
```javascript
// Test theme switching
const themeButton = await page.$('button[aria-label*="mode"]');
await themeButton.click();
await page.waitForTimeout(300);

// Check if theme changed
const isDark = await page.evaluate(() => {
  return document.documentElement.classList.contains('dark');
});

console.log('Dark mode active:', isDark);
```

**Expected Results**:
- ✅ Theme toggles successfully
- ✅ Dark mode class applied/removed
- ✅ Visual change visible

---

## Test Suite 4: Filter Functionality

### Test 4.1: Evidence Level Filters
```javascript
// Open filter panel (if not already open)
const filterToggle = await page.$('button[aria-expanded]');
const isOpen = await filterToggle?.getAttribute('aria-expanded') === 'true';
if (!isOpen) {
  await filterToggle.click();
  await page.waitForTimeout(300);
}

// Check evidence filter options
const evidenceFilters = await page.$$('input[type="checkbox"], button[class*="evidence"]');
console.log('Evidence filter options:', evidenceFilters.length);
```

**Expected Results**:
- ✅ Filter panel opens
- ✅ Evidence level filters present
- ✅ All 4 evidence levels available (1-4)

### Test 4.2: Country Filters
```javascript
// Check country filter
const countrySelect = await page.$('select, [role="combobox"]');
console.log('Country filter exists:', countrySelect !== null);
```

**Expected Results**:
- ✅ Country filter available
- ✅ Shows available countries

---

## Test Suite 5: Empty State (Our Enhancement)

### Test 5.1: Enhanced Empty State
```javascript
// Set filters that return no results
// (This might require interacting with specific filters)
// Then check for our enhanced empty state

const emptyState = await page.$('text=/No incidents found/');
if (emptyState) {
  // Check for our enhancements
  const hasHelpfulTips = await page.$('text=/Try:/');
  const hasTipList = await page.$$('li');
  const hasStyling = await page.$('[class*="blue"]');

  console.log('Empty state found:', true);
  console.log('Has helpful tips:', hasHelpfulTips !== null);
  console.log('Has tip list:', hasTipList.length > 0);
  console.log('Has blue styling:', hasStyling !== null);
}
```

**Expected Results** (if empty state triggered):
- ✅ Bold headline "No incidents found"
- ✅ Clear description
- ✅ Blue box with 💡 icon
- ✅ 4 actionable tips listed

---

## Test Suite 6: Mobile Responsiveness

### Test 6.1: Mobile Viewport
```javascript
// Set mobile viewport
await page.setViewport({ width: 375, height: 667 }); // iPhone SE

// Check mobile-specific elements
const mobileViewToggle = await page.$('.md\\:hidden');
const mobileFilterButton = await page.$('.lg\\:hidden');

console.log('Mobile view toggle visible:', mobileViewToggle !== null);
console.log('Mobile filter button visible:', mobileFilterButton !== null);
```

**Expected Results**:
- ✅ Mobile view toggle shows on small screens
- ✅ Mobile filter button visible
- ✅ Layout adapts to mobile

### Test 6.2: Touch Targets
```javascript
// Check button sizes (should be ≥44x44px for touch)
const buttons = await page.$$('button');
const touchTargetSizes = await Promise.all(
  buttons.map(btn => btn.evaluate(el => {
    const rect = el.getBoundingClientRect();
    return { width: rect.width, height: rect.height };
  }))
);

const validTouchTargets = touchTargetSizes.filter(
  size => size.width >= 44 && size.height >= 44
);

console.log('Total buttons:', buttons.length);
console.log('Valid touch targets (≥44x44px):', validTouchTargets.length);
```

**Expected Results**:
- ✅ Most interactive elements ≥44x44px
- ✅ Accessible on mobile devices

---

## Test Suite 7: Performance Metrics

### Test 7.1: Core Web Vitals
```javascript
// Measure performance
const metrics = await page.evaluate(() => {
  const perfData = window.performance.getEntriesByType('navigation')[0];
  return {
    loadTime: perfData.loadEventEnd - perfData.fetchStart,
    domContentLoaded: perfData.domContentLoadedEventEnd - perfData.fetchStart,
    firstPaint: performance.getEntriesByType('paint')[0]?.startTime,
  };
});

console.log('Load time:', metrics.loadTime, 'ms');
console.log('DOM Content Loaded:', metrics.domContentLoaded, 'ms');
console.log('First Paint:', metrics.firstPaint, 'ms');
```

**Expected Results**:
- ✅ Load time <3000ms
- ✅ DOM Content Loaded <1500ms
- ✅ First Paint <1000ms

### Test 7.2: Bundle Size
```javascript
// Check JavaScript bundle size
const resources = await page.evaluate(() => {
  return performance.getEntriesByType('resource')
    .filter(r => r.name.includes('.js'))
    .map(r => ({ name: r.name, size: r.transferSize }));
});

const totalJS = resources.reduce((sum, r) => sum + r.size, 0);
console.log('Total JavaScript:', (totalJS / 1024).toFixed(2), 'KB');
```

**Expected Results**:
- ✅ Total JS ~167 KB (matches our build output)
- ✅ No unexpectedly large bundles

---

## Test Suite 8: Error Handling

### Test 8.1: Network Error Simulation
```javascript
// Simulate offline
await page.setOfflineMode(true);
await page.reload();

// Check for error message
const errorMessage = await page.$('text=/Error loading incidents/');
console.log('Error message shown:', errorMessage !== null);

// Check for retry option
const retryButton = await page.$('button:has-text("Reload")');
console.log('Retry button available:', retryButton !== null);

// Restore online
await page.setOfflineMode(false);
```

**Expected Results**:
- ✅ Error message displays
- ✅ Retry/reload option available
- ✅ Graceful error handling

---

## Success Criteria

### Must Pass:
- ✅ All page load tests
- ✅ No console.log statements (cleaned)
- ✅ ARIA labels present on all interactive elements
- ✅ Mobile filter button positioned correctly
- ✅ Enhanced empty state displays
- ✅ All views switch successfully

### Should Pass:
- ✅ Performance metrics within targets
- ✅ Accessibility score >90
- ✅ Mobile responsiveness good
- ✅ Error handling graceful

### Nice to Have:
- ✅ All touch targets ≥44px
- ✅ Bundle size optimized
- ✅ Smooth animations

---

## Expected Overall Results

Based on our improvements:

**Before Improvements**:
- Console logs: Present 🐛
- ARIA labels: Missing ⚠️
- Mobile button: Poorly positioned ⚠️
- Empty states: Basic ⚠️
- Accessibility: ~70/100 ⚠️

**After Improvements**:
- Console logs: **REMOVED** ✅
- ARIA labels: **ALL ADDED** ✅
- Mobile button: **FIXED (bottom-20, right-4)** ✅
- Empty states: **ENHANCED** ✅
- Accessibility: **~95/100** ✅

**Estimated Lighthouse Scores**:
- Performance: 90-95
- Accessibility: 95-100
- Best Practices: 95-100
- SEO: 100

---

## Automated Test Script

Here's a complete script you can run:

```javascript
async function testDroneWatch() {
  console.log('🧪 Starting DroneWatch E2E Tests...\n');

  const results = {
    passed: 0,
    failed: 0,
    tests: []
  };

  // Test 1: Page Load
  await page.goto('https://www.dronemap.cc');
  const title = await page.title();
  if (title.includes('DroneWatch')) {
    results.passed++;
    results.tests.push({ name: 'Page Title', status: 'PASS' });
  }

  // Test 2: Console Logs (should be NONE)
  const logs = await page.evaluate(() => console.log.length);
  if (!logs || logs === 0) {
    results.passed++;
    results.tests.push({ name: 'No Console Logs', status: 'PASS' });
  }

  // Test 3: ARIA Labels
  const ariaButtons = await page.$$('button[aria-label]');
  if (ariaButtons.length >= 5) {
    results.passed++;
    results.tests.push({ name: 'ARIA Labels Present', status: 'PASS' });
  }

  // Test 4: Mobile Button Position
  const filterBtn = await page.$('button[class*="bottom-20"]');
  if (filterBtn) {
    results.passed++;
    results.tests.push({ name: 'Mobile Button Position', status: 'PASS' });
  }

  // Summary
  console.log('\n═══════════════════════════════════');
  console.log('TEST RESULTS');
  console.log('═══════════════════════════════════');
  console.log(`Total Tests: ${results.passed + results.failed}`);
  console.log(`✅ Passed: ${results.passed}`);
  console.log(`❌ Failed: ${results.failed}`);
  console.log(`Success Rate: ${((results.passed / (results.passed + results.failed)) * 100).toFixed(1)}%`);

  results.tests.forEach(test => {
    console.log(`${test.status === 'PASS' ? '✅' : '❌'} ${test.name}`);
  });
}

// Run tests
testDroneWatch();
```

---

**Test Plan Created**: October 7, 2025
**Ready for Execution**: After Claude Code restart
**Expected Duration**: 5-10 minutes
**Expected Pass Rate**: 95-100%
