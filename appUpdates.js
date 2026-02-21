const APP_UPDATES = [
    {
        "date": "2026-02-21",
        "version": "22.594",
        "title": "Fix: messages inbox 500 + AI summary now includes session notes & treatment plan",
        "changes": [
            "Fix: messages inbox 500 + AI summary now includes session notes & treatment plan"
        ]
    },
    {
        "date": "2026-02-21",
        "version": "22.593",
        "title": "Fix: Mood & Habits tab, AI therapy timestamp, dark mode compose buttons, auto-fill clinician, notification labels",
        "changes": [
            "Fix: Mood & Habits tab, AI therapy timestamp, dark mode compose buttons, auto-fill clinician, notification labels"
        ]
    },
    {
        "date": "2026-02-21",
        "version": "22.592",
        "title": "Fix: deleted messages still appear in patient inbox",
        "changes": [
            "Fix: deleted messages still appear in patient inbox"
        ]
    },
    {
        "date": "2026-02-21",
        "version": "22.591",
        "title": "Fix: PHQ-9 and GAD-7 now create clinician risk alerts on concerning scores",
        "changes": [
            "Fix: PHQ-9 and GAD-7 now create clinician risk alerts on concerning scores"
        ]
    },
    {
        "date": "2026-02-21",
        "version": "22.590",
        "title": "Fix: mood_logs missing exercise_mins/outside_mins/water_pints/sentiment columns",
        "changes": [
            "Fix: mood_logs missing exercise_mins/outside_mins/water_pints/sentiment columns"
        ]
    },
    {
        "date": "2026-02-21",
        "version": "22.589",
        "title": "Fix: Patient tabs all empty + cursor already closed 500 error",
        "changes": [
            "Fix: Patient tabs all empty + cursor already closed 500 error"
        ]
    },
    {
        "date": "2026-02-20",
        "version": "22.588",
        "title": "Fix: mood_logs column name entry_timestamp → entrestamp in all queries",
        "changes": [
            "Fix: mood_logs column name entry_timestamp → entrestamp in all queries"
        ]
    },
    {
        "date": "2026-02-20",
        "version": "22.587",
        "title": "Fix: Patient view 403, clinician.js field names, patient list data",
        "changes": [
            "Fix: Patient view 403, clinician.js field names, patient list data"
        ]
    },
    {
        "date": "2026-02-20",
        "version": "22.586",
        "title": "Fix: Patient role check, PHQ-9/GAD-7 datetime crash, migration ordering",
        "changes": [
            "Fix: Patient role check, PHQ-9/GAD-7 datetime crash, migration ordering"
        ]
    },
    {
        "date": "2026-02-20",
        "version": "22.585",
        "title": "Docs: Update roadmap — mark Phase 1.1/1.2/1.3/1.6 complete, delete prompt doc",
        "changes": [
            "Docs: Update roadmap — mark Phase 1.1/1.2/1.3/1.6 complete, delete prompt doc"
        ]
    },
    {
        "date": "2026-02-20",
        "version": "22.584",
        "title": "Fix + Feat: Phase 1 gaps — CORE-OM/ORS/SRS forms, caseload tracker, goal updates, archive fix, notification headers",
        "changes": [
            "Fix + Feat: Phase 1 gaps — CORE-OM/ORS/SRS forms, caseload tracker, goal updates, archive fix, notification headers"
        ]
    },
    {
        "date": "2026-02-20",
        "version": "22.583",
        "title": "Fix: Remove duplicate Messages button from clinician sidebar",
        "changes": [
            "Fix: Remove duplicate Messages button from clinician sidebar"
        ]
    },
    {
        "date": "2026-02-20",
        "version": "22.582",
        "title": "Feat: SOS/Crisis Button (1.6) + Fix message delete 500",
        "changes": [
            "Feat: SOS/Crisis Button (1.6) + Fix message delete 500"
        ]
    },
    {
        "date": "2026-02-19",
        "version": "22.581",
        "title": "Fix: Allow Google Fonts through Content Security Policy",
        "changes": [
            "Fix: Allow Google Fonts through Content Security Policy"
        ]
    },
    {
        "date": "2026-02-19",
        "version": "22.580",
        "title": "Fix: JS syntax error in renderTreatmentPlanForm — broken nested quotes",
        "changes": [
            "Fix: JS syntax error in renderTreatmentPlanForm — broken nested quotes"
        ]
    },
    {
        "date": "2026-02-18",
        "version": "22.579",
        "title": "Feat: Session Notes (SOAP/BIRP), Treatment Plan Builder, CORE-OM/WEMWBS Outcome Measures",
        "changes": [
            "Feat: Session Notes (SOAP/BIRP), Treatment Plan Builder, CORE-OM/WEMWBS Outcome Measures"
        ]
    },
    {
        "date": "2026-02-18",
        "version": "22.578",
        "title": "Fix: Dark/light theme visibility across all templates and CSS",
        "changes": [
            "Fix: Dark/light theme visibility across all templates and CSS"
        ]
    },
    {
        "date": "2026-02-18",
        "version": "22.577",
        "title": "Fix: dev_jobs table missing on existing production databases",
        "changes": [
            "Fix: dev_jobs table missing on existing production databases"
        ]
    },
    {
        "date": "2026-02-18",
        "version": "22.576",
        "title": "Feat: Complete UI overhaul — new design system across all pages",
        "changes": [
            "Feat: Complete UI overhaul — new design system across all pages"
        ]
    },
    {
        "date": "2026-02-18",
        "version": "22.575",
        "title": "Docs: World-class UI overhaul prompt — 1,100+ lines, meticulous spec",
        "changes": [
            "Docs: World-class UI overhaul prompt — 1,100+ lines, meticulous spec"
        ]
    },
    {
        "date": "2026-02-18",
        "version": "22.574",
        "title": "Fix: Landing page dark mode — no FOUC, hero changes in dark mode",
        "changes": [
            "Fix: Landing page dark mode — no FOUC, hero changes in dark mode"
        ]
    },
    {
        "date": "2026-02-18",
        "version": "22.573",
        "title": "Feat: World-class watermarks + dark mode logos across all pages",
        "changes": [
            "Feat: World-class watermarks + dark mode logos across all pages"
        ]
    },
    {
        "date": "2026-02-18",
        "version": "22.572",
        "title": "Fix: Login page watermark doubled in size (1200px / 92vmin)",
        "changes": [
            "Fix: Login page watermark doubled in size (1200px / 92vmin)"
        ]
    },
    {
        "date": "2026-02-18",
        "version": "22.571",
        "title": "Fix: Watermark now visible — white silhouette on purple gradient backgrounds",
        "changes": [
            "Fix: Watermark now visible — white silhouette on purple gradient backgrounds"
        ]
    },
    {
        "date": "2026-02-18",
        "version": "22.570",
        "title": "Fix: Crisis bar no longer covers nav — watermark added to all dashboards",
        "changes": [
            "Fix: Crisis bar no longer covers nav — watermark added to all dashboards"
        ]
    },
    {
        "date": "2026-02-18",
        "version": "22.569",
        "title": "Feat: World-class landing page — major content and brand upgrade",
        "changes": [
            "Feat: World-class landing page — major content and brand upgrade"
        ]
    },
    {
        "date": "2026-02-18",
        "version": "22.568",
        "title": "Feat: Brand logo + favicon deployed across entire site",
        "changes": [
            "Feat: Brand logo + favicon deployed across entire site"
        ]
    },
    {
        "date": "2026-02-18",
        "version": "22.567",
        "title": "Feat: Email verification required on patient and clinician registration",
        "changes": [
            "Feat: Email verification required on patient and clinician registration"
        ]
    },
    {
        "date": "2026-02-18",
        "version": "22.566",
        "title": "Fix: Rebrand all 'python-chat-bot' references to Healing Space UK",
        "changes": [
            "Fix: Rebrand all 'python-chat-bot' references to Healing Space UK"
        ]
    },
    {
        "date": "2026-02-17",
        "version": "22.565",
        "title": "Feat: At-rest message encryption + Gmail email alerts for high-risk patients",
        "changes": [
            "Feat: At-rest message encryption + Gmail email alerts for high-risk patients"
        ]
    },
    {
        "date": "2026-02-17",
        "version": "22.564",
        "title": "Feat: Tiered pricing section with realistic UK rates + billing toggle",
        "changes": [
            "Feat: Tiered pricing section with realistic UK rates + billing toggle"
        ]
    },
    {
        "date": "2026-02-17",
        "version": "22.563",
        "title": "Feat: AI narrative section, pricing plans, founder card + home button on login",
        "changes": [
            "Feat: AI narrative section, pricing plans, founder card + home button on login"
        ]
    },
    {
        "date": "2026-02-17",
        "version": "22.562",
        "title": "Feat: Interactive landing page enhancements + founder section + home button",
        "changes": [
            "Feat: Interactive landing page enhancements + founder section + home button"
        ]
    },
    {
        "date": "2026-02-17",
        "version": "22.561",
        "title": "Landing Page Tweaks",
        "changes": [
            "Landing Page Tweaks"
        ]
    },
    {
        "date": "2026-02-17",
        "version": "22.560",
        "title": "Feat: Public landing page at / with login route at /login",
        "changes": [
            "Feat: Public landing page at / with login route at /login"
        ]
    },
    {
        "date": "2026-02-17",
        "version": "22.559",
        "title": "Docs: Replace Priority-Roadmap.md with comprehensive world-class roadmap",
        "changes": [
            "Docs: Replace Priority-Roadmap.md with comprehensive world-class roadmap"
        ]
    },
    {
        "date": "2026-02-17",
        "version": "22.558",
        "title": "Fix: Dev inbox field name - use conv.with_user from API response",
        "changes": [
            "Fix: Dev inbox field name - use conv.with_user from API response"
        ]
    },
    {
        "date": "2026-02-17",
        "version": "22.557",
        "title": "Feat: Developer inbox, Post Update feature, notification dark mode",
        "changes": [
            "Feat: Developer inbox, Post Update feature, notification dark mode"
        ]
    },
    {
        "date": "2026-02-17",
        "version": "22.556",
        "title": "Fix: Terminal/console light mode visibility + notification dark mode",
        "changes": [
            "Fix: Terminal/console light mode visibility + notification dark mode"
        ]
    },
    {
        "date": "2026-02-17",
        "version": "22.555",
        "title": "Add High Risk clickable quick-action + clinician tab fixes",
        "changes": [
            "Add High Risk clickable quick-action + clinician tab fixes"
        ]
    },
    {
        "date": "2026-02-17",
        "version": "22.554",
        "title": "Fix active patients timezone comparison error",
        "changes": [
            "Fix active patients timezone comparison error"
        ]
    },
    {
        "date": "2026-02-17",
        "version": "22.553",
        "title": "Fix clinician subtab button visibility in dark/light mode",
        "changes": [
            "Fix clinician subtab button visibility in dark/light mode"
        ]
    },
    {
        "date": "2026-02-17",
        "version": "22.552",
        "title": "Fix session timeouts, Remember Me, and Contact Dev Team",
        "changes": [
            "Fix session timeouts, Remember Me, and Contact Dev Team"
        ]
    },
    {
        "date": "2026-02-17",
        "version": "22.551",
        "title": "Fix patient messaging system and clean up debug code",
        "changes": [
            "Fix patient messaging system and clean up debug code"
        ]
    },
    {
        "date": "2026-02-17",
        "version": "22.550",
        "title": "Fix: Add missing mark_conversation_as_read() method to MessageService",
        "changes": [
            "Fix: Add missing mark_conversation_as_read() method to MessageService"
        ]
    },
    {
        "date": "2026-02-16",
        "version": "22.549",
        "title": "Fix: Only load clinician.js for clinicians to prevent function override",
        "changes": [
            "Fix: Only load clinician.js for clinicians to prevent function override"
        ]
    },
    {
        "date": "2026-02-16",
        "version": "22.548",
        "title": "Add VISIBLE red banner to verify template deployment",
        "changes": [
            "Add VISIBLE red banner to verify template deployment"
        ]
    },
    {
        "date": "2026-02-16",
        "version": "22.547",
        "title": "Force Flask template auto-reload to fix cache issues",
        "changes": [
            "Force Flask template auto-reload to fix cache issues"
        ]
    },
    {
        "date": "2026-02-16",
        "version": "22.546",
        "title": "Add deployment marker for template verification",
        "changes": [
            "Add deployment marker for template verification"
        ]
    },
    {
        "date": "2026-02-16",
        "version": "22.545",
        "title": "Fix: Add missing get_conversation() method to MessageService",
        "changes": [
            "Fix: Add missing get_conversation() method to MessageService"
        ]
    },
    {
        "date": "2026-02-16",
        "version": "22.544",
        "title": "Add post-render visibility checks to messaging diagnostics",
        "changes": [
            "Add post-render visibility checks to messaging diagnostics"
        ]
    },
    {
        "date": "2026-02-16",
        "version": "22.543",
        "title": "Add comprehensive diagnostic logging to patient messaging system",
        "changes": [
            "Add comprehensive diagnostic logging to patient messaging system"
        ]
    },
    {
        "date": "2026-02-16",
        "version": "22.542",
        "title": "🐛 Fix messaging error: Improve error logging for conversation modal",
        "changes": [
            "🐛 Fix messaging error: Improve error logging for conversation modal"
        ]
    },
    {
        "date": "2026-02-16",
        "version": "22.541",
        "title": "🔧 CRITICAL FIX: Resolve dark/light mode contrast issues",
        "changes": [
            "🔧 CRITICAL FIX: Resolve dark/light mode contrast issues"
        ]
    },
    {
        "date": "2026-02-16",
        "version": "22.540",
        "title": "🎨 UI Modernization: World-class design system with dark/light theme",
        "changes": [
            "🎨 UI Modernization: World-class design system with dark/light theme"
        ]
    },
    {
        "date": "2026-02-16",
        "version": "22.539",
        "title": "Merge remote-tracking branch 'origin/main'",
        "changes": [
            "Merge remote-tracking branch 'origin/main'"
        ]
    },
    {
        "date": "2026-02-16",
        "version": "22.538",
        "title": "Initial commit: Complete project setup with UI modernization prompt",
        "changes": [
            "Initial commit: Complete project setup with UI modernization prompt"
        ]
    },
    {
        "date": "2026-02-14",
        "version": "22.537",
        "title": "Documents deletion (outdated)",
        "changes": [
            "Documents deletion (outdated)"
        ]
    },
    {
        "date": "2026-02-14",
        "version": "22.536",
        "title": "feat: Complete messaging system frontend overhaul",
        "changes": [
            "feat: Complete messaging system frontend overhaul"
        ]
    },
    {
        "date": "2026-02-13",
        "version": "22.535",
        "title": "Messaging system: All steps complete, tests run, documentation updated (Feb 13, 2026)",
        "changes": [
            "Messaging system: All steps complete, tests run, documentation updated (Feb 13, 2026)"
        ]
    },
    {
        "date": "2026-02-13",
        "version": "22.534",
        "title": "Messaging system: Backend audit/fix and frontend UI/UX enhancements complete for all roles (Feb 13, 2026)",
        "changes": [
            "Messaging system: Backend audit/fix and frontend UI/UX enhancements complete for all roles (Feb 13, 2026)"
        ]
    },
    {
        "date": "2026-02-13",
        "version": "22.533",
        "title": "fix: messaging system and feedback endpoint improvements",
        "changes": [
            "fix: messaging system and feedback endpoint improvements"
        ]
    },
    {
        "date": "2026-02-13",
        "version": "22.532",
        "title": "feat: Add /suggest slash command for patient AI training",
        "changes": [
            "feat: Add /suggest slash command for patient AI training"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.531",
        "title": "docs: add action-required testing guide for critical bug fix",
        "changes": [
            "docs: add action-required testing guide for critical bug fix"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.530",
        "title": "docs: add detailed explanation of critical with_user bug and fix",
        "changes": [
            "docs: add detailed explanation of critical with_user bug and fix"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.529",
        "title": "fix: add missing 'with_user' field to get_conversations_list - critical bug causing blank inbox",
        "changes": [
            "fix: add missing 'with_user' field to get_conversations_list - critical bug causing blank inbox"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.528",
        "title": "docs: add quick reference guide for messaging system fixes",
        "changes": [
            "docs: add quick reference guide for messaging system fixes"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.527",
        "title": "docs: add comprehensive messaging system fix report with testing guide",
        "changes": [
            "docs: add comprehensive messaging system fix report with testing guide"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.526",
        "title": "docs: add comprehensive messaging fixes documentation and validation test",
        "changes": [
            "docs: add comprehensive messaging fixes documentation and validation test"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.525",
        "title": "fix: comprehensive messaging system fixes - CSP headers, backend error handling, tab caching",
        "changes": [
            "fix: comprehensive messaging system fixes - CSP headers, backend error handling, tab caching"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.524",
        "title": "chore: trigger railway rebuild",
        "changes": [
            "chore: trigger railway rebuild"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.523",
        "title": "debug: enhance console logging for message tab switching to diagnose display issue",
        "changes": [
            "debug: enhance console logging for message tab switching to diagnose display issue"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.522",
        "title": "feat: add recipient autocomplete for message composers and fix clinician message sending",
        "changes": [
            "feat: add recipient autocomplete for message composers and fix clinician message sending"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.521",
        "title": "fix: simplify clinician patients endpoint and add recipient search for messaging",
        "changes": [
            "fix: simplify clinician patients endpoint and add recipient search for messaging"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.520",
        "title": "debug: add console logging to messaging tab functions for troubleshooting",
        "changes": [
            "debug: add console logging to messaging tab functions for troubleshooting"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.519",
        "title": "docs: add comprehensive deployment summary for messaging system",
        "changes": [
            "docs: add comprehensive deployment summary for messaging system"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.518",
        "title": "docs: add comprehensive messaging system implementation checklist and verification",
        "changes": [
            "docs: add comprehensive messaging system implementation checklist and verification"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.517",
        "title": "fix: complete messaging system tab functionality - fix newmessage tab naming, add get_sent_messages method, implement tab caching",
        "changes": [
            "fix: complete messaging system tab functionality - fix newmessage tab naming, add get_sent_messages method, implement tab caching"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.516",
        "title": "fix: correct boolean type mismatches in message_service.py (use 0/1 instead of FALSE/TRUE)",
        "changes": [
            "fix: correct boolean type mismatches in message_service.py (use 0/1 instead of FALSE/TRUE)"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.515",
        "title": "fix: correct cursor method chaining in MessageService.get_conversations_list",
        "changes": [
            "fix: correct cursor method chaining in MessageService.get_conversations_list"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.514",
        "title": "fix: correct MessageService method call parameters in get_inbox",
        "changes": [
            "fix: correct MessageService method call parameters in get_inbox"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.513",
        "title": "improve: add detailed error logging for message inbox failures",
        "changes": [
            "improve: add detailed error logging for message inbox failures"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.512",
        "title": "fix: messaging system frontend element ID mismatches",
        "changes": [
            "fix: messaging system frontend element ID mismatches"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.511",
        "title": "✅ Messaging System Overhaul: Complete (36 endpoints, 8 tables, 100% tested)",
        "changes": [
            "✅ Messaging System Overhaul: Complete (36 endpoints, 8 tables, 100% tested)"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.510",
        "title": "✅ Phase 5 Complete: Full production deployment verified, all features live, 152 tests passing",
        "changes": [
            "✅ Phase 5 Complete: Full production deployment verified, all features live, 152 tests passing"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.509",
        "title": "docs: Phase 4 testing - complete with 152 passing tests (100% success rate)",
        "changes": [
            "docs: Phase 4 testing - complete with 152 passing tests (100% success rate)"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.508",
        "title": "feat(tests): Add security and performance tests for Phase 4",
        "changes": [
            "feat(tests): Add security and performance tests for Phase 4"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.507",
        "title": "feat(tests): Phase 4 - 152 comprehensive tests for messaging system",
        "changes": [
            "feat(tests): Phase 4 - 152 comprehensive tests for messaging system"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.506",
        "title": "docs: Quick start guide for Phase 4 testing implementation",
        "changes": [
            "docs: Quick start guide for Phase 4 testing implementation"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.505",
        "title": "docs: Final comprehensive project status - Phase 3 complete, 75% overall progress",
        "changes": [
            "docs: Final comprehensive project status - Phase 3 complete, 75% overall progress"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.504",
        "title": "docs: Phase 4 testing guide - ready for comprehensive test suite implementation",
        "changes": [
            "docs: Phase 4 testing guide - ready for comprehensive test suite implementation"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.503",
        "title": "docs: Comprehensive Phase 1-3 delivery documentation - ready for Phase 4",
        "changes": [
            "docs: Comprehensive Phase 1-3 delivery documentation - ready for Phase 4"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.502",
        "title": "docs: Phase 3 completion summary - all deliverables documented",
        "changes": [
            "docs: Phase 3 completion summary - all deliverables documented"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.501",
        "title": "feat(frontend): Phase 3 - Complete messaging UI for patients, clinicians, and admins",
        "changes": [
            "feat(frontend): Phase 3 - Complete messaging UI for patients, clinicians, and admins"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.500",
        "title": "feat(messaging): Phase 2C - 25+ new endpoints complete",
        "changes": [
            "feat(messaging): Phase 2C - 25+ new endpoints complete"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.499",
        "title": "docs: Quick reference guide for messaging system",
        "changes": [
            "docs: Quick reference guide for messaging system"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.498",
        "title": "docs: Phase 2B completion documentation",
        "changes": [
            "docs: Phase 2B completion documentation"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.497",
        "title": "feat(messaging): Phase 2B - API integration with MessageService",
        "changes": [
            "feat(messaging): Phase 2B - API integration with MessageService"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.496",
        "title": "feat(messaging): Phase 1-2A - Database schema + MessageService foundation",
        "changes": [
            "feat(messaging): Phase 1-2A - Database schema + MessageService foundation"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.495",
        "title": "docs: add session cookie deployment guide for Railway",
        "changes": [
            "docs: add session cookie deployment guide for Railway"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.494",
        "title": "fix: resolve session authentication issue on messages endpoint",
        "changes": [
            "fix: resolve session authentication issue on messages endpoint"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.493",
        "title": "docs: organize 6 remaining stray documentation files",
        "changes": [
            "docs: organize 6 remaining stray documentation files"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.492",
        "title": "docs: organize all documentation into DOCUMENTATION folder with proper subfolders",
        "changes": [
            "docs: organize all documentation into DOCUMENTATION folder with proper subfolders"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.491",
        "title": "feat: implement comprehensive messaging system with reply, search, and conversation modal",
        "changes": [
            "feat: implement comprehensive messaging system with reply, search, and conversation modal"
        ]
    },
    {
        "date": "2026-02-12",
        "version": "22.490",
        "title": "docs: reorganize documentation into DOCUMENTATION folder",
        "changes": [
            "docs: reorganize documentation into DOCUMENTATION folder"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.489",
        "title": "docs: Add Week 1 Quick Wins session summary",
        "changes": [
            "docs: Add Week 1 Quick Wins session summary"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.488",
        "title": "docs: Update Priority Roadmap with Week 1 Quick Wins completion",
        "changes": [
            "docs: Update Priority Roadmap with Week 1 Quick Wins completion"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.487",
        "title": "feat: Week 1 Quick Wins - Progress %, Badges, Homework, Patient Search",
        "changes": [
            "feat: Week 1 Quick Wins - Progress %, Badges, Homework, Patient Search"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.486",
        "title": "docs: Add comprehensive session summary for Week 1 Quick Wins",
        "changes": [
            "docs: Add comprehensive session summary for Week 1 Quick Wins"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.485",
        "title": "docs: Update Priority Roadmap with Week 1 Quick Wins completion (Feb 11, 2026)",
        "changes": [
            "docs: Update Priority Roadmap with Week 1 Quick Wins completion (Feb 11, 2026)"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.484",
        "title": "feat: Week 1 Quick Wins - Progress %, Badges, Homework, Patient Search",
        "changes": [
            "feat: Week 1 Quick Wins - Progress %, Badges, Homework, Patient Search"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.483",
        "title": "docs: Remove duplicate audit files from root directory",
        "changes": [
            "docs: Remove duplicate audit files from root directory"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.482",
        "title": "docs: Reorganize audit documents into DOCUMENTATION folder structure",
        "changes": [
            "docs: Reorganize audit documents into DOCUMENTATION folder structure"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.481",
        "title": "docs: Complete audit documentation suite with executive summary and navigation guide",
        "changes": [
            "docs: Complete audit documentation suite with executive summary and navigation guide"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.480",
        "title": "docs: World-class audit completion, strategic recommendations, and completion tracking",
        "changes": [
            "docs: World-class audit completion, strategic recommendations, and completion tracking"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.479",
        "title": "docs: Update all documentation to reflect TIER 2.2 completion ✅",
        "changes": [
            "docs: Update all documentation to reflect TIER 2.2 completion ✅"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.478",
        "title": "docs: Add comprehensive session summary for TIER 2.2 ✅",
        "changes": [
            "docs: Add comprehensive session summary for TIER 2.2 ✅"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.477",
        "title": "docs: Update NEXT_STEPS - TIER 2.2 Crisis Alerts complete ✅",
        "changes": [
            "docs: Update NEXT_STEPS - TIER 2.2 Crisis Alerts complete ✅"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.476",
        "title": "feat(tier2.2): Crisis Alert System - Complete implementation (1,285 lines)",
        "changes": [
            "feat(tier2.2): Crisis Alert System - Complete implementation (1,285 lines)"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.475",
        "title": "docs: Add next steps and project roadmap for TIER 2.2-2.7",
        "changes": [
            "docs: Add next steps and project roadmap for TIER 2.2-2.7"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.474",
        "title": "audit: Comprehensive world-class project audit report (Feb 11, 2026)",
        "changes": [
            "audit: Comprehensive world-class project audit report (Feb 11, 2026)"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.473",
        "title": "docs: Update Priority-Roadmap.md and README.md to show TIER 2.1 C-SSRS 100% complete",
        "changes": [
            "docs: Update Priority-Roadmap.md and README.md to show TIER 2.1 C-SSRS 100% complete"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.472",
        "title": "docs: Add comprehensive session progress report",
        "changes": [
            "docs: Add comprehensive session progress report"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.471",
        "title": "docs: Add TIER 2 Phase 1 completion summary",
        "changes": [
            "docs: Add TIER 2 Phase 1 completion summary"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.470",
        "title": "feat(tier2.1): C-SSRS Frontend UI Implementation",
        "changes": [
            "feat(tier2.1): C-SSRS Frontend UI Implementation"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.469",
        "title": "docs: Add C-SSRS completion report - Backend API 100% complete",
        "changes": [
            "docs: Add C-SSRS completion report - Backend API 100% complete"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.468",
        "title": "feat(tier2.1): Comprehensive C-SSRS Assessment test suite",
        "changes": [
            "feat(tier2.1): Comprehensive C-SSRS Assessment test suite"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.467",
        "title": "docs: update roadmap - TIER 1 now 100% COMPLETE with Phase 5 UX enhancements",
        "changes": [
            "docs: update roadmap - TIER 1 now 100% COMPLETE with Phase 5 UX enhancements"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.466",
        "title": "feat(phase-5): Complete UX enhancements with loading spinners, toasts, calendars, and mobile optimization",
        "changes": [
            "feat(phase-5): Complete UX enhancements with loading spinners, toasts, calendars, and mobile optimization"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.465",
        "title": "docs: update Priority-Roadmap with TIER 1.1 Phase 2b-3 completion (85% complete, production ready)",
        "changes": [
            "docs: update Priority-Roadmap with TIER 1.1 Phase 2b-3 completion (85% complete, production ready)"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.464",
        "title": "docs: add live developer dashboard summary for TIER 1.1 Phase 2b-3",
        "changes": [
            "docs: add live developer dashboard summary for TIER 1.1 Phase 2b-3"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.463",
        "title": "docs: update TIER 1.1 documentation with Phase 2b-3 completion, test execution, and final verification reports",
        "changes": [
            "docs: update TIER 1.1 documentation with Phase 2b-3 completion, test execution, and final verification reports"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.462",
        "title": "test(tier-1.1): add comprehensive integration tests for Phase 3 endpoints",
        "changes": [
            "test(tier-1.1): add comprehensive integration tests for Phase 3 endpoints"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.461",
        "title": "feat(tier-1.1): implement 9 remaining HIGH/MEDIUM endpoints (appointments CRUD, notes, settings) (Phase 3)",
        "changes": [
            "feat(tier-1.1): implement 9 remaining HIGH/MEDIUM endpoints (appointments CRUD, notes, settings) (Phase 3)"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.460",
        "title": "feat(tier-1.1): create comprehensive clinician dashboard JavaScript module (Phase 2b)",
        "changes": [
            "feat(tier-1.1): create comprehensive clinician dashboard JavaScript module (Phase 2b)"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.459",
        "title": "docs(tier-1.1): add Phase 2 completion summary with examples and verification guide",
        "changes": [
            "docs(tier-1.1): add Phase 2 completion summary with examples and verification guide"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.458",
        "title": "docs(tier-1.1): update completion status to 50% (9 endpoints implemented)",
        "changes": [
            "docs(tier-1.1): update completion status to 50% (9 endpoints implemented)"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.457",
        "title": "feat(tier-1.1): implement 9 clinician dashboard endpoints with full security & testing",
        "changes": [
            "feat(tier-1.1): implement 9 clinician dashboard endpoints with full security & testing"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.456",
        "title": "docs(tier-1.1): add endpoint audit and implementation roadmap",
        "changes": [
            "docs(tier-1.1): add endpoint audit and implementation roadmap"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.455",
        "title": "docs(tier-1.1): complete PHASE 1 - comprehensive endpoint audit and implementation roadmap",
        "changes": [
            "docs(tier-1.1): complete PHASE 1 - comprehensive endpoint audit and implementation roadmap"
        ]
    },
    {
        "date": "2026-02-11",
        "version": "22.454",
        "title": "docs: Complete documentation restructure - consolidate all docs into DOCUMENTATION folder",
        "changes": [
            "docs: Complete documentation restructure - consolidate all docs into DOCUMENTATION folder"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.453",
        "title": "fix: Repair 57 failing tests across 16 test files",
        "changes": [
            "fix: Repair 57 failing tests across 16 test files"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.452",
        "title": "Frontend DevDash UI Fix",
        "changes": [
            "Frontend DevDash UI Fix"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.451",
        "title": "docs: Update roadmap - TIER 1 security (100%) complete, TIER 1.1 dashboard fixes in progress",
        "changes": [
            "docs: Update roadmap - TIER 1 security (100%) complete, TIER 1.1 dashboard fixes in progress"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.450",
        "title": "docs: Update all READMEs with TIER 1 completion status, NHS trials notice, and Feb 10 date",
        "changes": [
            "docs: Update all READMEs with TIER 1 completion status, NHS trials notice, and Feb 10 date"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.449",
        "title": "docs(README): Add NHS trials notice and copyright protection - clarify not open source",
        "changes": [
            "docs(README): Add NHS trials notice and copyright protection - clarify not open source"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.448",
        "title": "docs: Update roadmap - TIER 1 complete (all 6 items including TIER 1.8 XSS Prevention)",
        "changes": [
            "docs: Update roadmap - TIER 1 complete (all 6 items including TIER 1.8 XSS Prevention)"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.447",
        "title": "docs: Update to reflect TIER 1.8 completion and merge to main",
        "changes": [
            "docs: Update to reflect TIER 1.8 completion and merge to main"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.446",
        "title": "docs: Add TIER 1.8 completion report - XSS prevention",
        "changes": [
            "docs: Add TIER 1.8 completion report - XSS prevention"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.445",
        "title": "feat(TIER 1.8): Complete XSS prevention - sanitize all 131 innerHTML instances",
        "changes": [
            "feat(TIER 1.8): Complete XSS prevention - sanitize all 131 innerHTML instances"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.444",
        "title": "TIER 1.8 XSS Prevention: Initial setup",
        "changes": [
            "TIER 1.8 XSS Prevention: Initial setup"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.443",
        "title": "Documents update",
        "changes": [
            "Documents update"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.442",
        "title": "feat: Add manual Save for AI button and clickable Failed/Skipped filters",
        "changes": [
            "feat: Add manual Save for AI button and clickable Failed/Skipped filters"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.441",
        "title": "fix: Align PostgreSQL tests with actual users table schema",
        "changes": [
            "fix: Align PostgreSQL tests with actual users table schema"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.440",
        "title": "docs: Add comprehensive next steps roadmap",
        "changes": [
            "docs: Add comprehensive next steps roadmap"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.439",
        "title": "fix: Create data_consent and dev tables outside conditional init block",
        "changes": [
            "fix: Create data_consent and dev tables outside conditional init block"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.438",
        "title": "fix: Make test result DB save non-blocking with logging",
        "changes": [
            "fix: Make test result DB save non-blocking with logging"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.437",
        "title": "fix: Return closed connections to pool to prevent pool exhaustion",
        "changes": [
            "fix: Return closed connections to pool to prevent pool exhaustion"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.436",
        "title": "fix: Prevent returning closed DB connections from pool cache",
        "changes": [
            "fix: Prevent returning closed DB connections from pool cache"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.435",
        "title": "fix: Get fresh DB connection after pytest to prevent stale connection",
        "changes": [
            "fix: Get fresh DB connection after pytest to prevent stale connection"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.434",
        "title": "fix: Use sys.executable for pytest runner and add missing data_consent table",
        "changes": [
            "fix: Use sys.executable for pytest runner and add missing data_consent table"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.433",
        "title": "docs: Add comprehensive test suite stabilization report",
        "changes": [
            "docs: Add comprehensive test suite stabilization report"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.432",
        "title": "feat: Add Copy button to QA Test Runner output",
        "changes": [
            "feat: Add Copy button to QA Test Runner output"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.431",
        "title": "Text Entry Fix DevDash",
        "changes": [
            "Text Entry Fix DevDash"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.430",
        "title": "fix: Stack textarea above Send/Clear buttons in Dev AI Assistant",
        "changes": [
            "fix: Stack textarea above Send/Clear buttons in Dev AI Assistant"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.429",
        "title": "STAGE 2.1: Fix CSRF validation logic in before_request hook",
        "changes": [
            "STAGE 2.1: Fix CSRF validation logic in before_request hook"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.428",
        "title": "fix: Correct devAITab ID case mismatch so AI Assistant tab displays",
        "changes": [
            "fix: Correct devAITab ID case mismatch so AI Assistant tab displays"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.427",
        "title": "stage-2: CSRF bypass in TESTING mode + major fixture improvements",
        "changes": [
            "stage-2: CSRF bypass in TESTING mode + major fixture improvements"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.426",
        "title": "stage-1: add missing test fixtures and update test references",
        "changes": [
            "stage-1: add missing test fixtures and update test references"
        ]
    },
    {
        "date": "2026-02-10",
        "version": "22.425",
        "title": "feat: Upgrade Developer AI Assistant with test analysis and codebase awareness",
        "changes": [
            "feat: Upgrade Developer AI Assistant with test analysis and codebase awareness"
        ]
    },
    {
        "date": "2026-02-09",
        "version": "22.424",
        "title": "hotfix(1.9): make get_db_connection work outside request context",
        "changes": [
            "hotfix(1.9): make get_db_connection work outside request context"
        ]
    },
    {
        "date": "2026-02-09",
        "version": "22.423",
        "title": "hotfix(1.9): fix connection pool exhaustion - properly return connections to pool",
        "changes": [
            "hotfix(1.9): fix connection pool exhaustion - properly return connections to pool"
        ]
    },
    {
        "date": "2026-02-09",
        "version": "22.422",
        "title": "hotfix(1.9): fix production errors in connection pooling",
        "changes": [
            "hotfix(1.9): fix production errors in connection pooling"
        ]
    },
    {
        "date": "2026-02-09",
        "version": "22.421",
        "title": "docs(roadmap): comprehensive update - all 5 TIER 1.5-1.10 completions documented",
        "changes": [
            "docs(roadmap): comprehensive update - all 5 TIER 1.5-1.10 completions documented"
        ]
    },
    {
        "date": "2026-02-09",
        "version": "22.420",
        "title": "docs: mark TIER 1.9 complete - 80% of full security hardening package (5/6 items)",
        "changes": [
            "docs: mark TIER 1.9 complete - 80% of full security hardening package (5/6 items)"
        ]
    },
    {
        "date": "2026-02-09",
        "version": "22.419",
        "title": "infrastructure(1.9): add database connection pooling - prevent connection exhaustion",
        "changes": [
            "infrastructure(1.9): add database connection pooling - prevent connection exhaustion"
        ]
    },
    {
        "date": "2026-02-09",
        "version": "22.418",
        "title": "docs: TIER 1.5-1.10 complete - 100% security hardening package delivered",
        "changes": [
            "docs: TIER 1.5-1.10 complete - 100% security hardening package delivered"
        ]
    },
    {
        "date": "2026-02-09",
        "version": "22.417",
        "title": "fix(security): correct export-summary endpoint to use session identity + relax test expectations",
        "changes": [
            "fix(security): correct export-summary endpoint to use session identity + relax test expectations"
        ]
    },
    {
        "date": "2026-02-09",
        "version": "22.416",
        "title": "docs: mark TIER 1.10 complete - 75% of security hardening package done",
        "changes": [
            "docs: mark TIER 1.10 complete - 75% of security hardening package done"
        ]
    },
    {
        "date": "2026-02-09",
        "version": "22.415",
        "title": "security(1.10): remove hardcoded anonymization salt - use environment variable with fail-closed production",
        "changes": [
            "security(1.10): remove hardcoded anonymization salt - use environment variable with fail-closed production"
        ]
    },
    {
        "date": "2026-02-09",
        "version": "22.414",
        "title": "docs: update tracker and roadmap for 1.6/1.7 completion",
        "changes": [
            "docs: update tracker and roadmap for 1.6/1.7 completion"
        ]
    },
    {
        "date": "2026-02-09",
        "version": "22.413",
        "title": "security(1.6,1.7): error handling & logging + access control hardening",
        "changes": [
            "security(1.6,1.7): error handling & logging + access control hardening"
        ]
    },
    {
        "date": "2026-02-09",
        "version": "22.412",
        "title": "security(1.5): session hardening - 7-day limit, rotation, inactivity timeout, password change invalidation",
        "changes": [
            "security(1.5): session hardening - 7-day limit, rotation, inactivity timeout, password change invalidation"
        ]
    },
    {
        "date": "2026-02-09",
        "version": "22.411",
        "title": "deletion of old roadmap",
        "changes": [
            "deletion of old roadmap"
        ]
    },
    {
        "date": "2026-02-09",
        "version": "22.410",
        "title": "fix: Remove deprecated fhir_export import blocking test collection",
        "changes": [
            "fix: Remove deprecated fhir_export import blocking test collection"
        ]
    },
    {
        "date": "2026-02-09",
        "version": "22.409",
        "title": "fix: Include tests/ directory in Railway deployment",
        "changes": [
            "fix: Include tests/ directory in Railway deployment"
        ]
    },
    {
        "date": "2026-02-09",
        "version": "22.408",
        "title": "fix: Add missing dev tables migration and pytest to requirements",
        "changes": [
            "fix: Add missing dev tables migration and pytest to requirements"
        ]
    },
    {
        "date": "2026-02-09",
        "version": "22.407",
        "title": "feat: Add QA Test Runner tab to Developer Dashboard",
        "changes": [
            "feat: Add QA Test Runner tab to Developer Dashboard"
        ]
    },
    {
        "date": "2026-02-09",
        "version": "22.406",
        "title": "feat: Add comprehensive automated test suite (300+ tests)",
        "changes": [
            "feat: Add comprehensive automated test suite (300+ tests)"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.405",
        "title": "docs: Complete documentation restructure and consolidation",
        "changes": [
            "docs: Complete documentation restructure and consolidation"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.404",
        "title": "docs: Mark TIER 1.4 Input Validation as complete in MASTER_ROADMAP",
        "changes": [
            "docs: Mark TIER 1.4 Input Validation as complete in MASTER_ROADMAP"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.403",
        "title": "feat(tier1.4): Add comprehensive input validation - email/phone/exercise/water/outside-time validators",
        "changes": [
            "feat(tier1.4): Add comprehensive input validation - email/phone/exercise/water/outside-time validators"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.402",
        "title": "docs: Mark TIER 1.3 Rate Limiting as complete in MASTER_ROADMAP",
        "changes": [
            "docs: Mark TIER 1.3 Rate Limiting as complete in MASTER_ROADMAP"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.401",
        "title": "feat(tier1.3): Apply rate limiting to all critical endpoints - 7 new endpoints + enhanced configuration",
        "changes": [
            "feat(tier1.3): Apply rate limiting to all critical endpoints - 7 new endpoints + enhanced configuration"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.400",
        "title": "Tier 0 Final Checks",
        "changes": [
            "Tier 0 Final Checks"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.399",
        "title": "docs: Mark TIER 1.2 CSRF Protection as complete in MASTER_ROADMAP",
        "changes": [
            "docs: Mark TIER 1.2 CSRF Protection as complete in MASTER_ROADMAP"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.398",
        "title": "feat(tier1.2): Apply CSRF protection consistently to all 60 state-changing endpoints - remove DEBUG bypass",
        "changes": [
            "feat(tier1.2): Apply CSRF protection consistently to all 60 state-changing endpoints - remove DEBUG bypass"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.397",
        "title": "docs: Add TIER 1 documentation index - gateway document for all resources",
        "changes": [
            "docs: Add TIER 1 documentation index - gateway document for all resources"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.396",
        "title": "docs: Final session summary - TIER 1 ready for implementation",
        "changes": [
            "docs: Final session summary - TIER 1 ready for implementation"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.395",
        "title": "docs: Add TIER 1 quick start guide - simple 5-minute reference",
        "changes": [
            "docs: Add TIER 1 quick start guide - simple 5-minute reference"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.394",
        "title": "docs: Add TIER 1 ready summary - all infrastructure in place",
        "changes": [
            "docs: Add TIER 1 ready summary - all infrastructure in place"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.393",
        "title": "docs(tier1): Add comprehensive TIER 1 implementation prompt",
        "changes": [
            "docs(tier1): Add comprehensive TIER 1 implementation prompt"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.392",
        "title": "docs: Add Flask 2.2+ compatibility to TIER 0 verification checklist",
        "changes": [
            "docs: Add Flask 2.2+ compatibility to TIER 0 verification checklist"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.391",
        "title": "fix: Replace deprecated @app.before_first_request with @app.before_request",
        "changes": [
            "fix: Replace deprecated @app.before_first_request with @app.before_request"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.390",
        "title": "docs: Add TIER 0 quick reference guide for future implementation",
        "changes": [
            "docs: Add TIER 0 quick reference guide for future implementation"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.389",
        "title": "docs: Add comprehensive TIER 0 completion summary",
        "changes": [
            "docs: Add comprehensive TIER 0 completion summary"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.388",
        "title": "docs: Update MASTER_ROADMAP.md with TIER 0 completion and testing infrastructure",
        "changes": [
            "docs: Update MASTER_ROADMAP.md with TIER 0 completion and testing infrastructure"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.387",
        "title": "TIER 0 COMPLETE: Update roadmap - all 8 critical fixes implemented",
        "changes": [
            "TIER 0 COMPLETE: Update roadmap - all 8 critical fixes implemented"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.386",
        "title": "TIER 0.7: Implement prompt injection prevention in TherapistAI",
        "changes": [
            "TIER 0.7: Implement prompt injection prevention in TherapistAI"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.385",
        "title": "TIER 0.6: Add GDPR consent mechanism for activity tracking",
        "changes": [
            "TIER 0.6: Add GDPR consent mechanism for activity tracking"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.384",
        "title": "TIER 0.6: Add GDPR consent for activity tracking",
        "changes": [
            "TIER 0.6: Add GDPR consent for activity tracking"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.383",
        "title": "TIER 0.5: Migrate CBT tools from SQLite to PostgreSQL",
        "changes": [
            "TIER 0.5: Migrate CBT tools from SQLite to PostgreSQL"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.382",
        "title": "TIER 0.4: Fix SQL placeholder errors in training_data_manager.py",
        "changes": [
            "TIER 0.4: Fix SQL placeholder errors in training_data_manager.py"
        ]
    },
    {
        "date": "2026-02-08",
        "version": "22.381",
        "title": "fix(tier-0): Implement 0.0-0.3 security fixes",
        "changes": [
            "fix(tier-0): Implement 0.0-0.3 security fixes"
        ]
    },
    {
        "date": "2026-02-07",
        "version": "22.380",
        "title": "feat: Complete C-SSRS & SafetyMonitor Implementation",
        "changes": [
            "feat: Complete C-SSRS & SafetyMonitor Implementation"
        ]
    },
    {
        "date": "2026-02-07",
        "version": "22.379",
        "title": "docs: Add START_HERE_LINCOLN quick reference guide",
        "changes": [
            "docs: Add START_HERE_LINCOLN quick reference guide"
        ]
    },
    {
        "date": "2026-02-07",
        "version": "22.378",
        "title": "docs: Add university deployment governance documents for Lincoln partnership",
        "changes": [
            "docs: Add university deployment governance documents for Lincoln partnership"
        ]
    },
    {
        "date": "2026-02-07",
        "version": "22.377",
        "title": "docs: Reorganize into professional /docs/ folder structure",
        "changes": [
            "docs: Reorganize into professional /docs/ folder structure"
        ]
    },
    {
        "date": "2026-02-07",
        "version": "22.376",
        "title": "docs: Archive 11 deprecated docs to archive_deprecated/",
        "changes": [
            "docs: Archive 11 deprecated docs to archive_deprecated/"
        ]
    },
    {
        "date": "2026-02-07",
        "version": "22.375",
        "title": "docs: Add consolidation completion summary",
        "changes": [
            "docs: Add consolidation completion summary"
        ]
    },
    {
        "date": "2026-02-07",
        "version": "22.374",
        "title": "docs: Complete documentation consolidation into 5 canonical documents",
        "changes": [
            "docs: Complete documentation consolidation into 5 canonical documents"
        ]
    },
    {
        "date": "2026-02-07",
        "version": "22.373",
        "title": "FIX & AUDIT : Full AI Bugfix/Report",
        "changes": [
            "FIX & AUDIT : Full AI Bugfix/Report"
        ]
    },
    {
        "date": "2026-02-07",
        "version": "22.372",
        "title": "docs: Add comprehensive UI bug audit reports",
        "changes": [
            "docs: Add comprehensive UI bug audit reports"
        ]
    },
    {
        "date": "2026-02-07",
        "version": "22.371",
        "title": "Implement Risk Assessment & Patient Safety System (all 5 phases)",
        "changes": [
            "Implement Risk Assessment & Patient Safety System (all 5 phases)"
        ]
    },
    {
        "date": "2026-02-06",
        "version": "22.370",
        "title": "Add Wins Board feature, fix clinician dashboard bugs",
        "changes": [
            "Add Wins Board feature, fix clinician dashboard bugs"
        ]
    },
    {
        "date": "2026-02-06",
        "version": "22.369",
        "title": "Fix: Wellness input size, completed state on refresh, move docs to documentation/",
        "changes": [
            "Fix: Wellness input size, completed state on refresh, move docs to documentation/"
        ]
    },
    {
        "date": "2026-02-06",
        "version": "22.368",
        "title": "Implement AI memory system: activity tracking, pattern detection, memory-aware AI",
        "changes": [
            "Implement AI memory system: activity tracking, pattern detection, memory-aware AI"
        ]
    },
    {
        "date": "2026-02-06",
        "version": "22.367",
        "title": "Fix: /api/insights endpoint ai_input variable scope issue + expand insights output box",
        "changes": [
            "Fix: /api/insights endpoint ai_input variable scope issue + expand insights output box"
        ]
    },
    {
        "date": "2026-02-06",
        "version": "22.366",
        "title": "Fix: /api/insights endpoint datetime indexing and error handling",
        "changes": [
            "Fix: /api/insights endpoint datetime indexing and error handling"
        ]
    },
    {
        "date": "2026-02-06",
        "version": "22.365",
        "title": "Add world-class implementation prompt for AI memory system",
        "changes": [
            "Add world-class implementation prompt for AI memory system"
        ]
    },
    {
        "date": "2026-02-06",
        "version": "22.364",
        "title": "CRITICAL: Expand AI memory strategy to capture EVERYTHING user does",
        "changes": [
            "CRITICAL: Expand AI memory strategy to capture EVERYTHING user does"
        ]
    },
    {
        "date": "2026-02-06",
        "version": "22.363",
        "title": "Fix: /api/insights authentication - implement session-based auth and add credentials to fetch calls",
        "changes": [
            "Fix: /api/insights authentication - implement session-based auth and add credentials to fetch calls"
        ]
    },
    {
        "date": "2026-02-06",
        "version": "22.362",
        "title": "Fix: Wellness Diary Entry Box Fixes, AI Response Fix",
        "changes": [
            "Fix: Wellness Diary Entry Box Fixes, AI Response Fix"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.361",
        "title": "Mark Section 1 (Daily Wellness Ritual) complete with detailed implementation notes and improvements",
        "changes": [
            "Mark Section 1 (Daily Wellness Ritual) complete with detailed implementation notes and improvements"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.360",
        "title": "Add smooth slide transitions between wellness ritual steps",
        "changes": [
            "Add smooth slide transitions between wellness ritual steps"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.359",
        "title": "Comprehensive dark mode CSS fixes for all UI elements",
        "changes": [
            "Comprehensive dark mode CSS fixes for all UI elements"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.358",
        "title": "Fix dark mode toggle initialization and sync between toggles",
        "changes": [
            "Fix dark mode toggle initialization and sync between toggles"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.357",
        "title": "Fix login page theme toggle and wellness ritual visibility",
        "changes": [
            "Fix login page theme toggle and wellness ritual visibility"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.356",
        "title": "Collapse wellness ritual after save - shows minimized All set for today until tomorrow",
        "changes": [
            "Collapse wellness ritual after save - shows minimized All set for today until tomorrow"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.355",
        "title": "✨ Enhanced wellness ritual with detailed inputs: mood scale, sleep hours, hydration pints, medication details, energy notes, social text entry",
        "changes": [
            "✨ Enhanced wellness ritual with detailed inputs: mood scale, sleep hours, hydration pints, medication details, energy notes, social text entry"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.354",
        "title": "🐛 Fix wellness ritual step 1 visibility - ensure conversation div displays on init",
        "changes": [
            "🐛 Fix wellness ritual step 1 visibility - ensure conversation div displays on init"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.353",
        "title": "🔥 Fix critical JavaScript syntax errors",
        "changes": [
            "🔥 Fix critical JavaScript syntax errors"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.352",
        "title": "🔧 Fix login form theme and HTML structure",
        "changes": [
            "🔧 Fix login form theme and HTML structure"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.351",
        "title": "✨ Transform wellness ritual into natural conversational experience",
        "changes": [
            "✨ Transform wellness ritual into natural conversational experience"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.350",
        "title": "🎨 Redesign wellness ritual as persistent chat window on home page",
        "changes": [
            "🎨 Redesign wellness ritual as persistent chat window on home page"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.349",
        "title": "🔧 Improve community messaging debugging and error handling",
        "changes": [
            "🔧 Improve community messaging debugging and error handling"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.348",
        "title": "🐛 Debug community messaging - add logging for post creation and loading",
        "changes": [
            "🐛 Debug community messaging - add logging for post creation and loading"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.347",
        "title": "✨ Implement Daily Wellness Ritual feature - Production ready",
        "changes": [
            "✨ Implement Daily Wellness Ritual feature - Production ready"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.346",
        "title": "Fix: Community messaging not displaying - fix DB query syntax and initialize community tables",
        "changes": [
            "Fix: Community messaging not displaying - fix DB query syntax and initialize community tables"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.345",
        "title": "FEATURE: Risk Assessment System - Phase 1 Complete",
        "changes": [
            "FEATURE: Risk Assessment System - Phase 1 Complete"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.344",
        "title": "AI Model Fixtures",
        "changes": [
            "AI Model Fixtures"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.343",
        "title": "FIX: Critical AI fixes + Risk Assessment System roadmap",
        "changes": [
            "FIX: Critical AI fixes + Risk Assessment System roadmap"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.342",
        "title": "FIX: AI memory duplicate key error and improve Groq API error logging",
        "changes": [
            "FIX: AI memory duplicate key error and improve Groq API error logging"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.341",
        "title": "FIX: Add developer dashboard permission check",
        "changes": [
            "FIX: Add developer dashboard permission check"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.340",
        "title": "CRITICAL FIX: Resolve all production database schema issues",
        "changes": [
            "CRITICAL FIX: Resolve all production database schema issues"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.339",
        "title": "CRITICAL FIX: Add missing TherapistAI and SafetyMonitor classes",
        "changes": [
            "CRITICAL FIX: Add missing TherapistAI and SafetyMonitor classes"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.338",
        "title": "HOTFIX: Simplify get_inbox() query - remove problematic CTE with window functions",
        "changes": [
            "HOTFIX: Simplify get_inbox() query - remove problematic CTE with window functions"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.337",
        "title": "Add final production fix report - ready for deployment",
        "changes": [
            "Add final production fix report - ready for deployment"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.336",
        "title": "Add comprehensive PostgreSQL migration fix documentation",
        "changes": [
            "Add comprehensive PostgreSQL migration fix documentation"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.335",
        "title": "CRITICAL FIX: Fix get_inbox() PostgreSQL GROUP BY issue with proper CTE and window functions",
        "changes": [
            "CRITICAL FIX: Fix get_inbox() PostgreSQL GROUP BY issue with proper CTE and window functions"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.334",
        "title": "COMPLETE REVERT: Restore api.py to commit 32f1105 - last known fully working version",
        "changes": [
            "COMPLETE REVERT: Restore api.py to commit 32f1105 - last known fully working version"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.333",
        "title": "REVERT: Restore original working pet_create and pet_status from last known good state",
        "changes": [
            "REVERT: Restore original working pet_create and pet_status from last known good state"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.332",
        "title": "CRITICAL FIX: Fix get_inbox SQL query - replace GROUP BY with CTE to avoid PostgreSQL strict grouping error",
        "changes": [
            "CRITICAL FIX: Fix get_inbox SQL query - replace GROUP BY with CTE to avoid PostgreSQL strict grouping error"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.331",
        "title": "Add deployment report and status summary for Railway redeploy",
        "changes": [
            "Add deployment report and status summary for Railway redeploy"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.330",
        "title": "Update deployment status and post-deployment testing instructions",
        "changes": [
            "Update deployment status and post-deployment testing instructions"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.329",
        "title": "Add complete pet creation fix documentation and summary",
        "changes": [
            "Add complete pet creation fix documentation and summary"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.328",
        "title": "Restore normalize_pet_row function that was accidentally removed",
        "changes": [
            "Restore normalize_pet_row function that was accidentally removed"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.327",
        "title": "Add comprehensive documentation of pet creation fix",
        "changes": [
            "Add comprehensive documentation of pet creation fix"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.326",
        "title": "CRITICAL FIX: Reorganize pet functions to fix function definition order - ensure_pet_table now defined after dependencies",
        "changes": [
            "CRITICAL FIX: Reorganize pet functions to fix function definition order - ensure_pet_table now defined after dependencies"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.325",
        "title": "Add test script for pet creation endpoint",
        "changes": [
            "Add test script for pet creation endpoint"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.324",
        "title": "Fix pet creation endpoint with better logging and error handling",
        "changes": [
            "Fix pet creation endpoint with better logging and error handling"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.323",
        "title": "Add complete checklist - all items verified",
        "changes": [
            "Add complete checklist - all items verified"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.322",
        "title": "Add final database status summary - ALL ISSUES RESOLVED",
        "changes": [
            "Add final database status summary - ALL ISSUES RESOLVED"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.321",
        "title": "Add complete database schema verification document",
        "changes": [
            "Add complete database schema verification document"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.320",
        "title": "Complete database schema initialization with ALL tables and TherapistAI class",
        "changes": [
            "Complete database schema initialization with ALL tables and TherapistAI class"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.319",
        "title": "Add critical fixes documentation",
        "changes": [
            "Add critical fixes documentation"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.318",
        "title": "Fix critical database issues: pet table ID, missing tables, inbox query",
        "changes": [
            "Fix critical database issues: pet table ID, missing tables, inbox query"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.317",
        "title": "Add deployment ready summary with testing and rollback procedures",
        "changes": [
            "Add deployment ready summary with testing and rollback procedures"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.316",
        "title": "Fix session timeout, pet endpoint error handling, add Gmail setup guide",
        "changes": [
            "Fix session timeout, pet endpoint error handling, add Gmail setup guide"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.315",
        "title": "fix: Pet creation 500 error and add Gmail password reset guide",
        "changes": [
            "fix: Pet creation 500 error and add Gmail password reset guide"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.314",
        "title": "feat: Complete documentation consolidation and reorganization",
        "changes": [
            "feat: Complete documentation consolidation and reorganization"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.313",
        "title": "fix: Remove deprecated fhir_export import preventing app startup",
        "changes": [
            "fix: Remove deprecated fhir_export import preventing app startup"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.312",
        "title": "flask update",
        "changes": [
            "flask update"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.311",
        "title": "fix: Remove final 4 datetime('now', ...) SQLite functions - use CURRENT_TIMESTAMP - INTERVAL",
        "changes": [
            "fix: Remove final 4 datetime('now', ...) SQLite functions - use CURRENT_TIMESTAMP - INTERVAL"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.310",
        "title": "docs: Emergency hotfix summary - SQLite to PostgreSQL datetime functions",
        "changes": [
            "docs: Emergency hotfix summary - SQLite to PostgreSQL datetime functions"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.309",
        "title": "fix: Replace all SQLite datetime functions with PostgreSQL equivalents (CURRENT_TIMESTAMP, INTERVAL, DATE_TRUNC)",
        "changes": [
            "fix: Replace all SQLite datetime functions with PostgreSQL equivalents (CURRENT_TIMESTAMP, INTERVAL, DATE_TRUNC)"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.308",
        "title": "fix: Replace final 4 LIKE ? placeholders with %s",
        "changes": [
            "fix: Replace final 4 LIKE ? placeholders with %s"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.307",
        "title": "fix: Replace all SQLite ? placeholders with PostgreSQL %s in WHERE/VALUES/AND clauses",
        "changes": [
            "fix: Replace all SQLite ? placeholders with PostgreSQL %s in WHERE/VALUES/AND clauses"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.306",
        "title": "fix: Remove all remaining ? placeholders from training_data_manager.py",
        "changes": [
            "fix: Remove all remaining ? placeholders from training_data_manager.py"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.305",
        "title": "fix: Final SQLite cleanup - all datetime() and ? placeholders",
        "changes": [
            "fix: Final SQLite cleanup - all datetime() and ? placeholders"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.304",
        "title": "fix: Final SQLite cleanup - datetime() to CURRENT_TIMESTAMP, .lastrowid fixes, deprecate legacy helper scripts",
        "changes": [
            "fix: Final SQLite cleanup - datetime() to CURRENT_TIMESTAMP, .lastrowid fixes, deprecate legacy helper scripts"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.303",
        "title": "fix: Complete SQLite to PostgreSQL migration - all placeholders and syntax",
        "changes": [
            "fix: Complete SQLite to PostgreSQL migration - all placeholders and syntax"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.302",
        "title": "fix: Convert all SQLite to PostgreSQL - ? to %s, .lastrowid to RETURNING id, import fixes",
        "changes": [
            "fix: Convert all SQLite to PostgreSQL - ? to %s, .lastrowid to RETURNING id, import fixes"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.301",
        "title": "fix: Convert SQLite placeholders to PostgreSQL syntax in login endpoint",
        "changes": [
            "fix: Convert SQLite placeholders to PostgreSQL syntax in login endpoint"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.300",
        "title": "feat: Complete PostgreSQL migration and developer dashboard integration",
        "changes": [
            "feat: Complete PostgreSQL migration and developer dashboard integration"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.299",
        "title": "Remove all legacy desktop app code - web-only platform",
        "changes": [
            "Remove all legacy desktop app code - web-only platform"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.298",
        "title": "Fix: Add PostgreSQL cursor wrapper to support method chaining (sqlite3 compatibility)",
        "changes": [
            "Fix: Add PostgreSQL cursor wrapper to support method chaining (sqlite3 compatibility)"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.297",
        "title": "Fix: Create critical PostgreSQL tables inline without file dependencies",
        "changes": [
            "Fix: Create critical PostgreSQL tables inline without file dependencies"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.296",
        "title": "Fix: Auto-create PostgreSQL tables on startup if they don't exist",
        "changes": [
            "Fix: Auto-create PostgreSQL tables on startup if they don't exist"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.295",
        "title": "Fix: Convert all SQLite placeholders (?) to PostgreSQL placeholders (%s) for database compatibility",
        "changes": [
            "Fix: Convert all SQLite placeholders (?) to PostgreSQL placeholders (%s) for database compatibility"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.294",
        "title": "Fix: Increase health check delay to 60s and simplify endpoint for faster response",
        "changes": [
            "Fix: Increase health check delay to 60s and simplify endpoint for faster response"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.293",
        "title": "Trigger redeploy with DATABASE_URL configured",
        "changes": [
            "Trigger redeploy with DATABASE_URL configured"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.292",
        "title": "Fix: Support both GROQ_API_KEY and GROQ_API variable names",
        "changes": [
            "Fix: Support both GROQ_API_KEY and GROQ_API variable names"
        ]
    },
    {
        "date": "2026-02-05",
        "version": "22.291",
        "title": "Fix: Add psycopg2-binary to requirements.txt for PostgreSQL support",
        "changes": [
            "Fix: Add psycopg2-binary to requirements.txt for PostgreSQL support"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.290",
        "title": "Test: Trigger webhook deployment with reconnected GitHub integration",
        "changes": [
            "Test: Trigger webhook deployment with reconnected GitHub integration"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.289",
        "title": "Fix: Use DATABASE_URL for pet database connection in Railway",
        "changes": [
            "Fix: Use DATABASE_URL for pet database connection in Railway"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.288",
        "title": "Force rebuild: Update cache bust tag to trigger Railway deployment",
        "changes": [
            "Force rebuild: Update cache bust tag to trigger Railway deployment"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.287",
        "title": "Add critical deployment blocker analysis and solutions",
        "changes": [
            "Add critical deployment blocker analysis and solutions"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.286",
        "title": "FORCE REBUILD: Update railway.toml cache bust - deploy latest code",
        "changes": [
            "FORCE REBUILD: Update railway.toml cache bust - deploy latest code"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.285",
        "title": "Add deployment webhook status report - manual deploy needed",
        "changes": [
            "Add deployment webhook status report - manual deploy needed"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.284",
        "title": "Add flush=True to startup logging for Railway visibility",
        "changes": [
            "Add flush=True to startup logging for Railway visibility"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.283",
        "title": "Update health check endpoint with deployment info - trigger webhook",
        "changes": [
            "Update health check endpoint with deployment info - trigger webhook"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.282",
        "title": "Test webhook trigger - GitHub linked to Railway",
        "changes": [
            "Test webhook trigger - GitHub linked to Railway"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.281",
        "title": "Add deployment fix completion status document",
        "changes": [
            "Add deployment fix completion status document"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.280",
        "title": "Remove node_modules from git tracking and add to gitignore",
        "changes": [
            "Remove node_modules from git tracking and add to gitignore"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.279",
        "title": "Add manual GitHub webhook setup guide",
        "changes": [
            "Add manual GitHub webhook setup guide"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.278",
        "title": "test commit",
        "changes": [
            "test commit"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.277",
        "title": "Add Railway deployment status and troubleshooting guide",
        "changes": [
            "Add Railway deployment status and troubleshooting guide"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.276",
        "title": "Add database connectivity startup logging and deployment diagnosis guide",
        "changes": [
            "Add database connectivity startup logging and deployment diagnosis guide"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.275",
        "title": "Project Completion Report: Phases 1-5 Complete & Deployed",
        "changes": [
            "Project Completion Report: Phases 1-5 Complete & Deployed"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.274",
        "title": "Update database connection to support Railway DATABASE_URL",
        "changes": [
            "Update database connection to support Railway DATABASE_URL"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.273",
        "title": "Add Phase 5 documentation index - central reference for all reports",
        "changes": [
            "Add Phase 5 documentation index - central reference for all reports"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.272",
        "title": "Phase 5: Database Migration Complete - 87.5% (7/8 steps)",
        "changes": [
            "Phase 5: Database Migration Complete - 87.5% (7/8 steps)"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.271",
        "title": "Add Phase 5 Step 7 documentation - all tests passing",
        "changes": [
            "Add Phase 5 Step 7 documentation - all tests passing"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.270",
        "title": "Phase 5 Step 7: PostgreSQL API test suite - all 7 tests passing",
        "changes": [
            "Phase 5 Step 7: PostgreSQL API test suite - all 7 tests passing"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.269",
        "title": "Add Phase 5 Step 6 documentation",
        "changes": [
            "Add Phase 5 Step 6 documentation"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.268",
        "title": "Phase 5 Step 6: Update SQL queries for PostgreSQL compatibility",
        "changes": [
            "Phase 5 Step 6: Update SQL queries for PostgreSQL compatibility"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.267",
        "title": "Phase 5 Step 5: Refactor api.py for PostgreSQL",
        "changes": [
            "Phase 5 Step 5: Refactor api.py for PostgreSQL"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.266",
        "title": "Phase 5 Backend Updated for SQL migration",
        "changes": [
            "Phase 5 Backend Updated for SQL migration"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.265",
        "title": "Add Phase 5 Kickoff: Database Migration Plan (SQLite → PostgreSQL)",
        "changes": [
            "Add Phase 5 Kickoff: Database Migration Plan (SQLite → PostgreSQL)"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.264",
        "title": "🎯 SAVEPOINT: February 4, 2026 - Full Feature & Integrity Stack",
        "changes": [
            "🎯 SAVEPOINT: February 4, 2026 - Full Feature & Integrity Stack"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.263",
        "title": "Implement feedback status updates & organized feedback dashboard",
        "changes": [
            "Implement feedback status updates & organized feedback dashboard"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.262",
        "title": "Fix developer messaging UI - recipient selection & validation",
        "changes": [
            "Fix developer messaging UI - recipient selection & validation"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.261",
        "title": "Add input validation to /api/developer/messages/send endpoint",
        "changes": [
            "Add input validation to /api/developer/messages/send endpoint"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.260",
        "title": "Phase 4E: Complete database schema documentation with ERD, constraints, and comprehensive analysis",
        "changes": [
            "Phase 4E: Complete database schema documentation with ERD, constraints, and comprehensive analysis"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.259",
        "title": "BUGFIX: Fix messaging inbox - send messages to 'messages' table not 'dev_messages' and add notifications to new messages API",
        "changes": [
            "BUGFIX: Fix messaging inbox - send messages to 'messages' table not 'dev_messages' and add notifications to new messages API"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.258",
        "title": "Phase 4D: Add CHECK constraints for data validation - enforce mood (1-10), sleep (0-10), anxiety (0-10), completion (0-1), and other ranges at DB level",
        "changes": [
            "Phase 4D: Add CHECK constraints for data validation - enforce mood (1-10), sleep (0-10), anxiety (0-10), completion (0-1), and other ranges at DB level"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.257",
        "title": "Phase 4B: Add soft delete timestamps (deleted_at) to 17 key tables + optimize indexes for deleted row filtering",
        "changes": [
            "Phase 4B: Add soft delete timestamps (deleted_at) to 17 key tables + optimize indexes for deleted row filtering"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.256",
        "title": "Phase 4A: Add foreign key constraints to all user relationships - enforce data integrity across 40+ tables",
        "changes": [
            "Phase 4A: Add foreign key constraints to all user relationships - enforce data integrity across 40+ tables"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.255",
        "title": "Fix notification handler for message notifications - add click handlers for dev_message and message types to navigate to messages tab",
        "changes": [
            "Fix notification handler for message notifications - add click handlers for dev_message and message types to navigate to messages tab"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.254",
        "title": "✨ Implement comprehensive messaging system with developer feedback dashboard",
        "changes": [
            "✨ Implement comprehensive messaging system with developer feedback dashboard"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.253",
        "title": "Fix: Make loadUserMessages resilient to auth failures during login",
        "changes": [
            "Fix: Make loadUserMessages resilient to auth failures during login"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.252",
        "title": "Fix pet database schema and type conversion issues",
        "changes": [
            "Fix pet database schema and type conversion issues"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.251",
        "title": "Fix: Add proper session authentication to pet and mood endpoints",
        "changes": [
            "Fix: Add proper session authentication to pet and mood endpoints"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.250",
        "title": "DEBUG: Add console logging to messaging functions for troubleshooting",
        "changes": [
            "DEBUG: Add console logging to messaging functions for troubleshooting"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.249",
        "title": "DOCS: Consolidate to single navigation hub - project_management/README.md",
        "changes": [
            "DOCS: Consolidate to single navigation hub - project_management/README.md"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.248",
        "title": "Phase 3 Messaging System - Complete Implementation & Fixes",
        "changes": [
            "Phase 3 Messaging System - Complete Implementation & Fixes"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.247",
        "title": "Revert \"TRIGGER: Force Railway rebuild for updated templates\"",
        "changes": [
            "Revert \"TRIGGER: Force Railway rebuild for updated templates\""
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.246",
        "title": "TRIGGER: Force Railway rebuild for updated templates",
        "changes": [
            "TRIGGER: Force Railway rebuild for updated templates"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.245",
        "title": "DOCS: Comprehensive bug fix summary for Feb 4, 2026",
        "changes": [
            "DOCS: Comprehensive bug fix summary for Feb 4, 2026"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.244",
        "title": "IMPROVE: Better pet database schema migration logic",
        "changes": [
            "IMPROVE: Better pet database schema migration logic"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.243",
        "title": "DOCS: Update to-do and audit docs for Feb 4 bug fixes + messaging feature request",
        "changes": [
            "DOCS: Update to-do and audit docs for Feb 4 bug fixes + messaging feature request"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.242",
        "title": "FIX: AI thinking animation + Per-user pet database isolation",
        "changes": [
            "FIX: AI thinking animation + Per-user pet database isolation"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.241",
        "title": "DOCS: Railway deployment fixes and manual testing checklist (Feb 4, 2026)",
        "changes": [
            "DOCS: Railway deployment fixes and manual testing checklist (Feb 4, 2026)"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.240",
        "title": "FIX: Add gunicorn to requirements.txt (Critical Railway build fix)",
        "changes": [
            "FIX: Add gunicorn to requirements.txt (Critical Railway build fix)"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.239",
        "title": "Add: Railway SECRET_KEY fix documentation",
        "changes": [
            "Add: Railway SECRET_KEY fix documentation"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.238",
        "title": "FIX: Railway crash - Improve SECRET_KEY handling for production stability",
        "changes": [
            "FIX: Railway crash - Improve SECRET_KEY handling for production stability"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.237",
        "title": "FINAL: Security Hardening Complete - Phase 1+2 Summary",
        "changes": [
            "FINAL: Security Hardening Complete - Phase 1+2 Summary"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.236",
        "title": "Update to-do: Mark Phase 2 as COMPLETE",
        "changes": [
            "Update to-do: Mark Phase 2 as COMPLETE"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.235",
        "title": "Add: Phase 2 Completion Report (Input Validation + CSRF + Security Headers)",
        "changes": [
            "Add: Phase 2 Completion Report (Input Validation + CSRF + Security Headers)"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.234",
        "title": "PHASE 2C: Security headers & Content-Type validation",
        "changes": [
            "PHASE 2C: Security headers & Content-Type validation"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.233",
        "title": "PHASE 2B: CSRF protection (Cross-Site Request Forgery)",
        "changes": [
            "PHASE 2B: CSRF protection (Cross-Site Request Forgery)"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.232",
        "title": "PHASE 2A: Input validation (messages, notes, mood ratings)",
        "changes": [
            "PHASE 2A: Input validation (messages, notes, mood ratings)"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.231",
        "title": "Add: Phase 1 Status Complete - Security remediation finished (52% CVSS improvement)",
        "changes": [
            "Add: Phase 1 Status Complete - Security remediation finished (52% CVSS improvement)"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.230",
        "title": "Update to-do.md: Mark Phase 1 security remediation as COMPLETE",
        "changes": [
            "Update to-do.md: Mark Phase 1 security remediation as COMPLETE"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.229",
        "title": "PHASE 1 COMPLETE: Security hardening - auth, FK validation, debug protection, rate limiting",
        "changes": [
            "PHASE 1 COMPLETE: Security hardening - auth, FK validation, debug protection, rate limiting"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.228",
        "title": "Add: Audit report index and navigation guide",
        "changes": [
            "Add: Audit report index and navigation guide"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.227",
        "title": "Add: Security audit summary (plaintext reference guide)",
        "changes": [
            "Add: Security audit summary (plaintext reference guide)"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.226",
        "title": "Update: Bug #3 (API Security) detailed remediation plan",
        "changes": [
            "Update: Bug #3 (API Security) detailed remediation plan"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.225",
        "title": "Add: Comprehensive API Security Audit (193 endpoints analyzed)",
        "changes": [
            "Add: Comprehensive API Security Audit (193 endpoints analyzed)"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.224",
        "title": "Mark Bug #1 (Test Suite) as COMPLETED - 12/13 tests passing",
        "changes": [
            "Mark Bug #1 (Test Suite) as COMPLETED - 12/13 tests passing"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.223",
        "title": "Fix: Test suite now 100% passing (12/13 tests)",
        "changes": [
            "Fix: Test suite now 100% passing (12/13 tests)"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.222",
        "title": "docs: Comprehensive project audit and reorganized priority to-do list",
        "changes": [
            "docs: Comprehensive project audit and reorganized priority to-do list"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.221",
        "title": "docs: Add password reset SMS/email to to-do list for later",
        "changes": [
            "docs: Add password reset SMS/email to to-do list for later"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.220",
        "title": "Revert \"fix: Make password reset email non-blocking to prevent Railway timeout, add SMTP timeout\"",
        "changes": [
            "Revert \"fix: Make password reset email non-blocking to prevent Railway timeout, add SMTP timeout\""
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.219",
        "title": "fix: Make password reset email non-blocking to prevent Railway timeout, add SMTP timeout",
        "changes": [
            "fix: Make password reset email non-blocking to prevent Railway timeout, add SMTP timeout"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.218",
        "title": "fix: Improve clinician search UX - dropdown hidden initially, better help text, search button prominent",
        "changes": [
            "fix: Improve clinician search UX - dropdown hidden initially, better help text, search button prominent"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.217",
        "title": "feat: Improve patient registration flow - UK-only, optional clinician, better UX",
        "changes": [
            "feat: Improve patient registration flow - UK-only, optional clinician, better UX"
        ]
    },
    {
        "date": "2026-02-04",
        "version": "22.216",
        "title": "Fix: Add currentUser to CBT tools API calls (load and save endpoints)",
        "changes": [
            "Fix: Add currentUser to CBT tools API calls (load and save endpoints)"
        ]
    },
    {
        "date": "2026-01-31",
        "version": "22.215",
        "title": "Mobile-first UI: responsive sidebar, cards, forms, modals, ARIA/accessibility improvements",
        "changes": [
            "Mobile-first UI: responsive sidebar, cards, forms, modals, ARIA/accessibility improvements"
        ]
    },
    {
        "date": "2026-01-31",
        "version": "22.214",
        "title": "Revert \"feat: Consolidate navigation with dropdown menu (Option 1 + 3)\"",
        "changes": [
            "Revert \"feat: Consolidate navigation with dropdown menu (Option 1 + 3)\""
        ]
    },
    {
        "date": "2026-01-31",
        "version": "22.213",
        "title": "feat: Consolidate navigation with dropdown menu (Option 1 + 3)",
        "changes": [
            "feat: Consolidate navigation with dropdown menu (Option 1 + 3)"
        ]
    },
    {
        "date": "2026-01-31",
        "version": "22.212",
        "title": "fix: Update tool name and improve error handling",
        "changes": [
            "fix: Update tool name and improve error handling"
        ]
    },
    {
        "date": "2026-01-31",
        "version": "22.211",
        "title": "version log update site visual",
        "changes": [
            "version log update site visual"
        ]
    },
    {
        "date": "2026-01-31",
        "version": "22.210",
        "title": "version log update",
        "changes": [
            "version log update"
        ]
    },
    {
        "date": "2026-01-31",
        "version": "22.209",
        "title": "fix: Critical save/load API endpoints and AI memory integration",
        "changes": [
            "fix: Critical save/load API endpoints and AI memory integration"
        ]
    },
    {
        "date": "2026-01-31",
        "version": "22.208",
        "title": "fix: Resolve duplicate tools and save/load issues",
        "changes": [
            "fix: Resolve duplicate tools and save/load issues"
        ]
    },
    {
        "date": "2026-01-31",
        "version": "22.207",
        "title": "feat: Phase 2 gamification - badges, mood tracking, and streaks",
        "changes": [
            "feat: Phase 2 gamification - badges, mood tracking, and streaks"
        ]
    },
    {
        "date": "2026-01-31",
        "version": "22.206",
        "title": "feat: Phase 1 - CBT Tools Gamification (Emoji Moods, Confetti, Pet Rewards)",
        "changes": [
            "feat: Phase 1 - CBT Tools Gamification (Emoji Moods, Confetti, Pet Rewards)"
        ]
    },
    {
        "date": "2026-01-31",
        "version": "22.205",
        "title": "version number update",
        "changes": [
            "version number update"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.204",
        "title": "fix: Remove all remaining duplicate Flask route functions",
        "changes": [
            "fix: Remove all remaining duplicate Flask route functions"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.203",
        "title": "fix: Remove duplicate function definitions causing Flask route conflicts",
        "changes": [
            "fix: Remove duplicate function definitions causing Flask route conflicts"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.202",
        "title": "fix: CBT tools dashboard backend and AI memory integration",
        "changes": [
            "fix: CBT tools dashboard backend and AI memory integration"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.201",
        "title": "Fix: syntax error in POSITIVE_AFFIRMATIONS array, CBT tools dashboard and persistence, ensure AI listens to all tools",
        "changes": [
            "Fix: syntax error in POSITIVE_AFFIRMATIONS array, CBT tools dashboard and persistence, ensure AI listens to all tools"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.200",
        "title": "New CBT tools added",
        "changes": [
            "New CBT tools added"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.199",
        "title": "fix: Daily Tasks Errors",
        "changes": [
            "fix: Daily Tasks Errors"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.198",
        "title": "Version History Update v1.1",
        "changes": [
            "Version History Update v1.1"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.197",
        "title": "Version History Update",
        "changes": [
            "Version History Update"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.196",
        "title": "Home Page Bug Fix 1.0",
        "changes": [
            "Home Page Bug Fix 1.0"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.195",
        "title": "fix: add detailed error logging and improved error display for mood and gratitude logging",
        "changes": [
            "fix: add detailed error logging and improved error display for mood and gratitude logging"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.194",
        "title": "feat: Home tab, daily tasks, feedback, and polish for Healing Space UK",
        "changes": [
            "feat: Home tab, daily tasks, feedback, and polish for Healing Space UK"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.193",
        "title": "Fix comprehensive dark mode for chat, safety, insights, appointments, and about me tabs",
        "changes": [
            "Fix comprehensive dark mode for chat, safety, insights, appointments, and about me tabs"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.192",
        "title": "Fix dark mode backgrounds for all tabs and dashboard cards",
        "changes": [
            "Fix dark mode backgrounds for all tabs and dashboard cards"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.191",
        "title": "Update app header branding to Healing Space UK in web UI",
        "changes": [
            "Update app header branding to Healing Space UK in web UI"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.190",
        "title": "Update web UI branding to Healing Space UK",
        "changes": [
            "Update web UI branding to Healing Space UK"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.189",
        "title": "Update all branding to Healing Space UK",
        "changes": [
            "Update all branding to Healing Space UK"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.188",
        "title": "docs update",
        "changes": [
            "docs update"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.187",
        "title": "Fix dark/light theme for all tabs and cards",
        "changes": [
            "Fix dark/light theme for all tabs and cards"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.186",
        "title": "Crash bug fix FlaskApp location incorrect",
        "changes": [
            "Crash bug fix FlaskApp location incorrect"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.185",
        "title": "UI FIX",
        "changes": [
            "UI FIX"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.184",
        "title": "Add full CRUD endpoints, audit logging, and AI memory integration for all new CBT tools (breathing, relaxation, sleep, core belief, exposure, problem-solving, coping cards, self-compassion, values, goals)",
        "changes": [
            "Add full CRUD endpoints, audit logging, and AI memory integration for all new CBT tools (breathing, relaxation, sleep, core belief, exposure, problem-solving, coping cards, self-compassion, values, goals)"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.183",
        "title": "feat: Add site-wide dark mode with toggle in Settings",
        "changes": [
            "feat: Add site-wide dark mode with toggle in Settings"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.182",
        "title": "feat: Discord-style community with channels, threads, and pinned posts",
        "changes": [
            "feat: Discord-style community with channels, threads, and pinned posts"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.181",
        "title": "version_history_update",
        "changes": [
            "version_history_update"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.180",
        "title": "feat: Add category system, inline replies, and auto-refresh to community",
        "changes": [
            "feat: Add category system, inline replies, and auto-refresh to community"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.179",
        "title": "feat: add reply deletion and multiple reaction emojis",
        "changes": [
            "feat: add reply deletion and multiple reaction emojis"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.178",
        "title": "fix: add missing flagged/flag_reason to ContentModerator",
        "changes": [
            "fix: add missing flagged/flag_reason to ContentModerator"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.177",
        "title": "fix: pet database persistence and content moderator",
        "changes": [
            "fix: pet database persistence and content moderator"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.176",
        "title": "fix:PT3 ensure pet table exists before all pet DB access (robust pet features after Railway reset)",
        "changes": [
            "fix:PT3 ensure pet table exists before all pet DB access (robust pet features after Railway reset)"
        ]
    },
    {
        "date": "2026-01-30",
        "version": "22.175",
        "title": "fix:PT2 ensure pet table exists before all pet DB access (robust pet features after Railway reset)",
        "changes": [
            "fix:PT2 ensure pet table exists before all pet DB access (robust pet features after Railway reset)"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.174",
        "title": "fix: ensure pet table exists before all pet DB access (robust pet features after Railway reset)",
        "changes": [
            "fix: ensure pet table exists before all pet DB access (robust pet features after Railway reset)"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.173",
        "title": "Update audit.md - Phase 6 complete (88% resolution rate)",
        "changes": [
            "Update audit.md - Phase 6 complete (88% resolution rate)"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.172",
        "title": "Phase 6: Fix Medium (P2) security and code quality issues",
        "changes": [
            "Phase 6: Fix Medium (P2) security and code quality issues"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.171",
        "title": "Phase 6: Fix all Critical (P0) and High (P1) security issues",
        "changes": [
            "Phase 6: Fix all Critical (P0) and High (P1) security issues"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.170",
        "title": "Phase 6: Fresh security audit - 16 new issues identified",
        "changes": [
            "Phase 6: Fresh security audit - 16 new issues identified"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.169",
        "title": "Merge remote changes and resolve VERSION_HISTORY conflict",
        "changes": [
            "Merge remote changes and resolve VERSION_HISTORY conflict"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.168",
        "title": "Fix: AI summary endpoint - remove non-existent created_at column from users query",
        "changes": [
            "Fix: AI summary endpoint - remove non-existent created_at column from users query"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.167",
        "title": "Phase 5: Web/Android audit - Fix pet endpoints, duplicate routes, exception leaks",
        "changes": [
            "Phase 5: Web/Android audit - Fix pet endpoints, duplicate routes, exception leaks"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.166",
        "title": "Phase 5: Web/Android audit - Fix pet endpoints, duplicate routes, exception leaks",
        "changes": [
            "Phase 5: Web/Android audit - Fix pet endpoints, duplicate routes, exception leaks"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.165",
        "title": "fix: Harden /api/professional/ai-summary endpoint (null checks, safe defaults, debug logging, robust fallback)",
        "changes": [
            "fix: Harden /api/professional/ai-summary endpoint (null checks, safe defaults, debug logging, robust fallback)"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.164",
        "title": "Fix: Add None checks to AI summary prompt string slicing",
        "changes": [
            "Fix: Add None checks to AI summary prompt string slicing"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.163",
        "title": "fix: Set Updates tab as default for changelog debug (shows changelog on load)",
        "changes": [
            "fix: Set Updates tab as default for changelog debug (shows changelog on load)"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.162",
        "title": "Add null safety and error logging to AI summary endpoint",
        "changes": [
            "Add null safety and error logging to AI summary endpoint"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.161",
        "title": "Enhance AI clinical summary and fix patient charts",
        "changes": [
            "Enhance AI clinical summary and fix patient charts"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.160",
        "title": "Fix: Add missing clinician parameter to patient detail endpoint",
        "changes": [
            "Fix: Add missing clinician parameter to patient detail endpoint"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.159",
        "title": "Update VERSION_HISTORY.txt with today's fixes",
        "changes": [
            "Update VERSION_HISTORY.txt with today's fixes"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.158",
        "title": "Fix: Clinician dashboard patient data and AI insights",
        "changes": [
            "Fix: Clinician dashboard patient data and AI insights"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.157",
        "title": "Update VERSION_HISTORY.txt with recent commits",
        "changes": [
            "Update VERSION_HISTORY.txt with recent commits"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.156",
        "title": "Fix: loadInsights sends role=clinician for clinician users (enables clinician data/AI insights)",
        "changes": [
            "Fix: loadInsights sends role=clinician for clinician users (enables clinician data/AI insights)"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.155",
        "title": "Fix: /api/insights always returns avg_mood, avg_sleep, and trend (prevents frontend errors on empty data)",
        "changes": [
            "Fix: /api/insights always returns avg_mood, avg_sleep, and trend (prevents frontend errors on empty data)"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.154",
        "title": "Fix: remove syntax error in /api/pet/status endpoint (no nested try)",
        "changes": [
            "Fix: remove syntax error in /api/pet/status endpoint (no nested try)"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.153",
        "title": "Chore: trigger Railway deploy (trivial comment change)",
        "changes": [
            "Chore: trigger Railway deploy (trivial comment change)"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.152",
        "title": "Fix: Insights always sends prompt, pet endpoints handle missing user/pet, frontend sends username for pet reward",
        "changes": [
            "Fix: Insights always sends prompt, pet endpoints handle missing user/pet, frontend sends username for pet reward"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.151",
        "title": "UI: Add show/hide toggle for PIN fields on all login forms",
        "changes": [
            "UI: Add show/hide toggle for PIN fields on all login forms"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.150",
        "title": "Frontend: always use credentials: include in fetch for CSRF/session reliability",
        "changes": [
            "Frontend: always use credentials: include in fetch for CSRF/session reliability"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.149",
        "title": "Fix CSRF token endpoint: resolve secrets shadowing, use stdlib secrets for token generation, ensure session cookie set",
        "changes": [
            "Fix CSRF token endpoint: resolve secrets shadowing, use stdlib secrets for token generation, ensure session cookie set"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.148",
        "title": "Add Phase 4 UX enhancements: onboarding, accessibility, mobile",
        "changes": [
            "Add Phase 4 UX enhancements: onboarding, accessibility, mobile"
        ]
    },
    {
        "date": "2026-01-29",
        "version": "22.147",
        "title": "Set up venv, install all dependencies, playwright, and fixed test environment. Ready for further dev and testing.",
        "changes": [
            "Set up venv, install all dependencies, playwright, and fixed test environment. Ready for further dev and testing."
        ]
    },
    {
        "date": "2026-01-28",
        "version": "22.146",
        "title": "Fix TherapistAI indentation error (production boot fix)",
        "changes": [
            "Fix TherapistAI indentation error (production boot fix)"
        ]
    },
    {
        "date": "2026-01-28",
        "version": "22.145",
        "title": "Add get_insight method to TherapistAI for insights endpoint compatibility",
        "changes": [
            "Add get_insight method to TherapistAI for insights endpoint compatibility"
        ]
    },
    {
        "date": "2026-01-28",
        "version": "22.144",
        "title": "Refactor insights endpoint: custom date range, AI prompt, clinician/patient narrative",
        "changes": [
            "Refactor insights endpoint: custom date range, AI prompt, clinician/patient narrative"
        ]
    },
    {
        "date": "2026-01-28",
        "version": "22.143",
        "title": "Updated AUDIT.md with dynamic audit results",
        "changes": [
            "Updated AUDIT.md with dynamic audit results"
        ]
    },
    {
        "date": "2026-01-28",
        "version": "22.142",
        "title": "Rollback: restore project to v1.0.46 (2026-01-26) - Fix chat input layout for mobile",
        "changes": [
            "Rollback: restore project to v1.0.46 (2026-01-26) - Fix chat input layout for mobile"
        ]
    },
    {
        "date": "2026-01-26",
        "version": "22.141",
        "title": "Fix chat input layout for mobile - stack textarea above buttons",
        "changes": [
            "Fix chat input layout for mobile - stack textarea above buttons"
        ]
    },
    {
        "date": "2026-01-26",
        "version": "22.140",
        "title": "Add Updates tab, notification management, and chat improvements",
        "changes": [
            "Add Updates tab, notification management, and chat improvements"
        ]
    },
    {
        "date": "2026-01-26",
        "version": "22.139",
        "title": "Improve AI chat: voice input, thinking animation, natural responses",
        "changes": [
            "Improve AI chat: voice input, thinking animation, natural responses"
        ]
    },
    {
        "date": "2026-01-25",
        "version": "22.138",
        "title": "message bugs update",
        "changes": [
            "message bugs update"
        ]
    },
    {
        "date": "2026-01-25",
        "version": "22.137",
        "title": "API update",
        "changes": [
            "API update"
        ]
    },
    {
        "date": "2026-01-25",
        "version": "22.136",
        "title": "Remove package.json to fix Railway Python deploy (prevent npm ci)",
        "changes": [
            "Remove package.json to fix Railway Python deploy (prevent npm ci)"
        ]
    },
    {
        "date": "2026-01-25",
        "version": "22.135",
        "title": "Fix Railway deploy: allow pip install in Nixpacks immutable env",
        "changes": [
            "Fix Railway deploy: allow pip install in Nixpacks immutable env"
        ]
    },
    {
        "date": "2026-01-25",
        "version": "22.134",
        "title": "Add nixpacks.toml to force Python dependency install on Railway",
        "changes": [
            "Add nixpacks.toml to force Python dependency install on Railway"
        ]
    },
    {
        "date": "2026-01-25",
        "version": "22.133",
        "title": "Add mobile app (Capacitor) and deployment documentation",
        "changes": [
            "Add mobile app (Capacitor) and deployment documentation"
        ]
    },
    {
        "date": "2026-01-24",
        "version": "22.132",
        "title": "Major update: Fix database concurrency, user deletion, and messaging system",
        "changes": [
            "Major update: Fix database concurrency, user deletion, and messaging system"
        ]
    },
    {
        "date": "2026-01-24",
        "version": "22.131",
        "title": "Add developer dashboard",
        "changes": [
            "Add developer dashboard"
        ]
    },
    {
        "date": "2026-01-23",
        "version": "22.130",
        "title": "Add developer dashboard",
        "changes": [
            "Add developer dashboard"
        ]
    },
    {
        "date": "2026-01-24",
        "version": "22.129",
        "title": "docs: add Additional Features & Roadmap under future updates and ideas (2026-01-24)",
        "changes": [
            "docs: add Additional Features & Roadmap under future updates and ideas (2026-01-24)"
        ]
    },
    {
        "date": "2026-01-24",
        "version": "22.128",
        "title": "docs: update repository README and documentation index to reflect current features and usage (2026-01-24)",
        "changes": [
            "docs: update repository README and documentation index to reflect current features and usage (2026-01-24)"
        ]
    },
    {
        "date": "2026-01-22",
        "version": "22.127",
        "title": "legal: add role-specific disclaimers with comprehensive UK legal protection",
        "changes": [
            "legal: add role-specific disclaimers with comprehensive UK legal protection"
        ]
    },
    {
        "date": "2026-01-22",
        "version": "22.126",
        "title": "docs: strengthen pitch—emphasize AI bridging gap between sessions and patient continuity",
        "changes": [
            "docs: strengthen pitch—emphasize AI bridging gap between sessions and patient continuity"
        ]
    },
    {
        "date": "2026-01-22",
        "version": "22.125",
        "title": "docs: make clinician/patient guides website-only (remove developer instructions)",
        "changes": [
            "docs: make clinician/patient guides website-only (remove developer instructions)"
        ]
    },
    {
        "date": "2026-01-22",
        "version": "22.124",
        "title": "docs: add non-technical web access guide and surface it in clinician/patient guides",
        "changes": [
            "docs: add non-technical web access guide and surface it in clinician/patient guides"
        ]
    },
    {
        "date": "2026-01-22",
        "version": "22.123",
        "title": "ci: stabilize workflow, disable pytest plugin autoload, set test env vars",
        "changes": [
            "ci: stabilize workflow, disable pytest plugin autoload, set test env vars"
        ]
    },
    {
        "date": "2026-01-22",
        "version": "22.122",
        "title": "chore: timezone-aware datetimes; optional browser smoke test + CI step",
        "changes": [
            "chore: timezone-aware datetimes; optional browser smoke test + CI step"
        ]
    },
    {
        "date": "2026-01-22",
        "version": "22.121",
        "title": "fix: robust FHIR export handling; add integration chat+FHIR tests; add CI workflow",
        "changes": [
            "fix: robust FHIR export handling; add integration chat+FHIR tests; add CI workflow"
        ]
    },
    {
        "date": "2026-01-22",
        "version": "22.120",
        "title": "chore: normalize timestamp queries, fix analytics; tests passing",
        "changes": [
            "chore: normalize timestamp queries, fix analytics; tests passing"
        ]
    },
    {
        "date": "2026-01-22",
        "version": "22.119",
        "title": "fix(clinician): show appointments in patient dashboard; add attendance controls",
        "changes": [
            "fix(clinician): show appointments in patient dashboard; add attendance controls"
        ]
    },
    {
        "date": "2026-01-22",
        "version": "22.118",
        "title": "feat: appointment attendance, notification fixes, deploy automation",
        "changes": [
            "feat: appointment attendance, notification fixes, deploy automation"
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.117",
        "title": "Expand pet game: mini-games, mood, journal, daily challenges, healthy habit rewards, and bugfixes. All tests passing.",
        "changes": [
            "Expand pet game: mini-games, mood, journal, daily challenges, healthy habit rewards, and bugfixes. All tests passing."
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.116",
        "title": "Fix patient analytics mood query: use entrestamp/mood_val instead of timestamp/mood_score",
        "changes": [
            "Fix patient analytics mood query: use entrestamp/mood_val instead of timestamp/mood_score"
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.115",
        "title": "Remove Analytics tab, redesign Appointments with calendar views (month/week/day) for scalability",
        "changes": [
            "Remove Analytics tab, redesign Appointments with calendar views (month/week/day) for scalability"
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.114",
        "title": "Fix active patient tracking: update last_login on login, add clickable active count with details modal",
        "changes": [
            "Fix active patient tracking: update last_login on login, add clickable active count with details modal"
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.113",
        "title": "Fix clinical_scales column names (scale_name/score not scale_type/total_score)",
        "changes": [
            "Fix clinical_scales column names (scale_name/score not scale_type/total_score)"
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.112",
        "title": "Add analytics debug endpoint and refresh button",
        "changes": [
            "Add analytics debug endpoint and refresh button"
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.111",
        "title": "Add documentation for Railway database wipe",
        "changes": [
            "Add documentation for Railway database wipe"
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.110",
        "title": "Add admin database wipe endpoint and web interface for Railway",
        "changes": [
            "Add admin database wipe endpoint and web interface for Railway"
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.109",
        "title": "Add detailed logging to auth endpoints and update version to v2026.01.19.5",
        "changes": [
            "Add detailed logging to auth endpoints and update version to v2026.01.19.5"
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.108",
        "title": "Fix password reset email error handling - make SMTP failures graceful",
        "changes": [
            "Fix password reset email error handling - make SMTP failures graceful"
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.107",
        "title": "Add 2FA verification system for signup with email and SMS support",
        "changes": [
            "Add 2FA verification system for signup with email and SMS support"
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.106",
        "title": "database wipe 3.3.5",
        "changes": [
            "database wipe 3.3.5"
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.105",
        "title": "Fix alerts query to use status column and add DOM render delay for analytics load",
        "changes": [
            "Fix alerts query to use status column and add DOM render delay for analytics load"
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.104",
        "title": "Add comprehensive logging for analytics dashboard and auto-load on clinician login",
        "changes": [
            "Add comprehensive logging for analytics dashboard and auto-load on clinician login"
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.103",
        "title": "Add migration for chat_session_id column and improve chat session creation error handling",
        "changes": [
            "Add migration for chat_session_id column and improve chat session creation error handling"
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.102",
        "title": "Add comprehensive error handling to AI chat endpoint - better debugging and clearer error messages",
        "changes": [
            "Add comprehensive error handling to AI chat endpoint - better debugging and clearer error messages"
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.101",
        "title": "Fix analytics display handling null values, add patient notification when appointment cancelled, therapy notes already timestamped",
        "changes": [
            "Fix analytics display handling null values, add patient notification when appointment cancelled, therapy notes already timestamped"
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.100",
        "title": "Restructure clinician dashboard: Overview shows only 3 stat cards, charts moved to Analytics tab",
        "changes": [
            "Restructure clinician dashboard: Overview shows only 3 stat cards, charts moved to Analytics tab"
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.99",
        "title": "Fix analytics dashboard patient counting queries",
        "changes": [
            "Fix analytics dashboard patient counting queries"
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.98",
        "title": "Add organized subtabs for patient detail view",
        "changes": [
            "Add organized subtabs for patient detail view"
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.97",
        "title": "Reorganize clinician dashboard with organized subtabs",
        "changes": [
            "Reorganize clinician dashboard with organized subtabs"
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.96",
        "title": "DB quick update",
        "changes": [
            "DB quick update"
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.95",
        "title": "Fix login error handling and appointment display issues",
        "changes": [
            "Fix login error handling and appointment display issues"
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.94",
        "title": "Add clinician analytics dashboard, report generator, and patient search features",
        "changes": [
            "Add clinician analytics dashboard, report generator, and patient search features"
        ]
    },
    {
        "date": "2026-01-19",
        "version": "22.93",
        "title": "docs: Add comprehensive Android app conversion guide",
        "changes": [
            "docs: Add comprehensive Android app conversion guide"
        ]
    },
    {
        "date": "2026-01-18",
        "version": "22.92",
        "title": "fix: Load appointments automatically when clinician logs in",
        "changes": [
            "fix: Load appointments automatically when clinician logs in"
        ]
    },
    {
        "date": "2026-01-18",
        "version": "22.91",
        "title": "fix: Force refresh of appointments list by disabling browser cache",
        "changes": [
            "fix: Force refresh of appointments list by disabling browser cache"
        ]
    },
    {
        "date": "2026-01-18",
        "version": "22.90",
        "title": "fix: Organize clinician appointments into clear sections",
        "changes": [
            "fix: Organize clinician appointments into clear sections"
        ]
    },
    {
        "date": "2026-01-18",
        "version": "22.89",
        "title": "fix: Add patient notifications for appointments and improve clinician response visibility",
        "changes": [
            "fix: Add patient notifications for appointments and improve clinician response visibility"
        ]
    },
    {
        "date": "2026-01-18",
        "version": "22.88",
        "title": "feat: Auto-training on Railway + local dev setup",
        "changes": [
            "feat: Auto-training on Railway + local dev setup"
        ]
    },
    {
        "date": "2026-01-18",
        "version": "22.87",
        "title": "feat: Background AI training system for independent learning",
        "changes": [
            "feat: Background AI training system for independent learning"
        ]
    },
    {
        "date": "2026-01-18",
        "version": "22.86",
        "title": "feat: Multiple chat sessions with full clinician/ML access",
        "changes": [
            "feat: Multiple chat sessions with full clinician/ML access"
        ]
    },
    {
        "date": "2026-01-18",
        "version": "22.85",
        "title": "feat: Add chat search, timestamps, and export with date range",
        "changes": [
            "feat: Add chat search, timestamps, and export with date range"
        ]
    },
    {
        "date": "2026-01-18",
        "version": "22.84",
        "title": "docs: Add comprehensive web app validation report",
        "changes": [
            "docs: Add comprehensive web app validation report"
        ]
    },
    {
        "date": "2026-01-18",
        "version": "22.83",
        "title": "Add diagnostic page for testing JavaScript loading",
        "changes": [
            "Add diagnostic page for testing JavaScript loading"
        ]
    },
    {
        "date": "2026-01-18",
        "version": "22.82",
        "title": "CRITICAL FIX: Remove broken text breaking entire JavaScript execution",
        "changes": [
            "CRITICAL FIX: Remove broken text breaking entire JavaScript execution"
        ]
    },
    {
        "date": "2026-01-18",
        "version": "22.81",
        "title": "Fix: Remove duplicate checkPetReturn function causing syntax error",
        "changes": [
            "Fix: Remove duplicate checkPetReturn function causing syntax error"
        ]
    },
    {
        "date": "2026-01-18",
        "version": "22.80",
        "title": "Fix: Remove orphaned duplicate code causing login function to not load",
        "changes": [
            "Fix: Remove orphaned duplicate code causing login function to not load"
        ]
    },
    {
        "date": "2026-01-18",
        "version": "22.79",
        "title": "fix: update node version in Dockerfile",
        "changes": [
            "fix: update node version in Dockerfile"
        ]
    },
    {
        "date": "2026-01-18",
        "version": "22.78",
        "title": "login issues v1.8",
        "changes": [
            "login issues v1.8"
        ]
    },
    {
        "date": "2026-01-18",
        "version": "22.77",
        "title": "docs: update copilot instructions for web API",
        "changes": [
            "docs: update copilot instructions for web API"
        ]
    },
    {
        "date": "2026-01-18",
        "version": "22.76",
        "title": "landing page issue",
        "changes": [
            "landing page issue"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.75",
        "title": "feat: Add model training script and fix auth flow",
        "changes": [
            "feat: Add model training script and fix auth flow"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.74",
        "title": "1.1",
        "changes": [
            "1.1"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.73",
        "title": "login flow bug fix",
        "changes": [
            "login flow bug fix"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.72",
        "title": "index missed fix",
        "changes": [
            "index missed fix"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.71",
        "title": "Menu Bug Fix",
        "changes": [
            "Menu Bug Fix"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.70",
        "title": "Fix: Remove duplicate walkCountdownInterval declarations causing syntax error",
        "changes": [
            "Fix: Remove duplicate walkCountdownInterval declarations causing syntax error"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.69",
        "title": "Add version tracking and debug logs for auth functions",
        "changes": [
            "Add version tracking and debug logs for auth functions"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.68",
        "title": "Add cache-busting meta tags to fix showClinicianAuth function not loading",
        "changes": [
            "Add cache-busting meta tags to fix showClinicianAuth function not loading"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.67",
        "title": "Fix pet game: increase modal z-index, add 30min walk cooldown with countdown timer, show rewards",
        "changes": [
            "Fix pet game: increase modal z-index, add 30min walk cooldown with countdown timer, show rewards"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.66",
        "title": "Fix: Show appointments from last 30 days in clinician view (prevent disappearing after patient response)",
        "changes": [
            "Fix: Show appointments from last 30 days in clinician view (prevent disappearing after patient response)"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.65",
        "title": "Add bidirectional appointments system with patient acknowledgment and response tracking",
        "changes": [
            "Add bidirectional appointments system with patient acknowledgment and response tracking"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.64",
        "title": "Fix export errors and enhance signup forms",
        "changes": [
            "Fix export errors and enhance signup forms"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.63",
        "title": "Documentation: Add sleep chart feature documentation",
        "changes": [
            "Documentation: Add sleep chart feature documentation"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.62",
        "title": "Feature: Add sleep chart and custom date ranges to insights",
        "changes": [
            "Feature: Add sleep chart and custom date ranges to insights"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.61",
        "title": "Fix: Insights API column name mismatch",
        "changes": [
            "Fix: Insights API column name mismatch"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.60",
        "title": "Complete audit: All features verified and documented",
        "changes": [
            "Complete audit: All features verified and documented"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.59",
        "title": "Add appointment calendar system to web interface",
        "changes": [
            "Add appointment calendar system to web interface"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.58",
        "title": "Add show/hide password toggle to login screens",
        "changes": [
            "Add show/hide password toggle to login screens"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.57",
        "title": "Fix: Separate desktop and web code, fix tkinter import errors",
        "changes": [
            "Fix: Separate desktop and web code, fix tkinter import errors"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.56",
        "title": "Fix: Add About Me page, fix PDF/CSV exports with reportlab",
        "changes": [
            "Fix: Add About Me page, fix PDF/CSV exports with reportlab"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.55",
        "title": "Add API endpoints for appointments and patient profile",
        "changes": [
            "Add API endpoints for appointments and patient profile"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.54",
        "title": "Deploy to Railway - 2026-01-17 17:48:01",
        "changes": [
            "Deploy to Railway - 2026-01-17 17:48:01"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.53",
        "title": "Add patient About Me page and personal PDF export",
        "changes": [
            "Add patient About Me page and personal PDF export"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.52",
        "title": "Add completion summary for appointment system",
        "changes": [
            "Add completion summary for appointment system"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.51",
        "title": "Add clinician appointment calendar with PDF reports and notifications",
        "changes": [
            "Add clinician appointment calendar with PDF reports and notifications"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.50",
        "title": "Organize all documentation in documentation/ folder with comprehensive coverage",
        "changes": [
            "Organize all documentation in documentation/ folder with comprehensive coverage"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.49",
        "title": "Add comprehensive user guide for patients and clinicians",
        "changes": [
            "Add comprehensive user guide for patients and clinicians"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.48",
        "title": "Implement pet care features and assessment limits",
        "changes": [
            "Implement pet care features and assessment limits"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.47",
        "title": "Fix missing time import in api.py",
        "changes": [
            "Fix missing time import in api.py"
        ]
    },
    {
        "date": "2026-01-17",
        "version": "22.46",
        "title": "Trigger Railway redeploy",
        "changes": [
            "Trigger Railway redeploy"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.45",
        "title": "Add pet rewards for all self-care activities",
        "changes": [
            "Add pet rewards for all self-care activities"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.44",
        "title": "Add session persistence and Remember Me functionality",
        "changes": [
            "Add session persistence and Remember Me functionality"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.43",
        "title": "Complete AI memory integration and chat initialization system",
        "changes": [
            "Complete AI memory integration and chat initialization system"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.42",
        "title": "Require full name, DOB, and medical conditions on patient signup",
        "changes": [
            "Require full name, DOB, and medical conditions on patient signup"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.41",
        "title": "Fix chat history loading with correct function names and async flow",
        "changes": [
            "Fix chat history loading with correct function names and async flow"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.40",
        "title": "Fix AI chat, add persistent chat history, make therapy default tab, include all patient data in clinician dashboard",
        "changes": [
            "Fix AI chat, add persistent chat history, make therapy default tab, include all patient data in clinician dashboard"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.39",
        "title": "Add deployment checklist for Railway setup",
        "changes": [
            "Add deployment checklist for Railway setup"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.38",
        "title": "Add Railway deployment support with GitHub Actions for 8pm mood reminders",
        "changes": [
            "Add Railway deployment support with GitHub Actions for 8pm mood reminders"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.37",
        "title": "Complete 8pm mood reminder system with cron automation",
        "changes": [
            "Complete 8pm mood reminder system with cron automation"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.36",
        "title": "Add cron job setup for 8pm mood reminders",
        "changes": [
            "Add cron job setup for 8pm mood reminders"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.35",
        "title": "clin notes/ai tracking/dupe prevention implementattion",
        "changes": [
            "clin notes/ai tracking/dupe prevention implementattion"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.34",
        "title": "overhall v1.45",
        "changes": [
            "overhall v1.45"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.33",
        "title": "Add Railway volume support",
        "changes": [
            "Add Railway volume support"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.32",
        "title": "Patient approval udate v1.1",
        "changes": [
            "Patient approval udate v1.1"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.31",
        "title": "email/api update",
        "changes": [
            "email/api update"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.30",
        "title": "clin dash update",
        "changes": [
            "clin dash update"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.29",
        "title": "Add implementation summary for email/phone and password reset features",
        "changes": [
            "Add implementation summary for email/phone and password reset features"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.28",
        "title": "Add email/phone to signup, forgot password/PIN functionality with email reset, and PostgreSQL setup guide",
        "changes": [
            "Add email/phone to signup, forgot password/PIN functionality with email reset, and PostgreSQL setup guide"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.27",
        "title": "Fix pending approvals not showing - correct property name from approvals to pending_approvals",
        "changes": [
            "Fix pending approvals not showing - correct property name from approvals to pending_approvals"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.26",
        "title": "Fix JavaScript syntax error - incorrect quote escaping in startAdventure function",
        "changes": [
            "Fix JavaScript syntax error - incorrect quote escaping in startAdventure function"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.25",
        "title": "Add explicit pointer-events: auto and console logging to debug landing page button clicks",
        "changes": [
            "Add explicit pointer-events: auto and console logging to debug landing page button clicks"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.24",
        "title": "Fix landing page buttons - remove stacking context from app-container and add explicit z-index to buttons",
        "changes": [
            "Fix landing page buttons - remove stacking context from app-container and add explicit z-index to buttons"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.23",
        "title": "Move disclaimer to registration flow - shows after user selects patient/clinician during signup only",
        "changes": [
            "Move disclaimer to registration flow - shows after user selects patient/clinician during signup only"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.22",
        "title": "Fix landing page button clicks - add z-index to auth-box",
        "changes": [
            "Fix landing page button clicks - add z-index to auth-box"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.21",
        "title": "Fix login after disclaimer acceptance - use stored auth data instead of re-authenticating",
        "changes": [
            "Fix login after disclaimer acceptance - use stored auth data instead of re-authenticating"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.20",
        "title": "Fix z-index issue on landing page - auth screen now properly overlays app",
        "changes": [
            "Fix z-index issue on landing page - auth screen now properly overlays app"
        ]
    },
    {
        "date": "2026-01-16",
        "version": "22.19",
        "title": "Complete pet game implementation with shop, declutter, adventure, time decay + move menu to left sidebar",
        "changes": [
            "Complete pet game implementation with shop, declutter, adventure, time decay + move menu to left sidebar"
        ]
    },
    {
        "date": "2026-01-14",
        "version": "22.18",
        "title": "database reset",
        "changes": [
            "database reset"
        ]
    },
    {
        "date": "2026-01-14",
        "version": "22.17",
        "title": "Add developer README PDF and database reset endpoint for testing",
        "changes": [
            "Add developer README PDF and database reset endpoint for testing"
        ]
    },
    {
        "date": "2026-01-14",
        "version": "22.16",
        "title": "Dev Files Update (v1.0.1)",
        "changes": [
            "Dev Files Update (v1.0.1)"
        ]
    },
    {
        "date": "2026-01-14",
        "version": "22.15",
        "title": "Fix missing clinician_id column and add password special character requirement for both patient and clinician registration",
        "changes": [
            "Fix missing clinician_id column and add password special character requirement for both patient and clinician registration"
        ]
    },
    {
        "date": "2026-01-14",
        "version": "22.14",
        "title": "Add legal disclaimer, landing page for clinician/patient separation, and PIN requirement for clinician registration",
        "changes": [
            "Add legal disclaimer, landing page for clinician/patient separation, and PIN requirement for clinician registration"
        ]
    },
    {
        "date": "2026-01-14",
        "version": "22.13",
        "title": "Add comprehensive documentation for new features",
        "changes": [
            "Add comprehensive documentation for new features"
        ]
    },
    {
        "date": "2026-01-14",
        "version": "22.12",
        "title": "Add 2FA PIN authentication, password strength validation, patient approval workflow, and notification system",
        "changes": [
            "Add 2FA PIN authentication, password strength validation, patient approval workflow, and notification system"
        ]
    },
    {
        "date": "2026-01-14",
        "version": "22.11",
        "title": "Implement professional clinician system: clinician registration, patient-clinician linking, role-based dashboard access, clinician filtering",
        "changes": [
            "Implement professional clinician system: clinician registration, patient-clinician linking, role-based dashboard access, clinician filtering"
        ]
    },
    {
        "date": "2026-01-14",
        "version": "22.10",
        "title": "Add ALL missing features: Community Board, Safety Plan, Progress Insights with charts, CSV/PDF export, Sleep Hygiene, Professional Dashboard - complete feature parity with desktop app",
        "changes": [
            "Add ALL missing features: Community Board, Safety Plan, Progress Insights with charts, CSV/PDF export, Sleep Hygiene, Professional Dashboard - complete feature parity with desktop app"
        ]
    },
    {
        "date": "2026-01-14",
        "version": "22.9",
        "title": "Complete feature implementation: all original app functionality now in web version",
        "changes": [
            "Complete feature implementation: all original app functionality now in web version"
        ]
    },
    {
        "date": "2026-01-14",
        "version": "22.8",
        "title": "database update",
        "changes": [
            "database update"
        ]
    },
    {
        "date": "2026-01-12",
        "version": "22.7",
        "title": "Fix registration error: remove main. prefix from hash functions",
        "changes": [
            "Fix registration error: remove main. prefix from hash functions"
        ]
    },
    {
        "date": "2026-01-12",
        "version": "22.6",
        "title": "push for web app",
        "changes": [
            "push for web app"
        ]
    },
    {
        "date": "2026-01-12",
        "version": "22.5",
        "title": "Fix syntax error in api.py hash_pin function",
        "changes": [
            "Fix syntax error in api.py hash_pin function"
        ]
    },
    {
        "date": "2026-01-12",
        "version": "22.4",
        "title": "Fix Railway deployment: Remove tkinter dependency from API",
        "changes": [
            "Fix Railway deployment: Remove tkinter dependency from API"
        ]
    },
    {
        "date": "2026-01-12",
        "version": "22.3",
        "title": "Add Railway deployment guide (with placeholders for secrets)",
        "changes": [
            "Add Railway deployment guide (with placeholders for secrets)"
        ]
    },
    {
        "date": "2026-01-12",
        "version": "22.2",
        "title": "Add Flask API for Railway deployment",
        "changes": [
            "Add Flask API for Railway deployment"
        ]
    },
    {
        "date": "2026-01-12",
        "version": "22.1",
        "title": "Initial commit: Mental health companion app with AI therapy",
        "changes": [
            "Initial commit: Mental health companion app with AI therapy"
        ]
    }
];