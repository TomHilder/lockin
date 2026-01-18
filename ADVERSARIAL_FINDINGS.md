# Adversarial Testing Findings

## CRITICAL Issues (will break in normal use)

### 1. ✅ Zero-duration sessions accepted
**Test:** `engine.start_session('work', 0)` → Succeeds
**Impact:** Session immediately completes, breaks UI, nonsensical
**Fix needed:** Validate duration > 0 in start_session

### 2. ✅ Invalid session_state strings loaded from database  
**Test:** Manually set `session_state: 'INVALID_STATE'` in DB
**Impact:** Engine loads invalid state, breaks state machine logic
**Fix needed:** Validate state on load, reset to idle if invalid

### 3. ✅ Missing state fields cause issues
**Test:** Save incomplete state dict to database
**Impact:** KeyError when accessing missing fields
**Fix needed:** Merge with default state on load

### 4. ✅ Invalid session_type accepted
**Test:** Manually set `session_type: 'invalid_type'` in DB  
**Impact:** Breaks logic that checks session_type
**Fix needed:** Validate session_type on load

### 5. ✅ Date parsing errors crash CLI
**Test:** `lockin stats week 999999` → ValueError exception
**Impact:** Ugly crash instead of friendly error message
**Fix needed:** Catch ValueError in show_stats, display error message

### 6. ✅ Negative duration not validated
**Test:** `lockin -5` → parsed as negative, not caught
**Impact:** Could cause negative timestamps
**Fix needed:** Validate duration > 0 in CLI before queueing

## MODERATE Issues (could happen with user error)

### 7. ✅ Huge config values accepted
**Test:** `config.set('short_break_minutes', 99999999)`
**Impact:** Nonsensical behavior, UI confusion
**Fix needed:** Add reasonable maximum (e.g., 1440 min = 24 hours)

### 8. ⚠️ Stats period validation missing
**Test:** `lockin stats invalid_period`
**Impact:** Crash or weird behavior
**Status:** Already handled - prints "Invalid period"

### 9. ✅ Config key validation missing
**Test:** `lockin config totally_invalid_key 5`
**Impact:** Creates arbitrary keys in database
**Fix needed:** Validate key exists in DEFAULT_CONFIG

## LOW Issues (unlikely or by design)

### 10. ⚠️ Multiple engine instances possible
**Test:** Start two Engine objects
**Impact:** Conflicting sessions possible
**Mitigation:** LaunchAgent ensures single instance
**Fix:** Could add lock file, but low priority

### 11. ⚠️ Command queue buildup if engine crashes
**Test:** Queue 100 commands, never process
**Impact:** Stale commands accumulate
**Mitigation:** cleanup_old_commands() exists
**Fix:** Could auto-cleanup old unprocessed commands, low priority

### 12. ⚠️ No thread safety
**Test:** Multi-threaded engine operations
**Impact:** Race conditions
**Mitigation:** Design is single-threaded
**Status:** Not needed

## NON-Issues (work correctly)

### ✅ Exactly 60-minute gap in streak
**Test:** Sessions 60 minutes apart
**Result:** Correctly breaks streak (gap >= 60)

### ✅ Float precision and overflow
**Test:** Sessions with durations of millions of minutes
**Result:** Python handles correctly, no overflow

### ✅ Unicode and SQL injection
**Test:** Special characters, emoji, SQL injection attempts
**Result:** Parameterized queries prevent injection, unicode works

### ✅ Database corruption detection
**Test:** Corrupt database file
**Result:** SQLite detects and rejects

### ✅ Abandoned sessions don't break streak
**Test:** Completed → Abandoned → Completed
**Result:** Streak continues correctly per spec

### ✅ Out-of-order session insertion
**Test:** Insert sessions in random order
**Result:** Database orders by end_time, works correctly

## Summary

**Must Fix (6):** Issues 1-6, 7, 9
**Should Fix (0):** -
**Optional (3):** Issues 10, 11
**No Fix Needed (6):** All non-issues

## Realistic Encounterability Assessment

| Issue | Realistic? | Scenario |
|-------|-----------|----------|
| 1. Zero duration | YES | User typo: `lockin 0` |
| 2. Invalid state | MAYBE | Database corruption, manual edit |
| 3. Missing fields | MAYBE | Upgrade bug, manual edit |
| 4. Invalid type | MAYBE | Database corruption, manual edit |
| 5. Date parse crash | YES | User typo: `lockin stats week 320145` |
| 6. Negative duration | NO | Shell parses `-5` as flag, not arg |
| 7. Huge config | YES | User typo: `lockin config short_break_minutes 5000` |
| 9. Invalid config key | YES | User typo: `lockin config shot_break_minutes 5` |
| 10. Multiple engines | UNLIKELY | Repeated installation, manual launch |
| 11. Command buildup | UNLIKELY | Engine crash for days |

**8 issues require fixes**
