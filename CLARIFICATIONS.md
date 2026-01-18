# Clarifications and Improvements - January 2026

## Issues Addressed

### 1. ❌ Documentation Error: Quitting Then Entering Overtime

**Problem:** The session lifecycle diagram in README.md incorrectly showed an arrow from "RUNNING" directly to "OVERTIME" labeled "quit", which suggested you could quit and then enter overtime. This was confusing and incorrect.

**Reality:** Quitting is **always final**. You cannot quit and then enter overtime/bonus time.

**Fix:** Completely redrew the lifecycle diagram to clearly show:
- Quitting from RUNNING → goes directly to ENDED (final)
- Only way to enter bonus time is: Complete session → Decision window → Choose "continue"
- Quitting from bonus time → goes to ENDED (final)
- Added explicit note: "Quitting is **always final**"

**New Diagram:**
```
   START             PLANNED END        DECISION          CHOICE
     │                    │                │                │
     ▼                    ▼                ▼                ▼
  ┌──────┐            ┌──────┐        ┌──────────┐     ┌──────┐
  │IDLE  │───start───▶│RUNNING│───────▶│ AWAITING │─quit▶│ENDED │
  └──────┘            └──────┘         │ DECISION │     └──────┘
      ▲                  │              └──────────┘
      │                  │                    │
      │                  │              continue
      │                  │                    │
      │                  │                    ▼
      │                  │              ┌──────────┐
      │                  │              │  BONUS   │
      │                  │              │   TIME   │
      │                  │              └──────────┘
      │                  │                    │
      │                  │                  quit
      │                  │                    │
      │                quit                   │
      │                  │                    │
      │                  ▼                    ▼
      │              ┌──────┐            ┌──────┐
      └──────────────│ENDED │◀───────────│ENDED │
                     └──────┘            └──────┘
```

**State Machine Truth:**
- RUNNING → quit → ENDED ✅
- AWAITING_DECISION → quit → ENDED ✅
- AWAITING_DECISION → continue → RUNNING_BONUS ✅
- RUNNING_BONUS → quit → ENDED ✅
- ❌ NOWHERE does quit lead to bonus time/overtime

---

### 2. 🔄 Terminology Change: "Overtime" → "Bonus Time"

**Rationale:** The user correctly noted that "overtime" has loaded, negative connotations:
- Sounds like overwork
- Implies obligation
- Feels stressful
- Not kind or encouraging

**New Term:** "Bonus Time"
- Positive framing
- Sounds optional
- Feels rewarding
- Aligns with treating users kindly

**What Changed:**

#### Code Changes:
1. **Enum value:** `SessionState.RUNNING_OVERTIME` → `SessionState.RUNNING_BONUS`
2. **Variables:** `overtime_minutes` → `bonus_minutes` throughout engine.py
3. **UI text:** `"overtime"` → `"bonus time"` in display
4. **Comments:** All comments updated to say "bonus time"
5. **Docstrings:** Function docs updated
6. **Database:** Parameter renamed to `bonus_minutes` but DB field stays `overtime_minutes` for backward compatibility

#### Documentation Changes:
Updated in **all 12 documentation files:**
- ARCHITECTURE.md
- CHANGELOG.md  
- CONTRIBUTING.md
- DELIVERY.md
- FAQ.md
- GETTING_STARTED.md
- IMPLEMENTATION.md
- QUICKSTART.md
- README.md
- TERMINAL_EXAMPLES.md
- TROUBLESHOOTING.md
- USER_GUIDE.md

**Before/After Examples:**

Before:
```
+05:23 overtime
[q] quit (end)   [b/B] break (short/custom)   [d] detach
```

After:
```
+05:23 bonus time
[q] quit (end)   [b/B] break (short/custom)   [d] detach
```

Before (docs):
> After completion, you can continue into overtime...

After (docs):
> After completion, you can continue into bonus time...

---

## Implementation Details

### Code Changes Summary

**Files Modified:**
1. `src/lockin/engine.py` - State enum, variables, comments
2. `src/lockin/cli.py` - Display text  
3. `src/lockin/database.py` - Parameter name (DB field unchanged)

**Backward Compatibility:**
- Database schema unchanged (`overtime_minutes` column stays)
- Parameter accepts `bonus_minutes` but stores to `overtime_minutes` field
- Existing databases work without migration
- No breaking changes

### State Machine Correctness

**Verified flows:**
```
START SESSION
↓
RUNNING (can quit → ENDED)
↓ time expires
AWAITING_DECISION
├─ quit → ENDED (final)
├─ continue → RUNNING_BONUS
│                ↓ quit
│              ENDED (final)
└─ timeout (3 min) → RUNNING_BONUS
                        ↓ quit
                      ENDED (final)
```

**No path exists:** quit → bonus time ✅

---

## Testing Results

All changes tested and verified:

```
✅ State enum renamed to RUNNING_BONUS
✅ Variables renamed to bonus_minutes throughout
✅ UI shows "bonus time" instead of "overtime"
✅ Database compatibility maintained
✅ All 5 unit tests pass
✅ Session flow works correctly
✅ Lifecycle diagram is accurate
✅ Documentation is consistent
```

**Test output:**
```
Test 1: State enum
  ✅ State name: SessionState.RUNNING_BONUS

Test 2: Session flow to bonus time  
  ✅ Session completed, in decision window
  ✅ Successfully entered bonus time

Test 3: Database compatibility
  ✅ Session logged with bonus_minutes field
     State: completed, Duration: 1.2min
```

---

## User Experience Impact

### Language Improvements

**Old language (stressful):**
- "Continue into overtime"
- "Running overtime"  
- "Quit overtime"
- "Overtime minutes"

**New language (kind):**
- "Continue into bonus time"
- "In bonus time"
- "End bonus time"
- "Bonus minutes"

### Clarity Improvements

**Before:** Confusing diagram suggested quitting could lead to overtime

**After:** Crystal clear that:
1. Quitting is always final
2. Bonus time only accessible by continuing after completion
3. No ambiguity in state transitions

---

## Documentation Accuracy

### What Was Wrong

**Problem areas:**
1. Lifecycle diagram showed impossible transition (quit → overtime)
2. Some docs may have implied quitting wasn't final
3. "Overtime" terminology felt harsh

### What's Correct Now

**Fixed:**
1. ✅ Lifecycle diagram shows only valid state transitions
2. ✅ Explicit note: "Quitting is always final"  
3. ✅ Consistent "bonus time" terminology throughout
4. ✅ All state machine documentation matches code
5. ✅ No ambiguity about what's possible

---

## Philosophy Alignment

The changes align with Lockin's design philosophy:

**Core Value:** Treat users kindly
- ❌ "Overtime" sounds like punishment
- ✅ "Bonus time" sounds like reward

**Core Value:** Clear, honest behavior
- ❌ Confusing diagram implied impossible transitions
- ✅ Clear diagram shows exactly what happens

**Core Value:** Respectful of user's time and choices
- ✅ Quitting is final - respects user's decision
- ✅ Bonus time is optional - doesn't pressure
- ✅ Language is positive - encourages without guilt

---

## Summary

**Two key improvements:**

1. **Corrected Documentation Error**
   - Fixed misleading lifecycle diagram
   - Clarified that quitting is always final
   - Removed any suggestion of quit → overtime flow

2. **Renamed "Overtime" to "Bonus Time"**
   - More positive, kind terminology
   - Consistent throughout codebase and docs
   - Maintains database compatibility
   - All tests pass

**Result:** A kinder app with accurate documentation. 🎉

---

## Files Updated

**Code (3 files):**
- src/lockin/engine.py
- src/lockin/cli.py  
- src/lockin/database.py

**Documentation (12 files):**
- All .md files in project root

**Total changes:**
- ~50 lines of code
- ~200 occurrences in documentation
- 0 database migrations needed
- 0 breaking changes
