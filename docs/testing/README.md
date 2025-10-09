# DroneWatch 2.0 - E2E Testing Guide

Complete testing suite for DroneWatch production site using Playwright.

---

## 📋 Quick Start

### Installation

```bash
cd tests
npm install
npx playwright install  # Install browser binaries
```

### Run Tests

```bash
# Run all tests
npm test

# Run tests in headed mode (see browser)
npm run test:headed

# Run tests in UI mode (interactive)
npm run test:ui

# Run tests in debug mode
npm run test:debug

# Run specific browser
npm run test:chromium
npm run test:firefox
npm run test:webkit

# Run mobile tests
npm run test:mobile

# Run all browsers
npm run test:all

# View last test report
npm run report
```

---

## 📁 Project Structure

```
tests/
├── e2e/
│   └── dronewatch.spec.ts    # Main test suite
├── playwright.config.ts       # Playwright configuration
├── package.json              # Dependencies and scripts
└── README.md                 # This file

test-results/                 # Generated after test run
├── html/                     # HTML report
├── screenshots/              # Failure screenshots
├── videos/                   # Failure videos
├── traces/                   # Playwright traces
├── results.json              # JSON results
└── junit.xml                 # JUnit XML results
```

---

## 🎯 Test Suites

### 1. Initial Page Load (5 tests)
- Homepage loads successfully
- Map renders correctly
- Incident markers appear
- Load time under 3 seconds
- No console errors

### 2. Header and Navigation (3 tests)
- All header elements visible
- View switching works
- Theme toggle works

### 3. Map Interactions (3 tests)
- Zoom in/out works
- Marker click opens popup
- Evidence badge displays in popup

### 4. Filter Panel (5 tests)
- Opens on desktop
- Opens on mobile
- Evidence level filter works
- Country filter works
- Clear all filters works

### 5. List View (3 tests)
- Switches to list view
- Evidence badges display
- Empty state shows correctly

### 6. Analytics View (1 test)
- Charts render correctly

### 7. Mobile Responsiveness (2 tests)
- Displays correctly on mobile (375x812)
- Filter button positioned correctly

### 8. Accessibility (3 tests)
- ARIA labels present
- Active tab has aria-current
- Keyboard navigation works

### 9. Performance (2 tests)
- API data loads within 2 seconds
- Bundle size under 2MB

### 10. Data Quality (3 tests)
- Only Nordic incidents shown
- No test incidents visible
- Source badges display

### 11. Visual Regression (2 tests)
- Homepage matches baseline
- List view matches baseline

**Total: 32 automated tests**

---

## 🖥️ Tested Browsers

### Desktop
- ✅ Chromium (Chrome/Edge)
- ✅ Firefox
- ✅ WebKit (Safari)
- ✅ Microsoft Edge
- ✅ Google Chrome

### Mobile
- ✅ Mobile Chrome (Pixel 5)
- ✅ Mobile Safari (iPhone 12)

---

## 📊 Test Reports

After running tests, view the report:

```bash
npm run report
```

This opens an HTML report showing:
- Pass/fail status for each test
- Screenshots of failures
- Videos of failures
- Execution time
- Browser coverage
- Detailed error messages

---

## 🐛 Debugging Failed Tests

### View Trace
When a test fails, Playwright captures a trace. View it:

```bash
npx playwright show-trace test-results/traces/[test-name].zip
```

### Debug Mode
Run tests in debug mode to step through:

```bash
npm run test:debug
```

### Headed Mode
See the browser while tests run:

```bash
npm run test:headed
```

### UI Mode
Interactive test runner:

```bash
npm run test:ui
```

---

## 🎨 Recording New Tests

Use Playwright Codegen to record interactions:

```bash
npm run codegen
```

This opens a browser and records your actions as Playwright code.

---

## ⚙️ Configuration

Edit `playwright.config.ts` to customize:

- **Timeout**: Default 10 seconds
- **Retries**: 0 locally, 2 on CI
- **Base URL**: https://www.dronemap.cc
- **Browsers**: Add/remove browsers
- **Screenshot**: on-failure
- **Video**: retain-on-failure
- **Trace**: on-first-retry

---

## 🚀 CI/CD Integration

### GitHub Actions

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-node@v3
      with:
        node-version: 18

    - name: Install dependencies
      run: |
        cd tests
        npm ci

    - name: Install Playwright Browsers
      run: npx playwright install --with-deps

    - name: Run Playwright tests
      run: npm test

    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: playwright-report
        path: test-results/
        retention-days: 30
```

### GitLab CI

```yaml
e2e-tests:
  image: mcr.microsoft.com/playwright:v1.40.0-focal
  stage: test
  script:
    - cd tests
    - npm ci
    - npm test
  artifacts:
    when: always
    paths:
      - test-results/
    expire_in: 1 week
```

---

## 📝 Writing New Tests

### Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should do something', async ({ page }) => {
    // Arrange
    const button = page.locator('button');

    // Act
    await button.click();

    // Assert
    await expect(page.locator('.result')).toBeVisible();
  });
});
```

### Best Practices

1. **Use data-testid for stable selectors**
   ```typescript
   await page.locator('[data-testid="submit-button"]').click();
   ```

2. **Wait for network idle before assertions**
   ```typescript
   await page.waitForLoadState('networkidle');
   ```

3. **Use expect with proper matchers**
   ```typescript
   await expect(page.locator('.title')).toHaveText('Expected Text');
   ```

4. **Group related tests**
   ```typescript
   test.describe('Related Feature', () => {
     // Tests here share setup
   });
   ```

5. **Use Page Object Model for complex pages**
   ```typescript
   class HomePage {
     constructor(public page: Page) {}

     async clickLogin() {
       await this.page.click('[data-testid="login"]');
     }
   }
   ```

---

## 🔍 Selectors

### Recommended Selector Priority

1. **data-testid** (most stable)
   ```typescript
   page.locator('[data-testid="submit"]')
   ```

2. **User-facing text** (semantic)
   ```typescript
   page.locator('text=Submit')
   page.getByRole('button', { name: 'Submit' })
   ```

3. **ARIA labels** (accessible)
   ```typescript
   page.locator('[aria-label="Close"]')
   ```

4. **CSS selectors** (last resort)
   ```typescript
   page.locator('.submit-button')
   ```

---

## 📈 Performance Testing

### Lighthouse Integration

```typescript
import { test } from '@playwright/test';
import { playAudit } from 'playwright-lighthouse';

test('should pass Lighthouse audit', async ({ page }) => {
  await page.goto('/');

  await playAudit({
    page,
    thresholds: {
      performance: 90,
      accessibility: 90,
      'best-practices': 90,
      seo: 90,
    },
    reports: {
      formats: {
        html: true,
        json: true,
      },
      directory: './lighthouse-reports',
    },
  });
});
```

---

## 🛠️ Troubleshooting

### Tests Timeout
**Issue**: Tests hang or timeout
**Solution**:
- Increase timeout in config
- Check for missing `await` keywords
- Ensure selectors are correct

### Browser Not Found
**Issue**: Error about missing browser
**Solution**:
```bash
npx playwright install chromium
# or
npx playwright install --with-deps
```

### Flaky Tests
**Issue**: Tests pass/fail inconsistently
**Solution**:
- Add `await page.waitForLoadState('networkidle')`
- Use `toBeVisible()` with timeout
- Avoid `waitForTimeout()`, use proper waits

### Screenshot Differences
**Issue**: Visual regression tests fail
**Solution**:
- Update baselines: `npm test -- --update-snapshots`
- Increase `maxDiffPixels` threshold
- Check for date/time-dependent content

---

## 📚 Resources

- [Playwright Documentation](https://playwright.dev)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [API Reference](https://playwright.dev/docs/api/class-test)
- [Debugging Guide](https://playwright.dev/docs/debug)
- [Trace Viewer](https://playwright.dev/docs/trace-viewer)

---

## ✅ Manual Testing

For manual testing, use the checklist:
- **Manual Test Checklist**: `../MANUAL_TEST_CHECKLIST.md`
- **Test Report Template**: `../TEST_REPORT_TEMPLATE.md`

---

## 🤝 Contributing

When adding new tests:

1. Follow existing test structure
2. Add descriptive test names
3. Group related tests in `describe` blocks
4. Add comments for complex logic
5. Update this README if adding new test suites
6. Run tests locally before committing

---

## 📞 Support

For issues or questions:
- Check [Playwright Discord](https://aka.ms/playwright/discord)
- File issues in repository
- Review existing test failures in CI

---

**Last Updated**: October 7, 2025
**Playwright Version**: 1.40.0
