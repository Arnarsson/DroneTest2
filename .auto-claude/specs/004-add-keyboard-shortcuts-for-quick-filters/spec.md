# Add Keyboard Shortcuts for Quick Filters

## Overview

Add keyboard shortcuts for common filter operations following the existing QuickFilterChip pattern: 'A' for airports, 'M' for military, 'T' for today, 'V' for verified (3+), 'R' to reset all filters, 'F' to toggle filter panel.

## Rationale

QuickFilterChip in FilterPanel.tsx already defines the common quick filter toggles (airports, military, today, verified). All action handlers exist - just need keyboard event bindings. The onToggle for filter panel and resetFilters function are already exposed.

---
*This spec was created from ideation and is pending detailed specification.*
