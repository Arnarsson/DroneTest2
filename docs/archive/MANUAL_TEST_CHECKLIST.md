# Manual Test Checklist - DroneWatch 2.0 v2.3.0

**Preview URL**: https://dronewatch20-2bttyvxtp-arnarssons-projects.vercel.app
**Date**: October 7, 2025
**Tester**: USER
**Expected Evidence Counts**: OFFICIAL (5), VERIFIED (1), REPORTED (0), UNCONFIRMED (0)

---

## Quick Test (5 minutes)

Essential tests to verify core functionality:

1. **Legend Displays** - [ ] Bottom-left, shows 5/1/0/0 counts
2. **Map Loads** - [ ] 6 markers visible (5 green, 1 amber)
3. **Popup Opens** - [ ] Click any marker → popup with sources
4. **Cluster Works** - [ ] Copenhagen (3 incidents) or Aalborg (2 incidents)
5. **No Console Errors** - [ ] Open DevTools → Console → No red errors

---

## Full Test Suite (42 tests - 30 minutes)

### 1. Evidence Legend (6 tests)
- [ ] 1.1: Auto-opens on first visit, shows correct counts (5/1/0/0)
- [ ] 1.2: Collapse/expand animation smooth
- [ ] 1.3: "Learn more" link opens /about page
- [ ] 1.4: Count badges animate on open
- [ ] 1.5: Updates when filters applied
- [ ] 1.6: Hidden on mobile (<1024px)

### 2. Map & Clustering (6 tests)
- [ ] 2.1: Map centers on Nordic region, 6 markers visible
- [ ] 2.2: Aalborg shows cluster OR 2 separate markers
- [ ] 2.3: Copenhagen shows cluster with ✈️ 3
- [ ] 2.4: Billund shows single marker (Score 4, green)
- [ ] 2.5: No numbered Leaflet clusters (7, 8, 9)
- [ ] 2.6: Facility clusters use neutral slate color

### 3. Popup Enhancements (8 tests)
- [ ] 3.1: Title + date format: "X days ago · DD MMM YYYY HH:MM"
- [ ] 3.2: Evidence badge correct color (green/amber)
- [ ] 3.3: Source hierarchy: Quote → Name → "View Source"
- [ ] 3.4: Trust badge shows (e.g., "POLICE 100%")
- [ ] 3.5: Quote displayed in blockquote (if exists)
- [ ] 3.6: "Copy Embed Code" button works
- [ ] 3.7: "Report Issue" opens GitHub issues
- [ ] 3.8: Multi-source display (incident #6 has 2 sources)

### 4. Cluster Modal (6 tests)
- [ ] 4.1: Modal title: "✈️ Copenhagen Airport (3 incidents)"
- [ ] 4.2: 3 incident cards visible, sorted newest first
- [ ] 4.3: Each card clickable with chevron (→)
- [ ] 4.4: Click card → opens popup
- [ ] 4.5: Close button (X) + outside click + Escape work
- [ ] 4.6: Modal animation smooth (fade in/out)

### 5. Filter Integration (6 tests)
- [ ] 5.1: Min evidence = 4 → Shows 5, legend shows OFFICIAL (5)
- [ ] 5.2: Min evidence = 3 → Shows 6, legend shows 5/1
- [ ] 5.3: Min evidence = 1 → Shows 6, legend shows 5/1
- [ ] 5.4: Country = Denmark → Shows 6 (all DK)
- [ ] 5.5: Country = Norway → Shows 0
- [ ] 5.6: Asset = Airport → Shows 6 (all airports)

### 6. Performance (4 tests)
- [ ] 6.1: Page load < 3s on 3G
- [ ] 6.2: API response < 500ms
- [ ] 6.3: Bundle size < 200 KB
- [ ] 6.4: No console errors or warnings

### 7. Mobile Responsive (3 tests)
- [ ] 7.1: Map fills mobile screen (375×667)
- [ ] 7.2: Popup fits mobile, buttons 44×44px min
- [ ] 7.3: Cluster modal scrollable, full-width

### 8. Dark Mode (3 tests)
- [ ] 8.1: Toggle theme → all components readable
- [ ] 8.2: Map tiles switch to dark theme
- [ ] 8.3: Text contrast meets WCAG AA

---

## Test Results

**Quick Test**: ___/5 passed
**Full Test**: ___/42 passed

**Critical Issues**:


**Ready for Production**: YES / NO

**Tester**: ________________
**Completed**: ________________
