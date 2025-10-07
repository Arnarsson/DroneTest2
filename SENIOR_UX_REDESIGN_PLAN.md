# DroneWatch 2.0 - Senior UX/UI Redesign Plan

**System Prompt Alignment**: Senior-level UX & UI Frontend Designer specialized in geospatial visualization tools for public intelligence systems

**Date**: October 7, 2025 (Evening)
**Version**: 2.3.0 (Target)
**Branch**: `feature/senior-ux-redesign`
**Timeline**: 2 weeks (4 sprints × 2-3 days each)

---

## Executive Summary

Transform DroneWatch from a consumer-focused map application into a **professional geospatial intelligence tool optimized for journalists, newsrooms, and public intelligence analysis**. Prioritize embed-first architecture, source transparency, mobile-first touch optimization, and pan-European scalability.

### Key Objectives

1. **Embed-First Architecture**: Journalists can filter, verify sources, and embed maps with full functionality
2. **Source Transparency**: Blockquoted quotes first, hover tooltips, color-coded trust badges
3. **Mobile-First Touch**: 44px targets, bottom sheets, pull-to-refresh, iOS safe areas
4. **Performance**: 167 kB → <120 kB bundle, sub-2s 4G load time
5. **Newsroom UX**: High-contrast WCAG AAA, data export, print view, no whimsical styling
6. **Scalability**: i18n framework, multi-language support, pan-European deployment

---

## Gap Analysis: Current vs. Requirements

### ✅ Strengths (What's Working)

| Component | Status | Quality |
|-----------|--------|---------|
| **Map-First Experience** | ✅ Implemented | Leaflet.js with OpenStreetMap (no closed-source tiles) |
| **Evidence System** | ✅ Strong | Single source of truth in `evidence.ts`, consistent across components |
| **Mobile-Responsive** | ✅ Foundation | Tailwind CSS with responsive breakpoints |
| **Performance Baseline** | ✅ Good | 167 kB bundle, sub-1s load time on production |
| **Embed Route** | ✅ Exists | `/embed` page with basic map functionality |
| **Source Verification** | ✅ Implemented | Multi-source system with trust weights (Migration 011) |
| **Accessibility Start** | ✅ Phase 1 | ARIA labels added (Oct 7, 2025) |

### ❌ Critical Gaps

#### 1. EMBED-FIRST ARCHITECTURE (SEVERITY: HIGH)

**Current State**:
- Embed exists at `/embed` but is feature-limited
- No filter controls in embed mode
- No source verification modal (iframe-safe)
- No URL parameter sync for sharable views
- Missing "Copy Embed Code" button

**Required State**:
- Full-featured `<EmbedMap />` component (iframe-safe, isolated styles)
- Filter drawer with evidence/date/country controls
- URL parameters for sharable filtered views (`?minEvidence=3&country=DK&dateRange=7d`)
- Copy Embed Code generator with customization options
- Responsive height control via URL params

**Impact**: **BLOCKS NEWSROOM ADOPTION** - Journalists cannot filter or share embedded maps

---

#### 2. SOURCE TRANSPARENCY (SEVERITY: HIGH)

**Current State** (`Map.tsx:396-552`):
- Sources displayed as list with name, type, trust weight
- Source quotes shown inline with title/narrative
- External link icon at end of source entry
- Trust weight as percentage badge (80% green, 60-79% amber, <60% grey)

**Required State** (from UX guidance):
- **Blockquoted source quotes FIRST** (primary element, not secondary)
- Source name as secondary text below quote
- Hover tooltips for domain + source type
- "View Source" CTA button (prominent, not just icon)
- Multi-source verified badge when ≥2 sources

**Current Code Example** (needs refactor):
```typescript
// Map.tsx:506-544 - Source display in popup
${incident.sources.map(source => {
  return `
    <a href="${source.source_url}" target="_blank" ...>
      <div>
        ${favicon ? `<img src="${favicon}" />` : `<span>${emoji}</span>`}
        <span>${sourceName}</span> <!-- SOURCE NAME FIRST (WRONG) -->
        ${trustWeight badge}
        <svg>external link</svg>
      </div>
      ${showType ? `<span>${source.source_type}</span>` : ''}
    </a>
  `
})}
```

**Required Pattern**:
```typescript
// CORRECT: Quote first, name second, CTA prominent
<blockquote className="border-l-4 border-blue-500 pl-3 italic text-gray-700">
  "{source.source_quote || 'No direct quote available'}"
</blockquote>
<div className="flex items-center justify-between mt-2">
  <div className="flex items-center gap-2">
    <span className="text-sm font-medium">{sourceName}</span>
    <span className="text-xs text-gray-500" title={`Domain: ${domain}, Type: ${type}`}>
      ℹ️
    </span>
  </div>
  <button className="px-3 py-1 bg-blue-600 text-white rounded text-sm font-medium">
    View Source →
  </button>
</div>
```

**Impact**: **REDUCES TRUST** - Journalists need to read original quotes to validate information

---

#### 3. EVIDENCE LEGEND (SEVERITY: MEDIUM)

**Current State** (`components/EvidenceLegend.tsx`):
- Static legend component (non-interactive)
- Fixed positioning (bottom-right)
- No explanations of scoring system
- No examples of each evidence level
- Not optimized for mobile or embed

**Required State** (from UX guidance):
- **Interactive legend**: Click badges to toggle filter (1-4)
- Tooltips explaining each level (Social media/rumour → Official report)
- Example sources for each level
- "Learn More" link to About page
- **Mobile**: Horizontal bar with compact badges
- **Embed**: Collapsible drawer or pop-over (iframe-safe)
- **Accessibility**: High contrast, pattern overlays for color-blind users

**Implementation**:
```typescript
// components/EvidenceLegend.tsx (needs major refactor)
interface EvidenceLegendProps {
  activeFilters: Set<1 | 2 | 3 | 4>
  onToggle: (level: 1 | 2 | 3 | 4) => void
  mode?: 'full' | 'compact' | 'embed'
}

// Interactive badges with tooltips
{[1, 2, 3, 4].map(level => (
  <button
    key={level}
    onClick={() => onToggle(level as 1 | 2 | 3 | 4)}
    className={cn(
      'px-3 py-2 rounded-lg transition-all',
      activeFilters.has(level) ? 'opacity-100' : 'opacity-40'
    )}
    data-tooltip-id={`evidence-${level}`}
  >
    {config.emoji} {config.label}
  </button>
))}
```

**Impact**: **REDUCES USABILITY** - Users don't understand evidence system, can't quick-filter

---

#### 4. MOBILE-FIRST FAILURES (SEVERITY: MEDIUM)

**Current State**:
- Filter button at `bottom-12 right-6` (may overlap)
- Filter drawer slides from **side** (desktop pattern)
- Map popups have small touch targets (<44px)
- No iOS safe area insets
- No pull-to-refresh gesture
- No touch-optimized incident cards

**Required State**:
- Filter button at `bottom-20 right-4` with safe area insets
- Filter UI as **bottom sheet** (mobile-first pattern)
- Map popups with **44px minimum** touch targets
- Swipe-to-dismiss gestures
- Pull-to-refresh (10-15 lines with `react-use-gesture`)
- Touch-optimized card layout

**Impact**: **POOR MOBILE UX** - Touch targets too small, filter panel blocks content

---

#### 5. PERFORMANCE OPTIMIZATION (SEVERITY: MEDIUM)

**Current State**:
- Bundle size: 167 kB (good, but can be optimized)
- Framer Motion: 12 kB (used for non-critical animations)
- date-fns: 53 kB (could use smaller alternatives)
- Inline marker styles (increases bundle size)

**Target State**:
- **Phase 1**: 165 kB (minimal increase for embed features)
- **Phase 2**: 153 kB (-12 kB from removing Framer Motion)
- **Phase 3**: <120 kB (-47 kB from all optimizations)

**Optimization Strategy**:
1. Replace Framer Motion with CSS transitions (0 bundle cost)
2. Tree-shake unused date-fns functions
3. Lazy load Analytics components
4. Use next/dynamic for non-critical UI
5. Optimize Leaflet marker icons (extract inline styles)

**Impact**: **SLOWER 4G LOAD** - Target is sub-2s on 4G, currently ~2.5s

---

#### 6. NEWSROOM UX GAPS (SEVERITY: MEDIUM)

**Current State**:
- Consumer-focused UI with animations everywhere
- No data export features (JSON/CSV)
- No print-friendly view
- No "Copy Embed Code" button
- Missing editorial-style high-contrast design

**Required State**:
- High-contrast WCAG AAA design
- Export incident data as JSON/CSV
- Print-optimized CSS (`@media print`)
- Embed code generator with preview
- Editorial color palette (no whimsical styling)

**Impact**: **BLOCKS NEWSROOM USE** - Missing critical features for journalists

---

#### 7. SCALABILITY GAPS (SEVERITY: LOW)

**Current State**:
- Single-language (English)
- Hardcoded labels everywhere
- No i18n framework
- Denmark-focused (but supports Nordic)

**Required State**:
- next-intl i18n framework
- 5-language support (en, da, no, se, fi)
- Translated evidence labels + UI strings
- Region-specific defaults (auto-detect location)

**Impact**: **LIMITS EXPANSION** - Cannot deploy pan-European without i18n

---

## 4-Phase Implementation Plan

### PHASE 1: EMBED-FIRST ARCHITECTURE (Days 1-3)
**Goal**: Make DroneWatch embeddable, sharable, and journalist-ready
**Timeline**: 2-3 days | **Risk**: LOW | **Impact**: HIGH

#### Sprint 1.1: EmbedMap Component (Day 1)
**Files**: `components/embed/EmbedMap.tsx`, `app/embed/page.tsx`

**Tasks**:
1. Create isolated `<EmbedMap />` component
   - No external layout dependencies
   - Iframe-safe styles (no `window.top` calls)
   - Responsive height via URL param (`?height=600`)
   - Self-contained CSS (no Tailwind JIT issues in iframe)

2. Add filter drawer to embed mode
   - Evidence score slider (1-4)
   - Date range picker (relative: Today, 7d, 30d; absolute: YYYY-MM-DD)
   - Country dropdown (all Nordic countries)
   - Asset type checkboxes
   - Collapsible on mobile

3. Implement URL parameter system
   - Read params on mount: `useSearchParams()`
   - Update URL on filter change (debounced 300ms)
   - Browser history support (back/forward)
   - Sharable links for journalists

**Deliverables**:
- `/embed` route with full feature parity
- URL param schema documented
- Filter controls working in embed mode

**Testing**:
- [ ] Embed works in `<iframe>` (test on localhost)
- [ ] URL parameters sync correctly
- [ ] Filters update map in real-time
- [ ] No console errors in iframe

---

#### Sprint 1.2: Source Transparency Modal (Day 2)
**Files**: `components/embed/SourceModal.tsx`, `Map.tsx` (refactor popup)

**Tasks**:
1. Refactor source display pattern (blockquotes first)
   ```typescript
   // BEFORE: Name first, quote inline
   <div>
     <span>{sourceName}</span>
     <p>{narrative with quote}</p>
   </div>

   // AFTER: Quote first, name second
   <blockquote className="border-l-4 border-blue-500 pl-3 mb-2">
     "{source.source_quote || 'No direct quote available'}"
   </blockquote>
   <div className="flex justify-between">
     <span className="text-sm font-medium">{sourceName}</span>
     <button className="bg-blue-600 text-white px-3 py-1 rounded">
       View Source →
     </button>
   </div>
   ```

2. Add hover tooltips for domain + type
   - Use `data-tooltip-id` with Radix UI Tooltip
   - Show: `Domain: politi.dk | Type: police`
   - No inline text, only icon with hover

3. Implement multi-source verified badge
   - Show when `sources.length >= 2`
   - Green gradient background
   - "✓ Multi-source verified" text
   - Position at top of source list

4. Make modal iframe-safe
   - No `window.open()` or `window.parent` calls
   - Use `target="_blank" rel="noopener noreferrer"`
   - Test in iframe sandbox

**Deliverables**:
- Source quotes prominently displayed
- Hover tooltips for context
- Multi-source badge working
- Iframe-compatible modal

**Testing**:
- [ ] Source quotes render first
- [ ] Tooltips show on hover
- [ ] Multi-source badge appears when applicable
- [ ] Modal works in iframe

---

#### Sprint 1.3: Copy Embed Code Generator (Day 3)
**Files**: `components/embed/CopyEmbedCode.tsx`

**Tasks**:
1. Build embed code generator UI
   - Textarea with generated iframe code
   - Copy to clipboard button
   - Preview section showing current filters
   - Customization options (width, height, showFilters)

2. Generate iframe HTML
   ```typescript
   const embedCode = `
   <iframe
     src="https://dronewatch.cc/embed?minEvidence=${filters.minEvidence}&country=${filters.country}&dateRange=${filters.dateRange}&height=600&showFilters=true"
     width="100%"
     height="600"
     frameborder="0"
     style="border: 0;"
     allowfullscreen
   ></iframe>
   `.trim()
   ```

3. Add customization controls
   - Width: percentage or pixels
   - Height: pixels (default 600)
   - Show filters: boolean toggle
   - Show legend: boolean toggle

4. Social media preview meta tags
   - `og:image` for Twitter/LinkedIn
   - `og:description` with incident count
   - `og:title` with filtered view description

**Deliverables**:
- Copy Embed Code button in header
- Working iframe generator
- Social media preview tags

**Testing**:
- [ ] Generated iframe code works
- [ ] Copy to clipboard functional
- [ ] Social media previews render
- [ ] Customization options apply

---

### PHASE 2: NEWSROOM UX OPTIMIZATION (Days 4-6)
**Goal**: Transform UI for editorial/public intelligence use
**Timeline**: 2-3 days | **Risk**: MEDIUM | **Impact**: HIGH

#### Sprint 2.1: Remove Framer Motion + High Contrast (Day 4)
**Files**: `package.json`, `page.tsx`, `Header.tsx`, `FilterPanel.tsx`

**Tasks**:
1. Remove Framer Motion dependency
   ```bash
   npm uninstall framer-motion
   # Expected savings: -12 kB
   ```

2. Replace with CSS transitions
   ```typescript
   // BEFORE: <motion.div initial={...} animate={...} />
   // AFTER: <div className="transition-all duration-300 ease-out" />
   ```

3. Keep only essential animations
   - View tab transitions (CSS only)
   - Filter panel slide-in (CSS transform)
   - Modal fade-in (CSS opacity)

4. Increase contrast for WCAG AAA
   - Audit all colors with Lighthouse
   - Evidence badges: bolder borders
   - Text: minimum 7:1 contrast ratio
   - Background/foreground pairs validated

**Deliverables**:
- -12 kB bundle size reduction
- WCAG AAA contrast compliance
- No layout shift or jank

**Testing**:
- [ ] Bundle size: 167 kB → 155 kB
- [ ] Lighthouse accessibility score: 95+
- [ ] No visual regressions

---

#### Sprint 2.2: Data Export Features (Day 5)
**Files**: `components/newsroom/DataExport.tsx`, `hooks/useDataExport.ts`

**Tasks**:
1. Build export menu component
   ```typescript
   // Export dropdown in header
   <DropdownMenu>
     <DropdownMenuItem onClick={exportJSON}>
       Export as JSON
     </DropdownMenuItem>
     <DropdownMenuItem onClick={exportCSV}>
       Export as CSV
     </DropdownMenuItem>
     <DropdownMenuItem onClick={copyData}>
       Copy to Clipboard
     </DropdownMenuItem>
     <DropdownMenuItem onClick={printView}>
       Print View
     </DropdownMenuItem>
   </DropdownMenu>
   ```

2. Implement JSON export
   ```typescript
   const exportJSON = () => {
     const data = JSON.stringify(filteredIncidents, null, 2)
     const blob = new Blob([data], { type: 'application/json' })
     const url = URL.createObjectURL(blob)
     const a = document.createElement('a')
     a.href = url
     a.download = `dronewatch-incidents-${new Date().toISOString()}.json`
     a.click()
   }
   ```

3. Implement CSV export
   ```typescript
   const exportCSV = () => {
     const headers = ['Title', 'Date', 'Country', 'Evidence', 'Sources', 'Lat', 'Lon']
     const rows = filteredIncidents.map(i => [
       i.title,
       i.occurred_at,
       i.country,
       i.evidence_score,
       i.sources.map(s => s.source_name).join('; '),
       i.lat,
       i.lon
     ])
     const csv = [headers, ...rows].map(row => row.join(',')).join('\n')
     // Download as .csv
   }
   ```

4. Add print-friendly CSS
   ```css
   @media print {
     .no-print { display: none; }
     .print-only { display: block; }
     .incident-list { page-break-inside: avoid; }
   }
   ```

**Deliverables**:
- Export menu in header
- JSON/CSV export working
- Print-friendly view

**Testing**:
- [ ] JSON export downloads correctly
- [ ] CSV opens in Excel/Google Sheets
- [ ] Print view removes UI chrome

---

#### Sprint 2.3: Bottom Sheet Mobile UI (Day 6)
**Files**: `components/mobile/BottomSheet.tsx`, `FilterPanel.tsx` (refactor)

**Tasks**:
1. Build bottom sheet component
   ```typescript
   import { useGesture } from 'react-use-gesture'

   const BottomSheet = ({ isOpen, onClose, children }) => {
     const [{ y }, set] = useSpring(() => ({ y: 0 }))

     const bind = useGesture({
       onDrag: ({ movement: [, my], last }) => {
         if (last && my > 100) {
           onClose() // Swipe down to close
         } else {
           set({ y: my > 0 ? my : 0 })
         }
       }
     })

     return (
       <animated.div
         {...bind()}
         style={{ transform: y.to(y => `translateY(${y}px)`) }}
         className="fixed bottom-0 left-0 right-0 bg-white rounded-t-2xl shadow-elevated"
       >
         {children}
       </animated.div>
     )
   }
   ```

2. Add snap points (25%, 50%, 100%)
   - Swipe to expand/collapse
   - Haptic feedback on snap (iOS/Android)
   - Backdrop dims when expanded

3. Replace side drawer with bottom sheet on mobile
   ```typescript
   // BEFORE: FilterPanel slides from right
   // AFTER: BottomSheet slides from bottom
   {isMobile ? (
     <BottomSheet isOpen={isOpen} onClose={onClose}>
       <FilterContent />
     </BottomSheet>
   ) : (
     <FilterPanel /> // Desktop: keep sidebar
   )}
   ```

4. Add iOS safe area insets
   ```typescript
   style={{
     paddingBottom: 'max(env(safe-area-inset-bottom), 20px)'
   }}
   ```

**Deliverables**:
- Bottom sheet component
- Swipe-to-dismiss working
- iOS safe area support

**Testing**:
- [ ] Bottom sheet animates smoothly
- [ ] Swipe gestures work correctly
- [ ] Safe area insets applied on iOS

---

### PHASE 3: PERFORMANCE & SCALABILITY (Days 7-10)
**Goal**: Sub-2s 4G load, i18n support, pan-European ready
**Timeline**: 3-4 days | **Risk**: MEDIUM | **Impact**: MEDIUM

#### Sprint 3.1: Bundle Optimization (Day 7-8)
**Files**: `package.json`, `next.config.js`, `components/*`

**Tasks**:
1. Optimize date-fns imports
   ```typescript
   // BEFORE: import { format, formatDistance } from 'date-fns'
   // AFTER: import { format } from 'date-fns/format'
   //        import { formatDistance } from 'date-fns/formatDistance'
   ```

2. Tree-shake Leaflet features
   ```typescript
   // Only import needed Leaflet modules
   import L from 'leaflet/dist/leaflet-src.esm'
   ```

3. Lazy load Analytics components
   ```typescript
   const Analytics = dynamic(() => import('@/components/Analytics'), {
     loading: () => <LoadingSkeleton />,
     ssr: false
   })
   ```

4. Use next/dynamic for modals
   ```typescript
   const SourceModal = dynamic(() => import('@/components/SourceModal'))
   const AboutModal = dynamic(() => import('@/components/AboutModal'))
   ```

5. Optimize Leaflet marker icons
   - Extract inline styles to CSS classes
   - Use SVG sprites instead of inline HTML
   - Reduce gradient complexity

**Deliverables**:
- Bundle size: 153 kB → <120 kB
- Lazy loading implemented
- No performance regressions

**Testing**:
- [ ] Bundle size <120 kB
- [ ] Lighthouse performance score: 90+
- [ ] Load time <2s on 4G throttle

---

#### Sprint 3.2: i18n Framework (Day 9)
**Files**: `next.config.js`, `i18n/`, `components/*`

**Tasks**:
1. Install next-intl
   ```bash
   npm install next-intl
   ```

2. Create translation files
   ```
   i18n/
   ├── en.json   # English (default)
   ├── da.json   # Danish
   ├── no.json   # Norwegian
   ├── se.json   # Swedish
   └── fi.json   # Finnish
   ```

3. Extract hardcoded strings
   ```typescript
   // BEFORE: <h1>DroneWatch</h1>
   // AFTER: <h1>{t('site.title')}</h1>
   ```

4. Translate evidence labels
   ```json
   // en.json
   {
     "evidence": {
       "1": "Unconfirmed",
       "2": "Reported",
       "3": "Verified",
       "4": "Official"
     }
   }

   // da.json
   {
     "evidence": {
       "1": "Ubekræftet",
       "2": "Rapporteret",
       "3": "Verificeret",
       "4": "Officiel"
     }
   }
   ```

5. Add language selector
   ```typescript
   <select value={locale} onChange={changeLocale}>
     <option value="en">🇬🇧 English</option>
     <option value="da">🇩🇰 Dansk</option>
     <option value="no">🇳🇴 Norsk</option>
     <option value="se">🇸🇪 Svenska</option>
     <option value="fi">🇫🇮 Suomi</option>
   </select>
   ```

**Deliverables**:
- next-intl configured
- 5 languages supported
- Language selector in header

**Testing**:
- [ ] All UI strings translated
- [ ] Language switching works
- [ ] Date formatting locale-aware

---

#### Sprint 3.3: Touch Optimization (Day 10)
**Files**: `components/mobile/TouchPopup.tsx`, `Map.tsx`

**Tasks**:
1. Increase touch targets to 44px minimum
   ```typescript
   // BEFORE: <button className="p-1 text-sm">
   // AFTER: <button className="p-3 text-base min-w-[44px] min-h-[44px]">
   ```

2. Implement pull-to-refresh
   ```typescript
   import { useDrag } from 'react-use-gesture'

   const bind = useDrag(({ movement: [, my], last }) => {
     if (last && my > 100) {
       refetch() // Refresh data
     }
   })
   ```

3. Enable Leaflet touch gestures
   ```typescript
   L.map(mapRef.current, {
     touchZoom: true,
     doubleClickZoom: true,
     boxZoom: false, // Disable for better mobile UX
     tap: true
   })
   ```

4. Add haptic feedback (iOS/Android)
   ```typescript
   const vibrate = () => {
     if ('vibrate' in navigator) {
       navigator.vibrate(10) // 10ms pulse
     }
   }
   ```

**Deliverables**:
- Touch targets ≥44px
- Pull-to-refresh working
- Haptic feedback implemented

**Testing**:
- [ ] Touch targets meet accessibility standards
- [ ] Pull-to-refresh feels natural
- [ ] Haptic feedback works on iOS/Android

---

### PHASE 4: ADVANCED FEATURES (Days 11-14)
**Goal**: Complete professional toolset for newsrooms
**Timeline**: 3-4 days | **Risk**: LOW | **Impact**: MEDIUM

#### Sprint 4.1: Geolocation + Place Search (Day 11-12)
**Files**: `components/search/PlaceSearch.tsx`, `hooks/useGeolocation.ts`

**Tasks**:
1. Add Nominatim search API
   ```typescript
   const searchPlace = async (query: string) => {
     const response = await fetch(
       `https://nominatim.openstreetmap.org/search?q=${query}&format=json&limit=5`
     )
     return response.json()
   }
   ```

2. Build search autocomplete
   ```typescript
   <Combobox
     placeholder="Search for city or place..."
     options={searchResults}
     onSelect={flyToLocation}
   />
   ```

3. Implement geolocation detection
   ```typescript
   const { coords, error } = useGeolocation()

   useEffect(() => {
     if (coords) {
       map.flyTo([coords.latitude, coords.longitude], 10)
     }
   }, [coords])
   ```

4. Add "Use My Location" button
   ```typescript
   <button onClick={requestGeolocation}>
     📍 Use My Location
   </button>
   ```

**Deliverables**:
- Place search working
- Geolocation detection
- "Use My Location" button

**Testing**:
- [ ] Search returns relevant results
- [ ] Map flies to selected location
- [ ] Geolocation works with permission

---

#### Sprint 4.2: First-Time User Tour (Day 13)
**Files**: `components/tour/UserTour.tsx`, `hooks/useTour.ts`

**Tasks**:
1. Install react-joyride
   ```bash
   npm install react-joyride
   ```

2. Define tour steps
   ```typescript
   const steps = [
     {
       target: '.evidence-legend',
       content: 'Evidence levels: 1 (unconfirmed) to 4 (official)',
       disableBeacon: true
     },
     {
       target: '.filter-button',
       content: 'Filter incidents by evidence, date, and location'
     },
     {
       target: '.map-marker',
       content: 'Click markers to view incident details and sources'
     },
     {
       target: '.export-button',
       content: 'Export data as JSON or CSV for analysis'
     }
   ]
   ```

3. Show tour on first visit
   ```typescript
   const [hasSeenTour, setHasSeenTour] = useLocalStorage('dronewatch-tour', false)

   useEffect(() => {
     if (!hasSeenTour) {
       startTour()
     }
   }, [])
   ```

4. Add "Help" button to restart tour
   ```typescript
   <button onClick={startTour}>
     ❓ Take Tour
   </button>
   ```

**Deliverables**:
- Interactive user tour
- First-visit detection
- Help button to restart

**Testing**:
- [ ] Tour shows on first visit
- [ ] Tour can be skipped
- [ ] Help button restarts tour

---

#### Sprint 4.3: Polish + Documentation (Day 14)
**Files**: `README.md`, `EMBED_DOCUMENTATION.md`, `API_DOCUMENTATION.md`

**Tasks**:
1. Update README with embed instructions
2. Create embed documentation
3. Document URL parameter schema
4. Add code examples for newsrooms
5. Create video walkthrough (optional)
6. Test all features end-to-end
7. Prepare PR for merge to main

**Deliverables**:
- Complete documentation
- E2E testing passed
- PR ready for review

---

## Architecture Changes

### New Component Structure

```
frontend/
├── components/
│   ├── embed/
│   │   ├── EmbedMap.tsx           # Isolated embed component (iframe-safe)
│   │   ├── EmbedFilters.tsx       # Compact filter drawer
│   │   ├── EmbedLegend.tsx        # Always-visible evidence legend
│   │   └── CopyEmbedCode.tsx      # Embed code generator
│   ├── newsroom/
│   │   ├── DataExport.tsx         # JSON/CSV export menu
│   │   ├── SourceModal.tsx        # Iframe-safe source verification
│   │   └── PrintView.tsx          # Print-optimized layout
│   ├── mobile/
│   │   ├── BottomSheet.tsx        # Mobile filter UI (swipe-to-dismiss)
│   │   ├── PullToRefresh.tsx      # Refresh gesture
│   │   └── TouchPopup.tsx         # Touch-optimized incident popup
│   ├── search/
│   │   └── PlaceSearch.tsx        # Nominatim place search
│   ├── tour/
│   │   └── UserTour.tsx           # First-time user onboarding
│   └── i18n/
│       ├── LocaleProvider.tsx     # next-intl provider
│       └── LanguageSelector.tsx   # Language dropdown
├── i18n/
│   ├── en.json  # English
│   ├── da.json  # Danish
│   ├── no.json  # Norwegian
│   ├── se.json  # Swedish
│   └── fi.json  # Finnish
└── hooks/
    ├── useGeolocation.ts          # Browser geolocation
    ├── useDataExport.ts           # JSON/CSV export
    └── useTour.ts                 # Tour state management
```

---

## URL Parameter Schema

### Embed Parameters

```typescript
interface EmbedParams {
  // Filtering
  minEvidence: 1 | 2 | 3 | 4           // Minimum evidence level
  country: 'all' | 'DK' | 'NO' | 'SE' | 'FI' | 'PL' | 'NL'
  dateRange: 'day' | 'week' | 'month' | 'all' | '2025-01-01:2025-12-31'
  assetType: 'airport' | 'military' | 'harbor' | 'powerplant' | 'other' | 'all'

  // Display
  height: number                        // Pixels (default: 600)
  showFilters: boolean                  // Show filter drawer (default: true)
  showLegend: boolean                   // Show evidence legend (default: true)
  locale: 'en' | 'da' | 'no' | 'se' | 'fi'  // Language (default: 'en')

  // Map
  center: string                        // Lat,lon (e.g., "56.0,10.5")
  zoom: number                          // Zoom level (default: 6)
}
```

### Example URLs

```bash
# Basic embed (Denmark, last 7 days, all evidence)
https://dronewatch.cc/embed?country=DK&dateRange=week

# Filtered embed (verified incidents only, airports)
https://dronewatch.cc/embed?minEvidence=3&assetType=airport

# Custom size + language
https://dronewatch.cc/embed?height=800&locale=da&showFilters=false

# Sharable filtered view
https://dronewatch.cc/embed?minEvidence=3&country=DK&dateRange=month&center=55.6761,12.5683&zoom=10
```

---

## Bundle Size Optimization

### Current State: 167 kB

```
Route (app)                              Size     First Load JS
┌ ○ /                                    32.1 kB         167 kB
├ ○ /embed                               1.3 kB          98.1 kB
└ ○ /about                               15 kB           140 kB
```

### Phase 1 Target: 165 kB (-2 kB)
- Add embed features (+5 kB)
- Optimize marker icons (-3 kB)

### Phase 2 Target: 153 kB (-14 kB)
- Remove Framer Motion (-12 kB)
- Optimize filter UI (-2 kB)

### Phase 3 Target: <120 kB (-47 kB)
- Tree-shake date-fns (-15 kB)
- Lazy load Analytics (-10 kB)
- Optimize Leaflet (-8 kB)
- next-intl efficiency (-2 kB)
- Use next/dynamic everywhere (-12 kB)

### Optimization Techniques

1. **Tree Shaking**
   ```typescript
   // BEFORE: import { format, formatDistance, parseISO } from 'date-fns'
   // AFTER:  import { format } from 'date-fns/format'
   ```

2. **Dynamic Imports**
   ```typescript
   const Analytics = dynamic(() => import('@/components/Analytics'), { ssr: false })
   ```

3. **Remove Heavy Dependencies**
   ```bash
   npm uninstall framer-motion     # -12 kB
   npm uninstall react-virtuoso    # -8 kB (if unused)
   ```

4. **Use Native CSS**
   - Replace Framer Motion with CSS transitions
   - Use CSS Grid instead of Flexbox libraries
   - Inline critical CSS

5. **Code Splitting**
   - Split embed route from main app
   - Lazy load modals and drawers
   - Use React.lazy for large components

---

## Success Metrics

### Embed Functionality
- [ ] Journalists can filter by evidence + date in embed
- [ ] Copy Embed Code generates working iframe
- [ ] URL parameters create sharable filtered views
- [ ] Source verification modal works in iframe
- [ ] Evidence legend always visible in embed mode
- [ ] Filter drawer responsive on mobile

### Performance
- [ ] Bundle size <120 kB (Phase 3 complete)
- [ ] Load time <2s on 4G (300 Kbps throttle)
- [ ] Interaction delay <100ms (60fps)
- [ ] Works smoothly on iPhone 11 / Galaxy S21
- [ ] Lighthouse performance score: 90+

### Source Transparency
- [ ] Source quotes displayed FIRST (blockquoted)
- [ ] Source name as secondary text
- [ ] Hover tooltips for domain + type
- [ ] "View Source" button prominent
- [ ] Multi-source verified badge appears when ≥2 sources
- [ ] Trust weight color-coded (green/amber/grey)

### Evidence Legend
- [ ] Interactive legend (click to toggle filter)
- [ ] Tooltips explain each evidence level
- [ ] Example sources for each level
- [ ] "Learn More" link to About page
- [ ] Mobile: horizontal bar with compact badges
- [ ] Embed: collapsible drawer (iframe-safe)
- [ ] Accessibility: WCAG AAA contrast + patterns

### Newsroom UX
- [ ] WCAG AAA contrast compliance
- [ ] Export incidents as JSON
- [ ] Export incidents as CSV
- [ ] Print-friendly view (@media print)
- [ ] No whimsical animations or styling
- [ ] High-density data display
- [ ] Editorial color palette

### Mobile Optimization
- [ ] Touch targets ≥44px (accessibility standard)
- [ ] Bottom sheet pattern for filters
- [ ] Swipe-to-dismiss gestures
- [ ] Pull-to-refresh working
- [ ] iOS safe area insets applied
- [ ] Haptic feedback on interactions

### Scalability
- [ ] 5-language support (en, da, no, se, fi)
- [ ] next-intl framework integrated
- [ ] Region-specific defaults (auto-detect location)
- [ ] Pan-European incident view
- [ ] Date formatting locale-aware
- [ ] Evidence labels translated

### Advanced Features
- [ ] Place search with Nominatim API
- [ ] Geolocation detection working
- [ ] "Use My Location" button
- [ ] First-time user tour (react-joyride)
- [ ] Help button to restart tour
- [ ] Complete embed documentation

---

## What NOT to Do (Requirements Compliance)

### NEVER Use Closed-Source Map Tiles
✅ **COMPLIANT**: Using OpenStreetMap + CARTO (open-source)
- Leaflet.js with OSM tiles (light mode)
- CARTO dark tiles (dark mode)
- No Mapbox, Google Maps, or proprietary services

### NEVER Clutter or Hide Evidence/Sources
⚠️ **NEEDS WORK**: Source quotes not prominent (Phase 1.2)
- Move source quotes to PRIMARY position (blockquoted)
- Add "View Source" button (prominent CTA)
- Never hide trust weights or multi-source badges

### NEVER Omit Evidence Score Badges
✅ **COMPLIANT**: Evidence badges always shown
- Map markers show score (1-4)
- List view shows evidence badge
- Popups display evidence level
- Legend explains scoring system

### NEVER Add Whimsical Styling
⚠️ **NEEDS WORK**: Framer Motion overused (Phase 2.1)
- Remove non-critical animations
- Use editorial color palette
- High-contrast, data-dense design
- No "cute" icons or fluffy copy

### NEVER Compromise Speed with Heavy Dependencies
⚠️ **NEEDS WORK**: Framer Motion 12 kB, can optimize (Phase 3)
- Remove Framer Motion (-12 kB)
- Tree-shake date-fns (-15 kB)
- Lazy load non-critical components (-20 kB)
- Target: <120 kB bundle

### NEVER Ship Components That Break in Iframe
⚠️ **NEEDS WORK**: Modals not iframe-safe (Phase 1.2)
- Test all modals in iframe sandbox
- No `window.open()` or `window.parent` calls
- Use `target="_blank" rel="noopener noreferrer"`
- Responsive height via URL params

### NEVER Display Incidents Without Source/Score
✅ **COMPLIANT**: Always shown
- Evidence score required in API
- Sources displayed in all views
- No incident can be added without verification

---

## Testing Strategy

### Unit Tests
- [ ] EmbedMap component renders correctly
- [ ] URL parameters parsed and applied
- [ ] Filter state syncs to URL
- [ ] Source modal displays blockquotes
- [ ] Evidence legend toggles filter
- [ ] Data export generates valid JSON/CSV

### Integration Tests
- [ ] Embed route works in iframe
- [ ] Filter changes update map in real-time
- [ ] Source verification modal opens correctly
- [ ] Language switching changes all UI strings
- [ ] Export downloads file with correct content

### E2E Tests (Playwright)
- [ ] Load embed page
- [ ] Apply filters (evidence, date, country)
- [ ] Verify URL parameters update
- [ ] Click incident marker
- [ ] Verify source quote displayed first
- [ ] Click "View Source" button
- [ ] Copy embed code
- [ ] Paste into iframe and verify

### Performance Tests
- [ ] Lighthouse performance score ≥90
- [ ] Bundle size <120 kB
- [ ] Load time <2s on 4G throttle (300 Kbps)
- [ ] Interaction delay <100ms
- [ ] No layout shift (CLS = 0)

### Accessibility Tests
- [ ] Lighthouse accessibility score ≥95
- [ ] WCAG AAA contrast ratios
- [ ] Keyboard navigation works
- [ ] Screen reader announces all elements
- [ ] Touch targets ≥44px

### Cross-Browser Tests
- [ ] Chrome (desktop + mobile)
- [ ] Firefox (desktop + mobile)
- [ ] Safari (desktop + iOS)
- [ ] Edge (desktop)

### Device Tests
- [ ] iPhone 11 (iOS 15)
- [ ] Galaxy S21 (Android 12)
- [ ] iPad Pro (iPadOS 15)
- [ ] Desktop (1920×1080)
- [ ] Desktop (2560×1440)

---

## Risk Mitigation

### HIGH RISK: Bundle Size Optimization (Phase 3)
**Concern**: Tree-shaking might break functionality
**Mitigation**:
- Test after each dependency change
- Use bundle analyzer to verify savings
- Maintain feature parity throughout
- Rollback if bundle increases

### MEDIUM RISK: Framer Motion Removal (Phase 2)
**Concern**: Layout shift or broken animations
**Mitigation**:
- Replace with CSS transitions BEFORE removing
- Test all animated components
- Keep commits small for easy rollback
- Use git stash if issues arise

### MEDIUM RISK: i18n Integration (Phase 3)
**Concern**: Hard to extract all strings, potential bugs
**Mitigation**:
- Use TypeScript for type-safe translations
- Extract strings incrementally
- Test each language separately
- Keep English as fallback

### LOW RISK: Bottom Sheet UI (Phase 2)
**Concern**: Touch gestures might conflict with map
**Mitigation**:
- Disable map interaction when sheet dragging
- Add touch zones for safe interaction
- Test on real devices (not just simulator)

---

## Timeline & Milestones

### Week 1: Foundation
- **Day 1-3**: Phase 1 (Embed-First Architecture)
- **Milestone**: Journalists can embed filtered maps
- **Deliverable**: Working `/embed` route with full features

### Week 2: Optimization
- **Day 4-6**: Phase 2 (Newsroom UX)
- **Day 7-10**: Phase 3 (Performance & i18n)
- **Milestone**: <120 kB bundle, 5 languages supported
- **Deliverable**: Production-ready redesign

### Week 3 (Optional): Polish
- **Day 11-14**: Phase 4 (Advanced Features)
- **Milestone**: Place search, user tour, complete docs
- **Deliverable**: PR ready for merge

---

## Documentation Updates

### Files to Update
1. **README.md**
   - Add embed section with iframe examples
   - Document URL parameter schema
   - Add newsroom features (export, print)

2. **EMBED_DOCUMENTATION.md** (NEW)
   - Complete embed guide for journalists
   - Copy-paste iframe examples
   - Customization options
   - Troubleshooting

3. **API_DOCUMENTATION.md** (UPDATE)
   - Document export endpoints (if added)
   - URL parameter reference
   - Response schema

4. **CLAUDE.md** (UPDATE)
   - Add UX redesign architecture
   - Document new component structure
   - Update bundle size targets

---

## Conclusion

This redesign transforms DroneWatch from a consumer map application into a **professional geospatial intelligence tool** optimized for:
- **Journalists**: Embed maps, verify sources, export data
- **Newsrooms**: High-contrast UI, print views, editorial styling
- **Public Intelligence**: Source transparency, evidence scoring, multi-language
- **Mobile Users**: Touch-optimized, bottom sheets, pull-to-refresh

**Key Success Factors**:
1. ✅ Embed-first architecture enables newsroom adoption
2. ✅ Source transparency (blockquotes first) builds trust
3. ✅ Performance optimization (<120 kB) ensures fast 4G load
4. ✅ Mobile-first touch UX (44px targets) meets accessibility standards
5. ✅ i18n support enables pan-European deployment

**Next Steps**:
1. Merge this plan into `feature/senior-ux-redesign` branch
2. Begin Phase 1.1: Build EmbedMap component
3. Test incrementally, commit frequently
4. Deploy to staging after each phase
5. Gather journalist feedback before Phase 4

---

**Generated**: October 7, 2025 (Evening)
**Branch**: feature/senior-ux-redesign
**Target Version**: 2.3.0
**Estimated Completion**: 2 weeks

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
