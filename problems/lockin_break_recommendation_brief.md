# Technical Note --- Break recommendation label inconsistencies (short vs long)

## Problem description

After a work session finishes, the UI is intended to recommend **exactly
one** break type:

-   **short** break most of the time
-   **long** break every `long_break_every` sessions (based on current
    streak)

The user should then be able to choose:

-   the recommended break (`b`),
-   a custom-duration break (`B`),
-   or start a break and later switch between short/long (`s`/`l`) once
    in break mode.

Currently, the UI messaging and the actual "recommended break" behavior
are **not fully consistent across states**.

------------------------------------------------------------------------

## Current behavior in the code

There are two relevant "post-work" states where a break prompt is shown:

### 1) Decision window (`SessionState.AWAITING_DECISION`)

In `_show_decision_controls()` the label is computed from streak:

``` python
streak = self.db.calculate_current_streak()
long_break_every = self.config.long_break_every

if streak > 0 and streak % long_break_every == 0:
    break_label = "long"
else:
    break_label = "short"
```

Then the prompt is printed as:

``` python
[b/B] break ({break_label}/custom)
```

✅ This is aligned with the intended UX: **it shows only one
recommendation** (short *or* long), plus "custom".

### 2) Bonus time (`SessionState.RUNNING_BONUS`)

In `show_running_session()` the prompt is currently hard-coded:

``` python
[b/B] break (short/custom)
```

❌ This ignores the streak logic and always displays **short**, even
when the intended recommendation is long.

------------------------------------------------------------------------

## Action logic vs display logic mismatch

When the user presses `b`, the recommended break duration is computed
here:

``` python
streak = self.db.calculate_current_streak()
if streak % self.config.long_break_every == 0:
    duration = self.config.long_break_minutes
else:
    duration = self.config.short_break_minutes
```

This differs subtly from the display logic used in
`_show_decision_controls()`:

-   display logic uses `streak > 0 and streak % long_break_every == 0`
-   action logic uses `streak % long_break_every == 0` (no `streak > 0`
    guard)

Depending on what `calculate_current_streak()` returns (especially at
streak boundaries / "no streak" cases), the action may recommend a long
break when the display would not, or vice versa.

------------------------------------------------------------------------

## Recommended fix

### A) Make the RUNNING_BONUS prompt streak-based too

In the RUNNING_BONUS UI prompt, compute `break_label` using the same
logic as the decision window and print:

-   `break (short/custom)` **or**
-   `break (long/custom)`

instead of the hard-coded `short/custom`.

### B) Unify break recommendation logic in one helper

To prevent future drift, centralize the recommendation into one
function, e.g.:

-   `get_recommended_break_type(streak) -> "short"|"long"`
-   or `get_recommended_break_duration(streak) -> minutes`

and use it for: - label text in the UI, and - `b` key behavior.

This ensures display and action always agree.

------------------------------------------------------------------------

## Acceptance checks

After the change:

-   In **AWAITING_DECISION**, the prompt always shows **one**
    recommendation: `break (short/custom)` or `break (long/custom)`.
-   In **RUNNING_BONUS**, the prompt also shows the correct streak-based
    recommendation (not hard-coded short).
-   Pressing `b` starts the same break type the UI labels as
    recommended.
-   `B` continues to prompt for a custom duration.
-   Once in break mode, `s`/`l` continue to switch between short and
    long breaks.
