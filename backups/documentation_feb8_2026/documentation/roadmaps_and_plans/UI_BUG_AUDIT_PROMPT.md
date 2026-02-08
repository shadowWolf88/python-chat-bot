# UI BUG AUDIT & FIX PROMPT - Healing Space UK

You are auditing and fixing ALL UI bugs in Healing Space UK, an NHS-aligned mental health web application. The entire frontend lives in a single file: `templates/index.html` (~15,800 lines). The backend API is `api.py` (~15,600 lines). This is a Flask + PostgreSQL app deployed on Railway.

## YOUR MISSION

Systematically find and fix every UI bug in the application. Do NOT skip any section of the frontend. Do NOT introduce new features. Do NOT refactor working code. ONLY fix bugs. Every fix must be tested by reading surrounding code to confirm it won't break something else.

---

## PROJECT CONTEXT

### Architecture
- **Single-page app:** Everything is in `templates/index.html` - HTML, CSS, and JavaScript
- **Tab-based navigation:** Main tabs switched via `switchTab(tabName, buttonEl)`
- **Clinical subtabs:** Professional dashboard has subtabs via `switchClinicalTab(subtabName, buttonEl)` - constructs element ID as `'clinical' + subtabName.charAt(0).toUpperCase() + subtabName.slice(1) + 'Tab'`
- **Patient detail subtabs:** `switchPatientTab(subtabName, buttonEl)` - same ID construction pattern
- **Role-based UI:** Three roles: `user` (patient), `clinician`, `developer` - tabs shown/hidden based on role
- **Authentication:** `currentUser` and `currentUserRole` JS globals set on login
- **API calls:** All authenticated fetch calls MUST include `credentials: 'include'`
- **CSS variables:** Uses `var(--bg-card)`, `var(--text-secondary)`, `var(--accent-color)`, etc.
- **Dark mode:** `[data-theme="dark"]` CSS selectors

### Key Functions You Must Understand Before Fixing
```
switchTab(tabName, buttonEl)          - Main tab switching
switchClinicalTab(subtabName, btn)    - Clinical subtab switching
switchPatientTab(subtabName, btn)     - Patient detail subtab switching
completeLogin()                       - Post-login initialization
get_authenticated_username()          - Backend auth (Flask session)
loadHomeTabData()                     - Home tab data loading
initializeWellnessRitual()            - Wellness check-in flow
loadWinsBoard()                       - Wins feature loading
loadAnalyticsDashboard()              - Clinician analytics
loadPatients()                        - Clinician patient list
loadRiskDashboard()                   - Risk monitor data
```

---

## KNOWN BUG CATEGORIES TO INVESTIGATE

### 1. DUPLICATE ELEMENT IDs (CRITICAL - FIX FIRST)

The file has duplicate element IDs which cause `getElementById()` to return the wrong element. Search for ALL duplicate IDs across the entire file. Known duplicates include:
- `messagesInboxTab` / `messagesSentTab` / `messagesNewTab` - appear in both patient messages tab AND clinician professional messages subtab
- Any other ID that appears more than once

**How to fix:** Suffix with role context, e.g., `messagesInboxTabPatient` vs `clinMessagesInboxTab`. Update ALL JavaScript references to use the correct ID based on context.

### 2. UNDEFINED ELEMENT REFERENCES

Many `document.getElementById('someId')` calls reference elements that don't exist in the HTML. This causes features to silently fail. Search for ALL getElementById calls and verify the target element exists.

Known problem areas:
- Wins Board: `winsPresets`, `winsWeekCount`, `customWinInput`, `recentWinsList`
- Breathing exercises: `breathingTaskInstructions`, `breathingTaskStartBtn`, `breathingDisplay`
- Pet tasks: `petTaskInstructions`, `petTaskBtns`
- CBT form inputs: `cbtSituation`, `cbtThought`, `cbtEvidence`
- Analytics charts: `moodTrendChart`, `phq9Chart`, `gad7Chart`

**How to fix:** Either create the missing HTML elements where they belong, or fix the JavaScript to use the correct existing element IDs.

### 3. BUTTONS NOT WORKING / onclick CALLING WRONG FUNCTION

Audit every `onclick` handler in the HTML. For each one:
- Verify the function exists in the `<script>` block
- Verify the function signature matches the arguments passed
- Verify the function actually does what the button label implies
- Check for typos in function names

Pay special attention to:
- Buttons inside dynamically generated HTML (template literals) - these often have quote escaping issues
- Buttons that pass string arguments with special characters
- Buttons in modals that may be created/destroyed

### 4. MODAL SHOW/HIDE INCONSISTENCIES

The codebase uses THREE different approaches to show/hide elements, causing conflicts:

**Pattern A:** `.classList.add('hidden')` / `.classList.remove('hidden')` - CSS class
**Pattern B:** `.style.display = 'none'` / `.style.display = 'flex'` / `'block'` - inline style
**Pattern C:** `.style.display = ''` - reset to CSS default

**THE BUG:** If an element is hidden with Pattern A (class) but shown with Pattern B (inline style), or vice versa, it breaks. An element with `class="hidden"` AND `style="display: flex"` has unpredictable behavior.

**How to fix:** For each show/hide pair, ensure BOTH the show and hide use the same method. Prefer Pattern B (`.style.display`) for modals and overlays. Prefer Pattern A (`.classList`) for form sections and auth flows.

### 5. FETCH CALLS MISSING `credentials: 'include'`

Every `fetch()` call to an authenticated API endpoint MUST include `credentials: 'include'` in the options object. Without it, the Flask session cookie isn't sent and the request fails with 401.

Search for ALL `fetch(` calls in the file. For each one that hits a `/api/` endpoint, verify it includes `credentials: 'include'`. Known missing locations include:
- Pet-related endpoints (`/api/pet/*`)
- Chat history endpoint (`/api/therapy/history`)
- Chat sessions endpoint (`/api/therapy/sessions`)
- Developer endpoints (`/api/developer/*`)
- Some notification endpoints

**How to fix:** Add `credentials: 'include'` to the fetch options object.

### 6. ROLE-BASED TAB VISIBILITY BUGS

The `completeLogin()` function shows/hides tabs based on `currentUserRole`. Check:
- Are all patient-only tabs hidden for clinicians?
- Are all clinician-only tabs hidden for patients?
- Are developer-only tabs hidden for non-developers?
- When switching roles (logging out and back in as different role), do stale tabs remain visible?
- Do tabs use consistent display values (`inline-block` vs `block` vs `flex`)?

### 7. BUTTON STYLING ISSUES

`.btn` class has `width: 100%` by default. This means ANY button with class `btn` will stretch to full width unless overridden. Check:
- Action buttons in flex containers (acknowledge, resolve, etc.) - these need `width: auto`
- Inline button groups (filter buttons, tab buttons) - need `width: auto`
- Buttons inside cards that should be side-by-side
- Submit buttons that correctly should be full-width

### 8. TAB CONTENT NOT LOADING ON SWITCH

When a user switches tabs, data should load for that tab. Check:
- Does `switchTab()` call the correct data loading function for each tab?
- Does `switchClinicalTab()` call loading functions for all subtabs (including riskmonitor)?
- Are there race conditions where data loads before the DOM element is visible?
- Do loading spinners/placeholders get replaced with actual content?

### 9. FORM SUBMISSION BUGS

For every form in the app (login, register, mood log, CBT tools, assessments, messages, etc.):
- Does the submit button call the right function?
- Does the function collect all form field values?
- Does it validate inputs before sending?
- Does it show success/error feedback to the user?
- Does it clear the form after successful submission?
- Does it prevent double-submission?

### 10. DARK MODE COMPATIBILITY

Elements with hardcoded colors (not using CSS variables) will look wrong in dark mode. Check:
- Inline `style="color: #333"` or `background: white` - these won't adapt to dark mode
- Dynamically generated HTML with hardcoded colors
- Border colors that don't use variables
- Text that becomes invisible against dark backgrounds

---

## HOW TO WORK

### Step 1: Read the full file structure
Read `templates/index.html` in sections (500 lines at a time) to build a mental map of:
- Where each tab's HTML content lives
- Where each JavaScript function is defined
- What CSS classes and inline styles are used

### Step 2: Systematic audit
Go through each of the 10 bug categories above. For each category:
1. Search for ALL instances of the pattern
2. Verify each instance is correct
3. Fix any bugs found
4. Document what you fixed

### Step 3: Cross-reference
After individual fixes, verify:
- No function calls reference renamed/moved elements
- No duplicate IDs remain
- Show/hide pairs are consistent
- All fetch calls have credentials

### Step 4: Verify nothing is broken
After all fixes:
- Read through `switchTab()` flow for each tab
- Read through `completeLogin()` to verify initialization
- Read through each modal open/close flow
- Verify all onclick handlers still reference valid functions

---

## CRITICAL RULES

1. **Read before editing.** Always read the surrounding 50+ lines of code before making any change.
2. **One bug category at a time.** Don't try to fix everything in one pass.
3. **Don't rename functions** unless they have a typo. Other code may depend on the name.
4. **Don't change API contracts.** If a fetch call sends `{username: currentUser}`, keep that format.
5. **Don't add features.** No new buttons, no new modals, no new styles. Only fix what's broken.
6. **Don't remove code** unless it's truly dead (unreachable). Some code may look unused but is called dynamically.
7. **Preserve inline styles** on elements that have them. The codebase uses inline styles extensively - don't refactor to CSS classes.
8. **Test dark mode.** Any color you hardcode must also work in `[data-theme="dark"]`.
9. **Use `var()` for colors** when adding any new color values.
10. **Keep `.btn` overrides.** When adding `width: auto` to buttons, do it via inline style, not by changing the `.btn` class.

## DATABASE CONNECTION RULES (if touching api.py)
- Always use `get_wrapped_cursor(conn)` - NEVER `conn.cursor()`
- Use `%s` for PostgreSQL placeholders (NOT `?`)
- Subqueries in FROM must have `AS alias`
- Use `handle_exception(e, 'endpoint_name')` for error handling
- All POST/PUT/DELETE need `@CSRFProtection.require_csrf`
- Use `credentials: 'include'` on ALL frontend fetch calls

---

## OUTPUT FORMAT

For each bug fixed, report:
```
BUG #N: [Category] Short description
FILE: templates/index.html (or api.py)
LINE: approximate line number
BEFORE: the problematic code
AFTER: the fixed code
REASON: why this was a bug and how the fix resolves it
```

After all fixes, provide a summary count:
- Total bugs found
- Total bugs fixed
- Any bugs found but intentionally not fixed (with reason)
