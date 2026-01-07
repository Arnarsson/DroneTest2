# Replace page reload with proper filter reset in empty state

## Overview

The IncidentList empty state 'Reset Filters' functionality uses window.location.reload() instead of calling the filter reset function, causing a full page refresh and losing user context.

## Rationale

Full page reloads are jarring, slow, and cause unnecessary network requests. A proper state reset provides instant feedback and maintains the user's mental context of where they are in the app.

---
*This spec was created from ideation and is pending detailed specification.*
