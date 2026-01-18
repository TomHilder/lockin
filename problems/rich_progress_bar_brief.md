# Technical Note --- Make the progress bar visually meaningful

## Problem description

The UI currently shows a *fill-only* progress bar, e.g.:

    ███████████████

As time elapses the bar grows from left to right, but **there is no
visible empty region or frame**. Because the total scale is not visible,
users cannot visually judge what fraction of the session has elapsed ---
the bar reads more like a decorative divider than a progress indicator.

In short: the logic is correct, but the *visual encoding* of progress is
poor.

## Where this comes from in the code

The current rendering prints only the filled portion:

``` python
bar_length = 40
filled = int(bar_length * progress_pct / 100)

bar = (
    "█" * filled
    + "▌" * (1 if progress_pct % (100/bar_length) > 0 and filled < bar_length else 0)
)

console.print(f"[cyan]{bar}[/cyan]")
```

Because only `filled` characters are shown, the viewer never sees the
remaining space up to 40 characters.

## Recommended fix (minimal, preferred)

Keep the same width and style, but **render both filled and empty
portions** with different characters.

Suggested convention:

-   Filled: `█`
-   Empty: `░` (dim or default)

Conceptual change:

``` python
bar_length = 40
filled = int(bar_length * progress_pct / 100)
empty = bar_length - filled

bar = (
    "█" * filled
    + "▌" * (1 if progress_pct % (100/bar_length) > 0 and filled < bar_length else 0)
    + "░" * max(0, empty - 1)   # remainder in a faint block
)

console.print(f"[cyan]{bar}[/cyan]")
```

Example appearance at \~25%:

    ██████████░░░░░░░░░░░░░░░░░░░░░░░░░░

This immediately makes the proportion of elapsed time legible while
preserving a very minimal aesthetic.

## Alternatives (not required)

-   Add a thin frame: `[██████░░░░]`
-   Add endpoints: `|██████░░░░|`
-   Add a numeric percentage (e.g., `37%`)

These are optional; the filled/empty approach above is the recommended
default.

## What should change in the project

Update only the **bar construction logic** in `show_running_session` (or
its future `make_running_renderable`) to include an explicit empty
region. No changes are needed to timing, percentage calculation, or
session logic.

## Acceptance check

The fix is correct when:

-   The bar is always 40 characters wide.
-   As time increases, filled characters grow and empty characters
    shrink.
-   A user can visually estimate "about how far along" without reading
    any numbers.
