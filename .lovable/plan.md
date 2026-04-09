

## Plan: Add announcement banner to Navbar

**Single file edit**: `src/components/landing/Navbar.tsx`

Wrap the existing `<nav>` element in a fragment (`<>...</>`) and place the provided banner `<div>` above it. The banner has `position: relative` (not fixed), so the `<nav>` with `position: fixed` will need its `top` adjusted when the banner is visible.

Since the banner uses `document.getElementById` to hide itself (DOM manipulation), the nav's `top` won't auto-adjust. The simplest approach matching the user's exact HTML: wrap in a fragment, add the banner div verbatim above the nav, and make the banner also fixed with `z-index` above the nav. The nav's `top` should shift down by the banner height when visible.

**Simpler approach** (matching user intent for "slim banner above navbar"): Use React state to track banner visibility, render the banner as a fixed element above the nav, and adjust nav `top` accordingly.

**Implementation**:
1. Add `bannerVisible` state (default `true`)
2. Render the banner `<div>` above `<nav>` inside a fragment, using `position: fixed; top: 0; z-index: 51`
3. Set nav's `top` to the banner height (~38px) when banner is visible, `0` when dismissed
4. Close button sets `bannerVisible` to `false`
5. All other code remains untouched

