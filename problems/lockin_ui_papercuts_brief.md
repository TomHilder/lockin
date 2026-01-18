# UI Papercuts & Minor Improvements (Lockin TUI)

This note collects several small UI/UX issues noticed in the current
terminal UI code. These are in the same "papercut" category as the
previously discussed items (screen flicker, missing `[q]` labels,
ambiguous progress bar scale).

Some items below are **real functional issues**; others are **very
minor** and depend on intended behavior. For the minor items, please
sanity-check with broader project context before changing anything.

------------------------------------------------------------------------

## 1) Refresh cadence likely \~2 seconds (functional)

### Symptom

The running-session display appears to update less frequently than
intended and can feel "chunky" (timer ticks late, bar advances in larger
steps).

### Why

In `attach_to_session()` the loop includes both:

-   `select.select(..., timeout=1)` --- which already waits up to 1
    second, **and**
-   `time.sleep(1)` at the bottom --- which adds another second.

In the common "no key pressed" case, the loop often delays about **2
seconds per iteration** (or at least more than 1 second).

### Suggested action

Pick a single pacing mechanism:

-   Use `select` timeout as the tick, **or**
-   Use a short select timeout (e.g. 0--0.1s) and a single `sleep` that
    drives a 1 Hz refresh, **or**
-   Use a "deadline/monotonic" style scheduler (if desired).

(Exact approach depends on how the project wants key responsiveness vs
stable tick timing.)

------------------------------------------------------------------------

## 2) Progress bar width instability (mostly fixed by the "empty region" change)

### Symptom

The progress bar changes length as it fills because only the filled
portion is printed. This can look like the UI is "breathing"
horizontally.

### Why

The bar is rendered as `"█" * filled` (plus optional half block), so the
printed line grows in character count.

### Suggested action

The previously proposed "filled + empty" rendering solves this: always
print a fixed width with a dim empty character.

------------------------------------------------------------------------

## 3) Duplicate decision-window time logic (minor-to-moderate)

### Symptom

Potential future inconsistency / drift risk: decision remaining time is
computed in two places.

### Why

`show_running_session()` computes decision-window `remaining`, and
`_show_decision_controls()` recomputes it again.

### Suggested action

Consider centralizing time computations into a helper
(e.g. `compute_timers(state)`), or compute once and pass the derived
values down.\
This is not urgent but reduces future off-by-one or "one place updated,
other forgotten" issues.

------------------------------------------------------------------------

## 4) Key prompt bracket rendering should be made consistent (functional UX)

### Symptom

Key prompts like `[q]` disappear (user sees only `quit`).

### Why

Rich markup interprets `[q]` as a style tag, not literal text. (See
separate brief.)

### Suggested action

Ensure **all** key prompt strings consistently escape literal brackets
or use `Text` objects. This includes patterns like:

-   `[q]`, `[d]`, `[c]`, `[s]`, `[l]`
-   composite keys like `[b/B]`

------------------------------------------------------------------------

## 5) Time formatting for long bonus sessions (very minor; check intent)

### Symptom

`format_time_remaining()` always uses `MM:SS`. For long bonus time, this
produces e.g. `120:00` for two hours overtime.

### Suggested action (optional)

If desired, switch to `HH:MM:SS` once minutes exceed some threshold, or
reuse `format_duration`-style formatting for bonus time.\
If the project likes the "stopwatch" look, keep as-is.

------------------------------------------------------------------------

## 6) `format_duration` truncates minutes (very minor; check intent)

### Symptom

`format_duration(minutes: float)` uses `int(minutes)` which truncates.
If stored durations can be fractional, the UI may appear to undercount
slightly.

### Suggested action (optional)

Decide whether to floor/round/ceil, or ensure durations are integral
before display.\
If the DB always stores integer minutes, no change needed.

------------------------------------------------------------------------

## 7) Rendering and input handling are tightly coupled (minor; may improve maintainability)

### Symptom

The loop interleaves rendering, timing, and input logic. This is fine
now, but as the UI moves to `Live`, separation tends to reduce timing
bugs and make updates simpler.

### Suggested action (optional)

Consider structuring the main attach loop into clear phases:

1.  Fetch state and render (Live update)
2.  Poll input and enqueue commands
3.  Wait until next tick

Not required, but aligns with the planned `Live` refactor.

------------------------------------------------------------------------

## Summary of priority

**Highest priority (functional / user-visible):** - (1) Fix double-wait
refresh cadence - (4) Fix bracketed key prompts consistently - (2)
Fixed-width progress bar (already planned via empty-region change)

**Lower priority / "check intent":** - (3) De-duplicate decision-window
timing logic - (5) Long bonus-time formatting - (6) Duration
truncation - (7) Loop structure cleanup

------------------------------------------------------------------------

## Acceptance checks

After changes:

-   Running-session UI updates at intended cadence (e.g. \~1 Hz),
    without sluggish ticking.
-   Key prompts show literal bracketed labels (e.g. `[q] quit`).
-   Progress bar remains a constant width and communicates fraction
    elapsed.
-   Any optional changes (time formatting, rounding) match product
    intent.
