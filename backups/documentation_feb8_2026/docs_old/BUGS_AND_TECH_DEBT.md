# KNOWN ISSUES – Healing Space UK

**Last Updated:** February 7, 2026  
**Status:** All known issues below; no hidden issues expected

---

## 🔴 CRITICAL ISSUES

None currently tracked. All critical issues have been resolved.

**Recent Fixes:**
- ✅ Feb 7: 8 UI bugs (duplicate IDs, modal visibility)
- ✅ Feb 5: 4 database schema issues (pet table, daily_tasks, inbox query)
- ✅ Feb 4: 2 production bugs (AI animation, shared pets)

---

## 🟠 HIGH PRIORITY ISSUES

### 1. Phase 4 Clinical Features Not Yet Implemented
**Impact:** HIGH | **Area:** Clinical Features | **User Impact:** Clinicians missing advanced tools

**Description:**  
The following clinical features are planned but not yet implemented:
- Formal suicide risk assessment (C-SSRS)
- Treatment goals module
- Session notes & homework system
- CORE-OM / ORS outcome measurement
- Relapse prevention planning

**Workaround:** Use basic messaging and mood tracking; manual documentation recommended

**Suggested Fix:**  
Implement Phase 4 in priority order:
1. Suicide risk assessment (CRITICAL for NHS deployment)
2. Treatment goals
3. Session notes & homework
4. Outcome measurement
5. Relapse prevention

**Timeline:** Feb-May 2026

---

### 2. Multi-Language Support Not Available
**Impact:** MEDIUM | **Area:** UI / Localization | **User Impact:** Non-English speakers cannot use the app

**Description:**  
Currently English-only. No i18n/l10n system in place.

**Workaround:** Use browser translation (not ideal)

**Suggested Fix:**  
Implement i18n/l10n system with support for:
- Spanish, French, German, Mandarin (Phase 5)

**Timeline:** Q2 2026

---

### 3. Mobile Apps Not Available
**Impact:** MEDIUM | **Area:** Platform | **User Impact:** Patients must use web browser

**Description:**  
Only web app available. No native iOS/Android apps.

**Workaround:** Use responsive web design on mobile

**Suggested Fix:**  
Build native apps (Phase 5):
- Android (Kotlin + Jetpack Compose)
- iOS (Swift + SwiftUI)

**Timeline:** Q2-Q3 2026

---

## 🟡 MEDIUM PRIORITY ISSUES

### 1. Peer Support Community Not Moderated
**Impact:** MEDIUM | **Area:** Feature | **User Impact:** Safety concerns with unmoderated forum

**Description:**  
Community board exists but lacks moderation tools. Potential for harmful content.

**Workaround:** Don't rely on community for crisis support; use direct clinician messaging

**Suggested Fix:**  
Add moderation dashboard:
- Content flags
- Auto-moderation keywords
- Clinician review queue

**Timeline:** Q2 2026

---

### 2. Accessibility Features Incomplete
**Impact:** MEDIUM | **Area:** UI / Accessibility | **User Impact:** Users with disabilities excluded

**Description:**  
WCAG 2.1 compliance work in progress. Some keyboard navigation gaps exist.

**Known Issues:**
- ❌ Screen reader optimization incomplete
- ❌ Color contrast issues on dark mode buttons
- ❌ Some form fields not keyboard accessible
- ✅ Voice input being developed

**Suggested Fix:**  
Phase 5 accessibility hardening:
- Full keyboard navigation
- ARIA labels for all interactive elements
- Color contrast audit and fixes
- Screen reader testing

**Timeline:** Q2 2026

---

### 3. Limited Integration Options
**Impact:** MEDIUM | **Area:** Integration | **User Impact:** Can't connect with fitness trackers, calendars

**Description:**  
No third-party integrations currently available (Fitbit, Apple Health, Google Calendar, etc.)

**Workaround:** Manual data entry

**Suggested Fix:**  
Add integrations (Phase 6):
- Fitbit / Apple Health sync
- Google Calendar integration
- Spotify for mood-based playlists
- Webhook ecosystem

**Timeline:** Q3 2026

---

### 4. Analytics Limited to Per-Patient View
**Impact:** MEDIUM | **Area:** Reporting | **User Impact:** Clinicians can't see clinic-wide outcomes

**Description:**  
Clinician dashboard shows individual patient progress but not clinic-wide analytics or cohort analysis.

**Workaround:** Manual data aggregation

**Suggested Fix:**  
Add analytics features:
- Clinic-wide outcome reporting
- Cohort analysis
- Therapist effectiveness metrics
- NHS outcome reporting (IAPT compatibility)

**Timeline:** Q2 2026

---

## 🟢 LOW PRIORITY ISSUES

### 1. Gamification Could Be Enhanced
**Impact:** LOW | **Area:** Gamification / UX | **User Impact:** Lower patient engagement

**Description:**  
Pet gamification exists but could be richer:
- Limited mini-games (mostly pet care)
- No achievement badges
- No leaderboards
- Limited customization

**Workaround:** Use for basic motivation; add external gamification

**Suggested Fix:**  
Expand gamification:
- Mini-games library (mood tracking game, relaxation game, memory game)
- Achievement badges
- Weekly challenges
- Pet customization (hats, accessories, colors)

**Timeline:** Q2-Q3 2026

---

### 2. Offline Mode Not Available
**Impact:** LOW | **Area:** Platform / Feature | **User Impact:** Can't use on airplane/offline

**Description:**  
App requires internet connection. No offline mode for mood logging or journaling.

**Workaround:** Use on-device notes app; sync later

**Suggested Fix:**  
Implement offline-first architecture:
- Local IndexedDB caching
- Auto-sync when online
- Available in mobile apps (Phase 5)

**Timeline:** Q2-Q3 2026

---

### 3. Limited Therapy Style Customization
**Impact:** LOW | **Area:** AI / Feature | **User Impact:** AI therapy uses one approach

**Description:**  
AI therapist uses primarily CBT. No customization for patient preference (DBT, ACT, psychodynamic).

**Workaround:** Request specific techniques in chat

**Suggested Fix:**  
Add therapy customization:
- Patient selects preferred style
- AI adjusts prompts and techniques
- Clinician can override preference

**Timeline:** Q2-Q3 2026

---

### 4. Email Notifications Need Improvement
**Impact:** LOW | **Area:** Notifications / Feature | **User Impact:** Users miss alerts

**Description:**  
Email notification system exists but:
- No digest option (daily/weekly)
- No notification preferences UI
- SMS not yet implemented
- Webhook alerts only on high-risk events

**Workaround:** Check app regularly for updates

**Suggested Fix:**  
Improve notifications:
- Notification preferences UI
- Email digests (daily/weekly)
- SMS support
- Push notifications (mobile apps)

**Timeline:** Q2 2026

---

## ⚪ RESOLVED ISSUES (For Reference)

### ✅ Feb 7: 8 UI Bugs Fixed
- Duplicate element IDs in message tabs
- Modal visibility conflicts (shopModal, declutterModal, assessmentModal)
- Inconsistent modal toggle functions
- Button styling inconsistencies

### ✅ Feb 5: Database Schema Issues Fixed
- Pet table NULL ID constraint violation
- Missing daily_tasks table
- SQL syntax error in get_inbox()
- Duplicate function code in initialization

### ✅ Feb 4: Production Bugs Fixed
- AI "thinking" animation displaying escaped HTML
- Shared pet database (now per-user)

### ✅ Feb 1: Security Hardening Complete
- CVSS reduced from 8.5 to 1.6
- CSRF protection implemented
- Input validation complete
- Security headers hardened

---

## 🔧 ISSUE TRACKING

**How to Report Issues:**
1. Check this document first
2. If new, open GitHub issue with:
   - Clear title
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Browser/device info

**How to Propose Features:**
1. Check [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md)
2. If not listed, open feature request with:
   - Clear description
   - Use cases
   - Priority (critical/high/medium/low)
   - Estimated effort

---

## 📊 ISSUE STATISTICS

| Severity | Count | Status |
|----------|-------|--------|
| Critical | 0 | All resolved |
| High | 3 | In roadmap |
| Medium | 4 | In roadmap |
| Low | 4 | Future consideration |
| **Total** | **11** | All tracked |

---

**Last Updated:** February 7, 2026  
**Next Review:** February 28, 2026  
**Owner:** Development Team
