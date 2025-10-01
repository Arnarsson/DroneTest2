# DroneWatch Preview Testing Checklist

## 🎨 Brand Identity
- [ ] Logo displays correctly in light mode (dark navy)
- [ ] Logo displays correctly in dark mode (bright cyan)
- [ ] Tagline reads "Safety Through Transparency"
- [ ] Logo scales properly on mobile (<400px)
- [ ] Tagline hides on medium screens (<768px)

## 🎯 Evidence Badges
- [ ] **LIST VIEW**: Evidence badges show with icons
  - [ ] Score 4: Green "OFFICIAL" with shield
  - [ ] Score 3: Yellow "VERIFIED" with checkmark
  - [ ] Score 2: Orange "REPORTED" with alert
  - [ ] Score 1: Red "UNCONFIRMED" with question mark
- [ ] **MAP VIEW**: Evidence badges in popups match
- [ ] Hover tooltips explain methodology
- [ ] Badges are clickable/interactive

## 📰 Source Badges
- [ ] **LIST VIEW**: Sources appear with icons
  - [ ] Police sources show 🚔 icon (green)
  - [ ] NOTAM sources show 🛫 icon (blue)
  - [ ] News sources show 📰 icon (yellow)
  - [ ] Favicon loads or emoji fallback shows
- [ ] **MAP VIEW**: Sources appear in popups
- [ ] Source links are clickable
- [ ] Hover shows full URL
- [ ] External link icon visible

## 🔥 Critical - Sources Display
- [ ] **Incident cards** show "Sources" section (not empty)
- [ ] **At least one incident** has visible sources
- [ ] Source count shows (e.g., "4 sources")
- [ ] "+X more" appears if >4 sources

## 📱 Mobile Responsive
- [ ] Logo displays on mobile
- [ ] Evidence badges readable on mobile
- [ ] Source badges don't overflow
- [ ] Touch targets are large enough (≥44px)
- [ ] Filters panel accessible

## 🎨 Theme Switching
- [ ] Toggle dark/light mode works
- [ ] Logo color changes with theme
- [ ] Badge colors maintain contrast
- [ ] No flashing/flickering during switch

## 🚀 Performance
- [ ] Page loads in <3s on desktop
- [ ] No console errors in DevTools
- [ ] Smooth animations (no jank)
- [ ] Map markers load quickly

## ♿ Accessibility
- [ ] Tab navigation works through badges
- [ ] Focus indicators visible
- [ ] Screen reader announces badge labels
- [ ] Color contrast sufficient (check with DevTools)

## 🐛 Known Issues to Watch For
- [ ] Sources array is NOT empty `[]`
- [ ] No "undefined" or "null" in source types
- [ ] Evidence scores are 1-4 (not other values)
- [ ] Map popups don't break on click

---

## Quick Test Script
```javascript
// Run in browser console on preview URL
const checkSources = () => {
  fetch('/api/incidents?limit=5')
    .then(r => r.json())
    .then(data => {
      console.log('✅ Total incidents:', data.length);
      const withSources = data.filter(i => i.sources?.length > 0);
      console.log('✅ With sources:', withSources.length);
      console.log('Sample sources:', data[0]?.sources);
    });
};
checkSources();
```

---

## If Issues Found
1. Note the specific issue
2. Check browser console for errors
3. Take screenshot if visual bug
4. Report in PR #41 comments
5. We can fix in follow-up commit

---

**Expected Results:**
- ✅ All badges display with icons
- ✅ Sources visible (not empty arrays)
- ✅ Logo looks professional
- ✅ Mobile works smoothly
- ✅ No console errors
