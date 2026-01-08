# QA Fix Request

**Status**: REJECTED
**Date**: 2026-01-07
**QA Session**: 2

## Critical Issues to Fix

### 1. AtlasBadge.tsx - motion.a missing focus-ring

**Problem**: The Atlas Consulting branded link lacks keyboard focus indication
**Location**: frontend/components/AtlasBadge.tsx line 17
**Required Fix**: Add focus-ring class to the motion.a className

Current className:
"group flex items-center bg-black/95 backdrop-blur-xl rounded-xl md:rounded-2xl shadow-lg border border-gray-700/30 px-2 py-1.5 md:px-3 md:py-2 hover:border-gray-600/50 transition-all duration-300"

Should be:
"group flex items-center bg-black/95 backdrop-blur-xl rounded-xl md:rounded-2xl shadow-lg border border-gray-700/30 px-2 py-1.5 md:px-3 md:py-2 hover:border-gray-600/50 transition-all duration-300 focus-ring"

**Verification**: Tab to the Atlas badge link - should show blue focus ring

### 2. EvidenceLegend.tsx - Learn more link missing focus-ring

**Problem**: The Learn more about evidence scoring CTA link lacks focus indication
**Location**: frontend/components/EvidenceLegend.tsx line 96
**Required Fix**: Add focus-ring rounded classes to the anchor className

Current className:
"text-xs text-blue-600 dark:text-blue-400 hover:underline font-medium flex items-center gap-1"

Should be:
"text-xs text-blue-600 dark:text-blue-400 hover:underline font-medium flex items-center gap-1 focus-ring rounded"

**Verification**: Open legend panel, tab to Learn more link - should show blue focus ring

### 3. AboutModal.tsx - GitHub link missing focus-ring (Minor)

**Problem**: The inline GitHub link lacks keyboard focus indication
**Location**: frontend/components/AboutModal.tsx line 219
**Required Fix**: Add focus-ring rounded classes to the anchor className

Current className:
"text-blue-600 dark:text-blue-400 hover:underline font-medium"

Should be:
"text-blue-600 dark:text-blue-400 hover:underline font-medium focus-ring rounded"

**Verification**: Open About modal, tab to GitHub link - should show blue focus ring

## After Fixes

Once fixes are complete:
1. Commit with message: "fix: add focus-ring to remaining interactive links (qa-requested)"
2. QA will automatically re-run
3. Loop continues until approved
