# UI Improvements - January 2026

## Changes Made

### 1. Smart Quit Message (Scrap vs. End Early)

**What changed:**
- The quit control message now adapts based on session duration
- Shows `[q] quit (scrap)` when session is below abandon threshold (default 5 min)
- Shows `[q] quit (end early)` when session is above abandon threshold

**Why:**
- Makes it immediately clear whether quitting will log the session or not
- "Scrap" indicates the session won't be saved to history
- "End early" indicates the session will be logged as abandoned

**Before:**
```
[q] quit (end early)   [d] detach
```
Always showed "end early" regardless of duration.

**After:**
```
# At 2 minutes (< 5 min threshold)
[q] quit (scrap)   [d] detach

# At 7 minutes (> 5 min threshold)  
[q] quit (end early)   [d] detach
```

**Implementation:**
```python
# Check elapsed time against abandon threshold
abandon_threshold_minutes = self.config.abandon_threshold_minutes
elapsed_minutes = elapsed / 60

if elapsed_minutes < abandon_threshold_minutes:
    console.print("[dim][q] quit (scrap)   [d] detach[/dim]")
else:
    console.print("[dim][q] quit (end early)   [d] detach[/dim]")
```

---

### 2. Monthly Stats Show Weekly Breakdown

**What changed:**
- Monthly statistics now show breakdown by week instead of by day
- Weeks start on Monday (ISO standard)
- Format: `Jan 05-11    11h 40m (14 sessions)  ████████`

**Why:**
- Daily breakdown for a full month is too verbose (31 lines)
- Weekly view is more digestible and useful for trends
- Aligns with how most people think about productivity (weekly patterns)

**Before:**
```
Daily breakdown:

Mon 01     ████████████████ 3h 15m (6 sessions)
Tue 02     ██████████████████████ 4h 30m (9 sessions)
Wed 03     ████████████ 2h 15m (5 sessions)
... (continues for 31 days)
```

**After:**
```
Weekly breakdown:

Jan 05-11    11h 40m (14 sessions)  ██████████████████████████████
Jan 12-18    11h 40m (14 sessions)  ██████████████████████████████
Jan 19-25    11h 40m (14 sessions)  ██████████████████████████████
Jan 26-01     7h 30m ( 9 sessions)  ███████████████████
```

**Implementation:**
- Group sessions by ISO week (Monday start)
- Format week labels as "Mon DD-DD" showing start and end dates
- Display 4-5 weeks typically for a full month

---

### 3. Numbers Before Bars for Better Readability

**What changed:**
- Duration and session count now appear BEFORE the progress bar
- Right-aligned for clean column layout
- Consistent spacing for visual clarity

**Why:**
- Numbers are more important than bar length
- Reading left-to-right gets the data first
- Easier to scan and compare values
- Bars provide visual context after the numbers

**Before:**
```
Mon 18     ██████████████████ 3h 30m (7 sessions)
Tue 19     ████████████████████████ 4h 15m (8 sessions)
```
Numbers came after bars, harder to read.

**After:**
```
Mon 18    3h 30m (7 sessions)  ██████████████████
Tue 19    4h 15m (8 sessions)  ████████████████████████
```
Numbers come first, then bars provide visual representation.

**Implementation:**
```python
# Weekly stats format
console.print(f"{day_label:10} {format_duration(minutes):>7} ({sessions} sessions)  [cyan]{bar}[/cyan]")

# Monthly stats format  
console.print(f"{week_label:12} {format_duration(minutes):>7} ({sessions:>2} sessions)  [cyan]{bar}[/cyan]")
```

**Formatting details:**
- Day/week label: Left-aligned with fixed width
- Duration: Right-aligned (>7 chars) for column alignment
- Session count: Right-aligned for consistency
- Two spaces before bar for visual separation

---

## Visual Comparison

### Weekly Stats

**Before:**
```
Mon 18     ██████████████████ 3h 30m (7 sessions)
Tue 19     ████████████████████████ 4h 15m (8 sessions)
Wed 20     ██████████████ 2h 45m (6 sessions)
```

**After:**
```
Mon 18    3h 30m (7 sessions)  ██████████████████
Tue 19    4h 15m (8 sessions)  ████████████████████████
Wed 20    2h 45m (6 sessions)  ██████████████
```

### Monthly Stats

**Before:**
```
Daily breakdown:
(31 lines of daily data - too long)
```

**After:**
```
Weekly breakdown:

Jan 05-11    11h 40m (14 sessions)  ██████████████████████████████
Jan 12-18    11h 40m (14 sessions)  ██████████████████████████████
Jan 19-25    11h 40m (14 sessions)  ██████████████████████████████
Jan 26-01     7h 30m ( 9 sessions)  ███████████████████
```

---

## Testing Results

All changes tested and verified:

```
✅ Quit message shows 'scrap' at 2 minutes
✅ Quit message shows 'end early' at 7 minutes
✅ Monthly stats show weekly breakdown
✅ Numbers appear before bars in both views
✅ Formatting is clean and aligned
✅ All unit tests still pass (5/5)
```

**Sample output:**
```
╭──────────────────────────────╮
│ LOCKIN — Stats: January 2026 │
╰──────────────────────────────╯

╭─────────────────────┬─────────╮
│ Metric              │   Value │
├─────────────────────┼─────────┤
│ Focused (completed) │ 46h 40m │
│ Break time          │      0m │
│ Completed sessions  │      56 │
╰─────────────────────┴─────────╯

Weekly breakdown:

Jan 05-11    11h 40m (14 sessions)  ██████████████████████████████
Jan 12-18    11h 40m (14 sessions)  ██████████████████████████████
Jan 19-25    11h 40m (14 sessions)  ██████████████████████████████
Jan 26-01     7h 30m ( 9 sessions)  ███████████████████
```

---

## Documentation Updated

All documentation files updated to reflect changes:

- ✅ `TERMINAL_EXAMPLES.md` - All examples updated
- ✅ `README.md` - Stats section updated
- ✅ `UI_FLOW.md` - Quit message clarified
- ✅ `USER_GUIDE.md` - References to stats updated

---

## User Impact

**Positive impacts:**
1. **Clearer feedback** - Users know immediately if quitting will save their session
2. **Better monthly view** - Weekly breakdown is more useful than 31 days
3. **Easier reading** - Numbers-first layout scans faster
4. **More professional** - Consistent, clean formatting throughout

**No breaking changes:**
- All existing functionality preserved
- Database schema unchanged
- API unchanged
- Configuration unchanged

---

## Files Modified

1. **`src/lockin/cli.py`** (3 sections modified)
   - Added quit message logic (lines 186-197)
   - Changed weekly stats formatting (line 457 → numbers before bars)
   - Added monthly weekly breakdown (lines 417-460)

2. **Documentation files** (4 files updated)
   - `TERMINAL_EXAMPLES.md`
   - `README.md`
   - `UI_FLOW.md`
   - `USER_GUIDE.md`

**Total lines changed:** ~150 lines across 5 files

---

## Future Considerations

Potential follow-up improvements:

1. **Configurable breakdown granularity**
   - Let users choose daily/weekly for monthly stats
   - Add yearly monthly breakdown

2. **Color coding by productivity**
   - Green for high-productivity days/weeks
   - Yellow for medium
   - Dim for low

3. **Trend indicators**
   - Show ↑ ↓ → for week-over-week changes
   - Highlight personal bests

4. **Smart formatting**
   - Auto-adjust bar length based on terminal width
   - Responsive layout for different screen sizes

---

**All improvements are backward compatible and enhance the user experience without disrupting existing workflows.**
