# Technical Brief --- Replace `console.clear()` redraw with Rich `Live`

## Goal

Eliminate UI "flash" during the running session by replacing full-screen
clearing + reprinting with **Rich's `Live` renderer**, which performs
in-place, flicker-free updates.

## What causes the problem today

The current loop does:

``` python
console.clear()
show_running_session(state)
```

once per second.\
This **erases the entire terminal buffer each tick**, which causes
visible flicker on many terminals. The issue is the *clear + full
redraw*, not Rich itself.

## Design decision

Use **`rich.live.Live`** for the *running session screen only*.\
Keep `console.clear()` for static screens (`show_idle_dashboard`,
`show_stats`, `show_config`), which do not update in real time.

## Required architectural change (conceptual)

Shift from:

    state → print side effects

to:

    state → build a Rich renderable → Live updates it

### Introduce a pure renderer

Create a function like:

``` python
def make_running_renderable(self, state: dict) -> Renderable:
    """
    Return a single Rich object (Panel / Layout / Group / etc.)
    representing the entire running-session screen for this state.
    """
```

This function should contain **all layout logic currently inside
`show_running_session`**, but return an object instead of printing.

Allowed building blocks: - `Panel` - `Table` - `Layout` - `Group` -
`Text` / styled strings - The existing progress bar string may be kept
as plain text inside a Panel

## Replace the attach loop with `Live`

Rough target structure (logic preserved, only rendering changes):

``` python
from rich.live import Live

with Live(
    self.make_running_renderable(state),
    refresh_per_second=4,
    screen=True
) as live:

    while True:
        state = self.get_current_state()
        if not state or state['session_state'] in [IDLE, ENDED]:
            console.print("\n[yellow]Session ended[/yellow]")
            break

        live.update(self.make_running_renderable(state))

        # existing non-blocking key handling here (unchanged)
        ...
        time.sleep(1)
```

Key requirements: - **Do NOT call `console.clear()` inside the live
loop.** - All visual changes must come from `live.update(...)`.

## What to do with `show_running_session`

Two acceptable options (pick one):

**Option A --- refactor (preferred)** - Turn `show_running_session` into
`make_running_renderable`. - Move all `console.print(...)` calls into
construction of a single renderable. - Keep interactive key logic in
`attach_to_session` unchanged.

**Option B --- thin wrapper (if refactor is hard)** - Create
`make_running_renderable` that *internally* captures what would have
been printed by `show_running_session` into a Rich container (e.g., a
`Group` or `Layout`), then returns it. - Still remove `console.clear()`
from that path.

## What stays the same

Do **not** change: - Terminal raw mode / `tty.setcbreak` -
`select.select` input handling\
- Command queuing - Sleep cadence (1s is fine) - Database or engine
logic

## Optional polish (nice-to-have, not required)

-   If possible, render the progress bar as a Rich `Progress` or `Bar`
    instead of a manual string, but this is optional --- keep the
    current ASCII bar if simpler.

## Acceptance criteria

The fix is correct when: - The running session screen **no longer
flashes or blanks** each second. - The UI still updates once per
second. - The terminal scrollback is preserved (except when
`screen=True` is chosen). - Static screens (`stats`, `config`, idle
dashboard) can still use `console.clear()`.
