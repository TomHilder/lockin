# Technical Note --- Missing `[q]` and other key prompts in Rich output

## Problem description

In the running-session UI, the interface is intended to prompt the user
with key hints such as:

    [q] quit   [d] detach

However, in practice only the words like **`quit`** or **`detach`**
appear on screen --- the bracketed keys (`[q]`, `[d]`, etc.) are
missing.

This is not a terminal issue; it arises from how Rich interprets square
brackets in printed strings.

## Why this happens

The code currently prints lines like:

``` python
console.print("[dim][q] quit (scrap)   [d] detach[/dim]")
```

Rich treats square brackets `[...]` as **markup syntax**.\
Because `q` and `d` are **not valid Rich style tags**, Rich interprets
them as *style names* rather than literal text and silently drops the
bracketed labels from the rendered output.

As a result:

-   Input: `[q] quit`
-   On-screen result: `quit`

This matches exactly what the user is observing.

## Recommended ways to fix it

### Option A --- Escape the brackets (simplest local fix)

Keep markup enabled but escape any *literal* brackets:

``` python
console.print("[dim]\[q\] quit (scrap)   \[d\] detach[/dim]")
```

This tells Rich: "render `[q]` as text, not markup."

### Option B --- Disable markup for that line

``` python
console.print("[q] quit   [d] detach", markup=False)
```

Caveat: this also disables `[dim]...[/dim]` styling on that line, so you
would need to apply dim styling another way (e.g., via `Text`).

### Option C --- Use `Text` objects (robust, long-term)

Construct the line with `rich.text.Text`, which cleanly separates
*content* from *styling* and avoids markup ambiguity entirely:

``` python
from rich.text import Text

t = Text()
t.append("[q] ", style="dim")
t.append("quit   ")
t.append("[d] ", style="dim")
t.append("detach")

console.print(t)
```

## What should change in the project

Wherever the UI shows key prompts like `[q]`, `[b]`, `[B]`, `[c]`,
`[d]`, `[s]`, or `[l]`, choose **either**:

-   Escape all literal brackets in existing f-strings, **or**
-   Migrate those lines to `Text` objects for clearer styling.

No changes are needed to terminal mode, input handling, or key logic ---
only to how these strings are rendered.

## Acceptance check

The fix is correct when lines such as:

    [q] quit   [d] detach

appear exactly as written on screen while still preserving dim/cyan
styling elsewhere in the UI.
