# DroneWatch 2.0 - Manual E2E Test Checklist

**Production Site**: https://www.dronemap.cc
**Date**: October 7, 2025
**System Version**: 2.2.0 (AI Verification + Multi-Layer Defense)

---

## 🎯 Test Objectives

- Verify all Phase 1 UX improvements are live
- Validate evidence scoring system accuracy
- Test geographic filtering (Nordic-only incidents)
- Ensure mobile responsiveness
- Validate AI verification layer integration

---

## ✅ Pre-Test Setup

- [ ] Clear browser cache
- [ ] Test on multiple browsers (Chrome, Firefox, Safari)
- [ ] Test on mobile device or device emulation
- [ ] Verify you have stable internet connection

---

## 1️⃣ Initial Page Load

### Desktop View
- [ ] **Site loads successfully** at https://www.dronemap.cc
- [ ] **Map renders correctly** (Leaflet map visible)
- [ ] **Incident markers appear** on map
- [ ] **No console errors** (F12 → Console tab)
- [ ] **Page loads in <3 seconds**

### Visual Elements
- [ ] **DroneWatch logo** visible in header
- [ ] **"Safety Through Transparency" tagline** visible
- [ ] **Theme toggle button** (sun/moon icon) visible
- [ ] **View tabs** (Map/List/Analytics) visible and clickable
- [ ] **Filter button** visible (desktop: sidebar, mobile: floating button)

---

## 2️⃣ Map View Testing

### Map Interaction
- [ ] **Zoom in/out** works smoothly
- [ ] **Pan/drag** map works correctly
- [ ] **Incident markers** are color-coded by evidence score:
  - Green = Official (Score 4)
  - Amber = Verified (Score 3)
  - Orange = Reported (Score 2)
  - Red = Unconfirmed (Score 1)

### Facility Clustering
- [ ] **Multiple incidents at same location** show cluster marker with count (e.g., ✈️ 3)
- [ ] **Individual incidents** show evidence score marker (1-4)
- [ ] **Clicking cluster** zooms to facility and expands markers
- [ ] **No numbered clusters** (7, 8, 9) appearing - only facility clusters or evidence scores

### Incident Popups
- [ ] **Click marker** opens popup
- [ ] **Popup shows**:
  - Incident title
  - Evidence badge (colored, with emoji and label)
  - Date (formatted: "Oct 3, 2025" or "2 days ago")
  - Location (city, country)
  - Asset type with icon
  - Source badge(s) with trust indicators
- [ ] **Multiple sources** listed if available
- [ ] **Popup closes** when clicking X or map

---

## 3️⃣ Filter Panel Testing

### Opening/Closing
- [ ] **Desktop**: Filter panel visible on left sidebar
- [ ] **Mobile**: Floating filter button (bottom-right, above map controls)
- [ ] **Mobile button shows active filter count** if filters applied
- [ ] **Filter panel slides in smoothly** (animation)

### Evidence Level Filter
- [ ] **4 toggle buttons** visible (Official, Verified, Reported, Unconfirmed)
- [ ] **Default**: All enabled
- [ ] **Toggle OFF "Unconfirmed"** → Red markers disappear
- [ ] **Toggle ON again** → Red markers reappear
- [ ] **Map updates immediately** when toggling

### Date Range Filter
- [ ] **Timeline slider** visible
- [ ] **Drag left handle** → Filters out older incidents
- [ ] **Drag right handle** → Filters out newer incidents
- [ ] **Date labels update** as you drag
- [ ] **Map markers update** in real-time

### Country Filter
- [ ] **Dropdown shows**: All Countries, Denmark, Norway, Sweden, Finland, Poland, Netherlands
- [ ] **Select "Denmark"** → Only Danish incidents visible
- [ ] **Map centers** on Denmark
- [ ] **Select "All Countries"** → All incidents return

### Asset Type Filter
- [ ] **6 toggle buttons**: Airport, Military, Harbor, Power Plant, Bridge, Other
- [ ] **Default**: All enabled
- [ ] **Toggle OFF "Airport"** → Airport incidents disappear
- [ ] **Toggle multiple types** → Filters combine correctly
- [ ] **Icons match asset types** correctly

### Clear Filters
- [ ] **"Clear All" button** visible
- [ ] **Click "Clear All"** → All filters reset to default
- [ ] **All incidents** reappear on map

---

## 4️⃣ List View Testing

### Switching Views
- [ ] **Click "List" tab** in header
- [ ] **View switches** from map to list
- [ ] **Tab is highlighted** (active state)
- [ ] **Smooth transition** (animation)

### List Display
- [ ] **All incidents displayed** as cards
- [ ] **Each card shows**:
  - Evidence badge (colored)
  - Title
  - Date
  - Location with country flag emoji
  - Asset type with icon
  - Source badge(s)
- [ ] **Cards are scrollable** if many incidents
- [ ] **Sorted by date** (newest first)

### Filtering in List View
- [ ] **Apply evidence filter** → List updates
- [ ] **Apply date filter** → List updates
- [ ] **Apply country filter** → List updates
- [ ] **Apply asset filter** → List updates
- [ ] **Filters work same as Map view**

### Empty State
- [ ] **Apply strict filters** (e.g., only Score 1 from 2020)
- [ ] **Empty state shows**:
  - 🔍 emoji
  - "No incidents found" message
  - Blue help box with 4 tips
- [ ] **Tips are readable** and helpful

---

## 5️⃣ Analytics View Testing

### Switching Views
- [ ] **Click "Analytics" tab**
- [ ] **View switches** to analytics dashboard
- [ ] **Loading state** if data is being calculated

### Charts Display
- [ ] **Incidents Over Time chart** visible
- [ ] **Evidence Distribution chart** visible
- [ ] **Country Distribution chart** visible
- [ ] **Asset Type Distribution chart** visible
- [ ] **Charts render correctly** (no errors)
- [ ] **Data matches** incident count

### Interactivity
- [ ] **Hover over chart elements** shows tooltips
- [ ] **Charts are responsive** to filters
- [ ] **Apply filter** → Charts update

---

## 6️⃣ Theme Toggle Testing

### Light/Dark Mode
- [ ] **Click theme toggle** (sun/moon icon)
- [ ] **Theme switches** smoothly
- [ ] **All elements adapt**:
  - Background colors
  - Text colors
  - Map tiles
  - Card backgrounds
  - Buttons
- [ ] **No visual glitches** during switch
- [ ] **Toggle again** → Returns to original theme
- [ ] **Theme persists** after page reload

---

## 7️⃣ Mobile Responsiveness Testing

### Mobile View (< 768px)
- [ ] **Switch to mobile** (375px x 812px - iPhone X)
- [ ] **Map fills screen** vertically
- [ ] **Header shrinks** appropriately
- [ ] **View tabs stack** or remain accessible
- [ ] **Filter button** floats at bottom-right
- [ ] **Filter button positioned correctly** (bottom-20, right-4 - NOT overlapping map controls)

### Filter Panel Mobile
- [ ] **Click filter button**
- [ ] **Panel slides up** from bottom
- [ ] **Panel covers most of screen**
- [ ] **Close button** visible
- [ ] **All filters accessible** and usable
- [ ] **Scrollable** if content overflows

### Touch Interactions
- [ ] **Map pan** works with touch
- [ ] **Map zoom** works with pinch
- [ ] **Tap marker** opens popup
- [ ] **Tap outside popup** closes it
- [ ] **Swipe to dismiss** filter panel (if implemented)

### Landscape Mode
- [ ] **Rotate to landscape**
- [ ] **Layout adapts** correctly
- [ ] **All elements remain accessible**

---

## 8️⃣ Data Quality Validation

### Evidence Scores
- [ ] **Check 5 random incidents**
- [ ] **Verify evidence score matches sources**:
  - Score 4: Police/military/aviation authority source
  - Score 3: 2+ media sources OR 1 media + official quote
  - Score 2: 1 credible media source
  - Score 1: Social media or low-trust source
- [ ] **No "test" incidents** visible (e.g., "DroneTest Success")

### Geographic Scope
- [ ] **All incidents are Nordic** (Denmark, Norway, Sweden, Finland, Poland, Netherlands)
- [ ] **No foreign incidents** (e.g., Ukraine, Russia, Germany outside Nordic)
- [ ] **Coordinates within** 54-71°N, 4-31°E

### Source Quality
- [ ] **Each incident has** at least 1 source
- [ ] **Source badges show**:
  - Source type (News, Police, Aviation, etc.)
  - Trust indicator (star/checkmark)
  - Publication name
- [ ] **Sources are clickable** (link to original article)
- [ ] **No broken links**

### Multi-Source Incidents
- [ ] **Find incident with 2+ sources**
- [ ] **Verify evidence score upgraded** (e.g., 2 news sources → Score 3)
- [ ] **All sources listed** in popup
- [ ] **No duplicate sources**

---

## 9️⃣ Performance Testing

### Load Times
- [ ] **Initial page load**: <3 seconds
- [ ] **Map render**: <1 second after page load
- [ ] **Incident data fetch**: <2 seconds
- [ ] **Filter application**: <100ms (instant)
- [ ] **View switching**: <200ms (smooth)

### Network Requests
- [ ] **Open Network tab** (F12 → Network)
- [ ] **Check API calls**:
  - `/api/incidents` returns 200 OK
  - Response time <2 seconds
  - JSON payload valid
- [ ] **No failed requests** (404, 500 errors)
- [ ] **No excessive requests** (no infinite loops)

### Bundle Size
- [ ] **Check Performance tab**
- [ ] **Initial JS bundle**: <500KB
- [ ] **Total transfer**: <2MB
- [ ] **No memory leaks** after 5 minutes of use

---

## 🔟 Accessibility Testing

### Keyboard Navigation
- [ ] **Tab through page** elements
- [ ] **All interactive elements** focusable
- [ ] **Focus indicators** visible
- [ ] **Enter/Space** activates buttons
- [ ] **Escape** closes popups/panels

### ARIA Labels
- [ ] **Inspect ViewTab buttons** (F12 → Elements)
- [ ] **Verify aria-label**: "Switch to map view", etc.
- [ ] **Verify aria-current**: "page" on active tab
- [ ] **Filter button has** aria-label and aria-expanded

### Screen Reader Compatibility
- [ ] **Use VoiceOver** (Mac: Cmd+F5) or **NVDA** (Windows)
- [ ] **Navigate page** with screen reader
- [ ] **All content announced** correctly
- [ ] **No missing labels**

### Color Contrast
- [ ] **Evidence badges** readable in both themes
- [ ] **Text on buttons** readable
- [ ] **Map labels** readable
- [ ] **No WCAG AA violations** (use browser extension)

---

## 1️⃣1️⃣ AI Verification Layer (Backend)

### Verify AI Layer is Active
- [ ] **Check recent incidents** (<24 hours old)
- [ ] **Incidents should be**:
  - Actual drone sightings/incidents
  - NOT policy announcements
  - NOT defense deployments
  - NOT discussion articles
- [ ] **No false positives** in database

### Test Cases (Backend Validation)
If you have access to the database or logs:
- [ ] **Check `ai_verification` column** in incidents table
- [ ] **Verify incidents have** `is_incident: true`
- [ ] **Check confidence scores** (should be >0.7)
- [ ] **No incidents with** `category: "policy"` or `"defense"`

---

## 1️⃣2️⃣ Error Handling

### Network Errors
- [ ] **Disable network** (DevTools → Network → Offline)
- [ ] **Reload page**
- [ ] **Error message displayed** (not blank page)
- [ ] **Re-enable network**
- [ ] **Page recovers** when back online

### Invalid Filters
- [ ] **Manually set date range** where start > end
- [ ] **App handles gracefully** (no crash)
- [ ] **Shows appropriate message** or corrects automatically

### Missing Data
- [ ] **Apply filters** that return 0 results
- [ ] **Empty state shown** correctly (not error)
- [ ] **Helpful tips displayed**

---

## 1️⃣3️⃣ Cross-Browser Testing

### Chrome
- [ ] **All tests above** pass in Chrome

### Firefox
- [ ] **All tests above** pass in Firefox
- [ ] **Map renders** correctly
- [ ] **No Firefox-specific bugs**

### Safari
- [ ] **All tests above** pass in Safari
- [ ] **iOS Safari** (if testing mobile)
- [ ] **No Safari-specific bugs**

---

## ✅ Test Summary

### Pass/Fail Count
- **Total Tests**: ___
- **Passed**: ___
- **Failed**: ___
- **Blocked**: ___

### Critical Issues Found
1.
2.
3.

### Minor Issues Found
1.
2.
3.

### Performance Metrics
- **Average Load Time**: ___ seconds
- **Largest Contentful Paint**: ___ seconds
- **First Input Delay**: ___ ms
- **Cumulative Layout Shift**: ___

### Overall Assessment
- [ ] **Production Ready** ✅
- [ ] **Needs Minor Fixes** ⚠️
- [ ] **Needs Major Fixes** ❌

### Tester Notes
```
[Your observations and comments here]
```

---

## 📊 Next Steps

Based on test results:
1. **If all pass**: Deploy Phase 2 improvements
2. **If minor issues**: Create bug tickets, fix in next sprint
3. **If critical issues**: Hotfix immediately before promoting

---

**Test Completed By**: _____________
**Date**: _____________
**Time Spent**: _____________
