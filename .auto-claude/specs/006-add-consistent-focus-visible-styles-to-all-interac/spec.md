# Add consistent focus-visible styles to all interactive elements

## Overview

Add visible focus ring styles to buttons, tabs, and clickable elements for keyboard navigation accessibility. Currently only form inputs have focus:ring-2 styling while buttons like ViewTab, QuickFilterChip, and ThemeToggle lack visible focus indicators.

## Rationale

Users who navigate with keyboards (including accessibility users) cannot see which element is currently focused, making the application inaccessible for keyboard-only navigation. This is a WCAG 2.1 Level AA requirement.

---
*This spec was created from ideation and is pending detailed specification.*
