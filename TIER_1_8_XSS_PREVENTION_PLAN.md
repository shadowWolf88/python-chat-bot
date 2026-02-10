# TIER 1.8: XSS Prevention - Implementation Plan

**Status**: STARTING  
**Priority**: HIGHEST (Final security gap in TIER 1)  
**Effort**: 12 hours  
**Files**: templates/index.html (143 innerHTML instances found)

---

## 📋 AUDIT RESULTS

### Total Findings
- **Total innerHTML uses**: 143
- **Categories identified**:
  1. **User-generated content** (HIGH RISK) - 45 instances
     - Pet names, pet messages
     - Mood entries, wellness notes
     - Chat messages, therapy notes
     - Community posts, safety plans
  
  2. **Dynamic HTML templates** (MEDIUM RISK) - 68 instances
     - Goal cards, CBT tool listings
     - Daily tasks, appointments
     - Notification items, approval cards
  
  3. **Loading/error messages** (LOW RISK) - 18 instances
     - Error states, loading spinners
     - Empty state messages
  
  4. **Trusted content** (NO RISK) - 12 instances
     - App icons, internal UI elements
     - Hardcoded HTML structures

---

## 🛡️ MITIGATION STRATEGY

### Approach by Category

#### Category 1: User-Generated Content (45 instances) - USE textContent
**Risk**: Stored XSS if user input contains `<script>`, `<img onerror>`, etc.  
**Fix**: Use `textContent` or `innerText` instead of `innerHTML`  
**Affected**:
- Pet names/messages (5 instances)
- Mood logs/notes (8 instances)
- Chat messages (12 instances)
- Therapy notes (6 instances)
- Community posts (8 instances)
- Safety plans (6 instances)

**Implementation**:
```javascript
// WRONG (vulnerable):
petName.innerHTML = userInput;

// RIGHT (safe):
petName.textContent = userInput;
```

#### Category 2: Dynamic HTML Templates (68 instances) - USE DOMPurify or Safe Creation
**Risk**: Moderate if templates include unvalidated user data  
**Fix**: Use template literals with textContent + createElement, or DOMPurify  
**Affected**:
- CBT tool cards (8 instances)
- Goal progress displays (6 instances)
- Task lists (5 instances)
- Notification items (10 instances)
- Approval cards (8 instances)
- Chart/stat displays (15 instances)
- Tab headers (8 instances)
- Other dynamic lists (8 instances)

**Implementation**:
```javascript
// Option A: Use createElement (safest)
const div = document.createElement('div');
div.textContent = templateContent;
container.appendChild(div);

// Option B: Use DOMPurify if HTML needed
container.innerHTML = DOMPurify.sanitize(templateHtml);
```

#### Category 3: Loading/Error Messages (18 instances) - LOW PRIORITY
**Risk**: Low (controlled messages)  
**Fix**: Convert to textContent where possible, keep innerHTML for hardcoded messages  
**Affected**:
- Loading spinners (5 instances)
- Error messages (7 instances)
- Empty state messages (6 instances)

#### Category 4: Trusted Content (12 instances) - NO ACTION
**Risk**: None (hardcoded, no user data)  
**Fix**: Acceptable to leave as-is, document as approved  
**Affected**:
- App logos/icons (4 instances)
- UI structure elements (8 instances)

---

## 📝 IMPLEMENTATION CHECKLIST

### Phase 1: Preparation (1 hour)
- [ ] Create feature branch: `git checkout -b tier-1-8-xss-prevention`
- [ ] Install DOMPurify via CDN or npm
- [ ] Create backup: `cp templates/index.html templates/index.html.backup`
- [ ] Document baseline: `grep -n "innerHTML" templates/index.html > xss_audit_baseline.txt`

### Phase 2: Fix High-Risk User-Generated Content (5 hours)
- [ ] Pet name/message display (lines 5078-5099)
- [ ] Mood entry rendering (lines 6624, 7072)
- [ ] Chat message display (lines 9316, 9987)
- [ ] Therapy notes rendering
- [ ] Community post display
- [ ] Safety plan content
- [ ] Test each fix: `pytest tests/backend/test_security.py::TestXSSPrevention`

### Phase 3: Fix Medium-Risk Dynamic Templates (4 hours)
- [ ] CBT tool cards (lines 4918-4945)
- [ ] Goal progress (lines 5180-5235)
- [ ] Daily tasks (lines 6834-6911)
- [ ] Notifications (lines 9775-9790)
- [ ] Approval cards (lines 9895-9912)
- [ ] Charts/stats rendering
- [ ] Test each fix: `pytest tests/backend/test_security.py::TestXSSPrevention`

### Phase 4: Review & Testing (1.5 hours)
- [ ] Run all security tests: `pytest tests/backend/test_security.py -v`
- [ ] Manual XSS testing in browser:
  - Inject `<script>alert('XSS')</script>` into pet name
  - Inject `<img src=x onerror=alert('XSS')>` into mood note
  - Inject `javascript:alert('XSS')` into URLs
  - Verify no alerts/popups occur
- [ ] Code review: Check all innerHTML → textContent conversions
- [ ] Update documentation

### Phase 5: Commit & Push (0.5 hours)
- [ ] Run full test suite: `pytest tests/ -q`
- [ ] Commit: `git commit -m "feat: TIER 1.8 XSS Prevention - all 143 innerHTML instances fixed"`
- [ ] Push: `git push origin tier-1-8-xss-prevention`
- [ ] Create PR with security testing notes

---

## 🧪 TEST STRATEGY

### Unit Tests to Add
Create `tests/backend/test_xss_prevention.py`:

```python
class TestXSSPrevention:
    """Verify XSS vulnerabilities are patched"""
    
    def test_pet_name_xss(self, app):
        """Pet name should not execute JavaScript"""
        malicious = "<script>alert('XSS')</script>"
        with app.test_client() as client:
            # Inject payload
            # Verify no <script> rendered in DOM
    
    def test_mood_note_xss(self, app):
        """Mood notes should escape HTML tags"""
        malicious = "<img src=x onerror=alert('XSS')>"
        # Test that onerror is not executed
    
    def test_chat_message_xss(self, app):
        """Chat messages should not render HTML"""
        malicious = "<svg onload=alert('XSS')>"
        # Test that onload is escaped
    
    def test_innerHTML_replaced_with_textContent(self, app):
        """Verify high-risk innerHTML calls use textContent"""
        # Parse HTML, check all user data is via textContent
    
    def test_domPurify_sanitization(self, app):
        """DOMPurify correctly sanitizes template content"""
        malicious_html = "<div><img src=x onerror=alert('XSS')></div>"
        sanitized = DOMPurify.sanitize(malicious_html)
        assert "<img" not in sanitized or "onerror" not in sanitized
```

### Manual Testing
1. **Pet Name XSS**: Create pet with name `<img src=x onerror="console.log('XSS')">`
   - Verify: No console log appears
   - Verify: Name displays as literal text
   
2. **Mood Note XSS**: Log mood with note `<script>alert('XSS')</script>`
   - Verify: No alert pops up
   - Verify: Note displays as text
   
3. **Chat Message XSS**: Send message `<svg onload=alert('XSS')>`
   - Verify: No alert pops up
   - Verify: Message displays as text

---

## 🔧 IMPLEMENTATION DETAILS

### DOMPurify Setup
```html
<!-- Add to index.html head -->
<script src="https://cdn.jsdelivr.net/npm/dompurify@3.0.6/dist/purify.min.js"></script>
```

### Conversion Pattern Examples

**Pattern 1: User Text → textContent**
```javascript
// Before (vulnerable):
petName.innerHTML = userPetName;

// After (safe):
petName.textContent = userPetName;
```

**Pattern 2: Safe HTML Template → innerHTML + DOMPurify**
```javascript
// Before (potentially vulnerable):
container.innerHTML = `
  <div class="card">
    <h3>${goalTitle}</h3>
    <p>${goalDescription}</p>
  </div>
`;

// After (safe):
const template = `
  <div class="card">
    <h3>${DOMPurify.sanitize(goalTitle)}</h3>
    <p>${DOMPurify.sanitize(goalDescription)}</p>
  </div>
`;
container.innerHTML = DOMPurify.sanitize(template);

// OR even safer:
const card = document.createElement('div');
card.className = 'card';
const title = document.createElement('h3');
title.textContent = goalTitle;
card.appendChild(title);
container.appendChild(card);
```

**Pattern 3: Hardcoded Safe HTML → Keep As-Is**
```javascript
// Safe to keep (no user data):
loader.innerHTML = '<div style="text-align:center;">Loading...</div>';
```

---

## 📊 PROGRESS TRACKING

| Phase | Component | Status | Hours |
|-------|-----------|--------|-------|
| 1 | Setup & backup | ⏳ TODO | 1 |
| 2.1 | Pet names/messages | ⏳ TODO | 1 |
| 2.2 | Mood/wellness data | ⏳ TODO | 1 |
| 2.3 | Chat messages | ⏳ TODO | 1.5 |
| 2.4 | Therapy/safety plans | ⏳ TODO | 1.5 |
| 3.1 | CBT tools/cards | ⏳ TODO | 1 |
| 3.2 | Tasks/notifications | ⏳ TODO | 1.5 |
| 3.3 | Charts/stats | ⏳ TODO | 1 |
| 4 | Testing & review | ⏳ TODO | 1.5 |
| 5 | Commit & push | ⏳ TODO | 0.5 |

**Total**: 12 hours

---

## 🎯 SUCCESS CRITERIA

✅ All 143 innerHTML instances reviewed  
✅ 45 high-risk user-generated content fixed (textContent)  
✅ 68 medium-risk templates fixed (DOMPurify or createElement)  
✅ All security tests passing  
✅ XSS payloads tested in browser (no execution)  
✅ Code committed with detailed message  
✅ Zero security warnings in final scan

---

## 📌 NOTES

- DOMPurify config: Default settings sufficient (removes `<script>`, event handlers)
- textContent preferred over innerText (better browser compatibility)
- Test in Chrome DevTools: Check "Disable JavaScript" to verify payloads aren't executed
- Keep backup HTML file for reference during refactoring

---

**Next**: Start Phase 1 - Create branch, install DOMPurify, backup files
