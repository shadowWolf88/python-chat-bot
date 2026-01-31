const APP_UPDATES = [
    {
        date: '2026-01-31',
        version: '22.1',
        title: 'fix: Critical save/load API endpoints and AI memory integration',
        changes: [
            'fix: Critical save/load API endpoints and AI memory integration',
        ]
    },
    {
        date: '2026-01-31',
        version: '22.0',
        title: 'fix: Resolve duplicate tools and save/load issues',
        changes: [
            'fix: Resolve duplicate tools and save/load issues',
        ]
    },
    {
        date: '2026-01-31',
        version: '21.9',
        title: 'feat: Phase 2 gamification - badges, mood tracking, and streaks',
        changes: [
            'feat: Phase 2 gamification - badges, mood tracking, and streaks',
        ]
    },
    {
        date: '2026-01-31',
        version: '21.8',
        title: 'feat: Phase 1 - CBT Tools Gamification (Emoji Moods, Confetti, Pet Rewards)',
        changes: [
            'feat: Phase 1 - CBT Tools Gamification (Emoji Moods, Confetti, Pet Rewards)',
        ]
    },
    {
        date: '2026-01-31',
        version: '21.7',
        title: 'version number update',
        changes: [
            'version number update',
        ]
    },
    {
        date: '2026-01-30',
        version: '21.6',
        title: 'fix: Remove all remaining duplicate Flask route functions',
        changes: [
            'fix: Remove all remaining duplicate Flask route functions',
        ]
    },
    {
        date: '2026-01-30',
        version: '21.5',
        title: 'fix: Remove duplicate function definitions causing Flask route conflicts',
        changes: [
            'fix: Remove duplicate function definitions causing Flask route conflicts',
        ]
    },
    {
        date: '2026-01-30',
        version: '21.4',
        title: 'fix: CBT tools dashboard backend and AI memory integration',
        changes: [
            'fix: CBT tools dashboard backend and AI memory integration',
        ]
    },
    {
        date: '2026-01-30',
        version: '21.3',
        title: 'Fix: syntax error in POSITIVE_AFFIRMATIONS array, CBT tools dashboard and per...',
        changes: [
            'Fix: syntax error in POSITIVE_AFFIRMATIONS array, CBT tools dashboard and persistence, ensure AI listens to all tools',
        ]
    },
    {
        date: '2026-01-30',
        version: '21.2',
        title: 'New CBT tools added',
        changes: [
            'New CBT tools added',
        ]
    },
    {
        date: '2026-01-30',
        version: '21.1',
        title: 'fix: Daily Tasks Errors',
        changes: [
            'fix: Daily Tasks Errors',
        ]
    },
    {
        date: '2026-01-30',
        version: '21.0',
        title: 'Version History Update v1',
        changes: [
            'Version History Update v1.1',
        ]
    },
    {
        date: '2026-01-30',
        version: '20.9',
        title: 'Version History Update',
        changes: [
            'Version History Update',
        ]
    },
    {
        date: '2026-01-30',
        version: '20.8',
        title: 'Home Page Bug Fix 1',
        changes: [
            'Home Page Bug Fix 1.0',
        ]
    },
    {
        date: '2026-01-30',
        version: '20.7',
        title: 'fix: add detailed error logging and improved error display for mood and grati...',
        changes: [
            'fix: add detailed error logging and improved error display for mood and gratitude logging',
        ]
    },
    {
        date: '2026-01-30',
        version: '20.6',
        title: 'feat: Home tab, daily tasks, feedback, and polish for Healing Space UK',
        changes: [
            'feat: Home tab, daily tasks, feedback, and polish for Healing Space UK',
        ]
    },
    {
        date: '2026-01-30',
        version: '20.5',
        title: 'Fix comprehensive dark mode for chat, safety, insights, appointments, and abo...',
        changes: [
            'Fix comprehensive dark mode for chat, safety, insights, appointments, and about me tabs',
        ]
    },
    {
        date: '2026-01-30',
        version: '20.4',
        title: 'Fix dark mode backgrounds for all tabs and dashboard cards',
        changes: [
            'Fix dark mode backgrounds for all tabs and dashboard cards',
        ]
    },
    {
        date: '2026-01-30',
        version: '20.3',
        title: 'Update app header branding to Healing Space UK in web UI',
        changes: [
            'Update app header branding to Healing Space UK in web UI',
        ]
    },
    {
        date: '2026-01-30',
        version: '20.2',
        title: 'Update web UI branding to Healing Space UK',
        changes: [
            'Update web UI branding to Healing Space UK',
        ]
    },
    {
        date: '2026-01-30',
        version: '20.1',
        title: 'Update all branding to Healing Space UK',
        changes: [
            'Update all branding to Healing Space UK',
        ]
    },
    {
        date: '2026-01-30',
        version: '20.0',
        title: 'docs update',
        changes: [
            'docs update',
        ]
    },
    {
        date: '2026-01-30',
        version: '19.9',
        title: 'Fix dark/light theme for all tabs and cards',
        changes: [
            'Fix dark/light theme for all tabs and cards',
        ]
    },
    {
        date: '2026-01-30',
        version: '19.8',
        title: 'Crash bug fix FlaskApp location incorrect',
        changes: [
            'Crash bug fix FlaskApp location incorrect',
        ]
    },
    {
        date: '2026-01-30',
        version: '19.7',
        title: 'UI FIX',
        changes: [
            'UI FIX',
        ]
    },
    {
        date: '2026-01-30',
        version: '19.6',
        title: 'Add full CRUD endpoints, audit logging, and AI memory integration for all new...',
        changes: [
            'Add full CRUD endpoints, audit logging, and AI memory integration for all new CBT tools (breathing, relaxation, sleep, core belief, exposure, problem-solving, coping cards, self-compassion, values, goals)',
        ]
    },
    {
        date: '2026-01-30',
        version: '19.5',
        title: 'feat: Add site-wide dark mode with toggle in Settings',
        changes: [
            'feat: Add site-wide dark mode with toggle in Settings',
        ]
    },
    {
        date: '2026-01-30',
        version: '19.4',
        title: 'feat: Discord-style community with channels, threads, and pinned posts',
        changes: [
            'feat: Discord-style community with channels, threads, and pinned posts',
        ]
    },
    {
        date: '2026-01-30',
        version: '19.3',
        title: 'version_history_update',
        changes: [
            'version_history_update',
        ]
    },
    {
        date: '2026-01-30',
        version: '19.2',
        title: 'feat: Add category system, inline replies, and auto-refresh to community',
        changes: [
            'feat: Add category system, inline replies, and auto-refresh to community',
        ]
    },
    {
        date: '2026-01-30',
        version: '19.1',
        title: 'feat: add reply deletion and multiple reaction emojis',
        changes: [
            'feat: add reply deletion and multiple reaction emojis',
        ]
    },
    {
        date: '2026-01-30',
        version: '19.0',
        title: 'fix: add missing flagged/flag_reason to ContentModerator',
        changes: [
            'fix: add missing flagged/flag_reason to ContentModerator',
        ]
    },
    {
        date: '2026-01-30',
        version: '18.9',
        title: 'fix: pet database persistence and content moderator',
        changes: [
            'fix: pet database persistence and content moderator',
        ]
    },
    {
        date: '2026-01-30',
        version: '18.8',
        title: 'fix:PT3 ensure pet table exists before all pet DB access (robust pet features...',
        changes: [
            'fix:PT3 ensure pet table exists before all pet DB access (robust pet features after Railway reset)',
        ]
    },
    {
        date: '2026-01-30',
        version: '18.7',
        title: 'fix:PT2 ensure pet table exists before all pet DB access (robust pet features...',
        changes: [
            'fix:PT2 ensure pet table exists before all pet DB access (robust pet features after Railway reset)',
        ]
    },
    {
        date: '2026-01-29',
        version: '18.6',
        title: 'fix: ensure pet table exists before all pet DB access (robust pet features af...',
        changes: [
            'fix: ensure pet table exists before all pet DB access (robust pet features after Railway reset)',
        ]
    },
    {
        date: '2026-01-29',
        version: '18.5',
        title: 'Update audit',
        changes: [
            'Update audit.md - Phase 6 complete (88% resolution rate)',
        ]
    },
    {
        date: '2026-01-29',
        version: '18.4',
        title: 'Phase 6: Fix Medium (P2) security and code quality issues',
        changes: [
            'Phase 6: Fix Medium (P2) security and code quality issues',
        ]
    },
    {
        date: '2026-01-29',
        version: '18.3',
        title: 'Phase 6: Fix all Critical (P0) and High (P1) security issues',
        changes: [
            'Phase 6: Fix all Critical (P0) and High (P1) security issues',
        ]
    },
    {
        date: '2026-01-29',
        version: '18.2',
        title: 'Phase 6: Fresh security audit - 16 new issues identified',
        changes: [
            'Phase 6: Fresh security audit - 16 new issues identified',
        ]
    },
    {
        date: '2026-01-29',
        version: '18.1',
        title: 'Merge remote changes and resolve VERSION_HISTORY conflict',
        changes: [
            'Merge remote changes and resolve VERSION_HISTORY conflict',
        ]
    },
    {
        date: '2026-01-29',
        version: '18.0',
        title: 'Fix: AI summary endpoint - remove non-existent created_at column from users q...',
        changes: [
            'Fix: AI summary endpoint - remove non-existent created_at column from users query',
        ]
    },
    {
        date: '2026-01-29',
        version: '17.9',
        title: 'Phase 5: Web/Android audit - Fix pet endpoints, duplicate routes, exception l...',
        changes: [
            'Phase 5: Web/Android audit - Fix pet endpoints, duplicate routes, exception leaks',
        ]
    },
    {
        date: '2026-01-29',
        version: '17.8',
        title: 'Phase 5: Web/Android audit - Fix pet endpoints, duplicate routes, exception l...',
        changes: [
            'Phase 5: Web/Android audit - Fix pet endpoints, duplicate routes, exception leaks',
        ]
    },
    {
        date: '2026-01-29',
        version: '17.7',
        title: 'fix: Harden /api/professional/ai-summary endpoint (null checks, safe defaults...',
        changes: [
            'fix: Harden /api/professional/ai-summary endpoint (null checks, safe defaults, debug logging, robust fallback)',
        ]
    },
    {
        date: '2026-01-29',
        version: '17.6',
        title: 'Fix: Add None checks to AI summary prompt string slicing',
        changes: [
            'Fix: Add None checks to AI summary prompt string slicing',
        ]
    },
    {
        date: '2026-01-29',
        version: '17.5',
        title: 'fix: Set Updates tab as default for changelog debug (shows changelog on load)',
        changes: [
            'fix: Set Updates tab as default for changelog debug (shows changelog on load)',
        ]
    },
    {
        date: '2026-01-29',
        version: '17.4',
        title: 'Add null safety and error logging to AI summary endpoint',
        changes: [
            'Add null safety and error logging to AI summary endpoint',
        ]
    },
    {
        date: '2026-01-29',
        version: '17.3',
        title: 'Enhance AI clinical summary and fix patient charts',
        changes: [
            'Enhance AI clinical summary and fix patient charts',
        ]
    },
    {
        date: '2026-01-29',
        version: '17.2',
        title: 'Fix: Add missing clinician parameter to patient detail endpoint',
        changes: [
            'Fix: Add missing clinician parameter to patient detail endpoint',
        ]
    },
    {
        date: '2026-01-29',
        version: '17.1',
        title: 'Update VERSION_HISTORY',
        changes: [
            'Update VERSION_HISTORY.txt with today\'s fixes',
        ]
    },
    {
        date: '2026-01-29',
        version: '17.0',
        title: 'Fix: Clinician dashboard patient data and AI insights',
        changes: [
            'Fix: Clinician dashboard patient data and AI insights',
        ]
    },
    {
        date: '2026-01-29',
        version: '16.9',
        title: 'Update VERSION_HISTORY',
        changes: [
            'Update VERSION_HISTORY.txt with recent commits',
        ]
    },
    {
        date: '2026-01-29',
        version: '16.8',
        title: 'Fix: loadInsights sends role=clinician for clinician users (enables clinician...',
        changes: [
            'Fix: loadInsights sends role=clinician for clinician users (enables clinician data/AI insights)',
        ]
    },
    {
        date: '2026-01-29',
        version: '16.7',
        title: 'Fix: /api/insights always returns avg_mood, avg_sleep, and trend (prevents fr...',
        changes: [
            'Fix: /api/insights always returns avg_mood, avg_sleep, and trend (prevents frontend errors on empty data)',
        ]
    },
    {
        date: '2026-01-29',
        version: '16.6',
        title: 'Fix: remove syntax error in /api/pet/status endpoint (no nested try)',
        changes: [
            'Fix: remove syntax error in /api/pet/status endpoint (no nested try)',
        ]
    },
    {
        date: '2026-01-29',
        version: '16.5',
        title: 'Chore: trigger Railway deploy (trivial comment change)',
        changes: [
            'Chore: trigger Railway deploy (trivial comment change)',
        ]
    },
    {
        date: '2026-01-29',
        version: '16.4',
        title: 'Fix: Insights always sends prompt, pet endpoints handle missing user/pet, fro...',
        changes: [
            'Fix: Insights always sends prompt, pet endpoints handle missing user/pet, frontend sends username for pet reward',
        ]
    },
    {
        date: '2026-01-29',
        version: '16.3',
        title: 'UI: Add show/hide toggle for PIN fields on all login forms',
        changes: [
            'UI: Add show/hide toggle for PIN fields on all login forms',
        ]
    },
    {
        date: '2026-01-29',
        version: '16.2',
        title: 'Frontend: always use credentials: include in fetch for CSRF/session reliability',
        changes: [
            'Frontend: always use credentials: include in fetch for CSRF/session reliability',
        ]
    },
    {
        date: '2026-01-29',
        version: '16.1',
        title: 'Fix CSRF token endpoint: resolve secrets shadowing, use stdlib secrets for to...',
        changes: [
            'Fix CSRF token endpoint: resolve secrets shadowing, use stdlib secrets for token generation, ensure session cookie set',
        ]
    },
    {
        date: '2026-01-29',
        version: '16.0',
        title: 'Add Phase 4 UX enhancements: onboarding, accessibility, mobile',
        changes: [
            'Add Phase 4 UX enhancements: onboarding, accessibility, mobile',
        ]
    },
    {
        date: '2026-01-29',
        version: '15.9',
        title: 'Set up venv, install all dependencies, playwright, and fixed test environment',
        changes: [
            'Set up venv, install all dependencies, playwright, and fixed test environment. Ready for further dev and testing.',
        ]
    },
    {
        date: '2026-01-28',
        version: '15.8',
        title: 'Fix TherapistAI indentation error (production boot fix)',
        changes: [
            'Fix TherapistAI indentation error (production boot fix)',
        ]
    },
    {
        date: '2026-01-28',
        version: '15.7',
        title: 'Add get_insight method to TherapistAI for insights endpoint compatibility',
        changes: [
            'Add get_insight method to TherapistAI for insights endpoint compatibility',
        ]
    },
    {
        date: '2026-01-28',
        version: '15.6',
        title: 'Refactor insights endpoint: custom date range, AI prompt, clinician/patient n...',
        changes: [
            'Refactor insights endpoint: custom date range, AI prompt, clinician/patient narrative',
        ]
    },
    {
        date: '2026-01-28',
        version: '15.5',
        title: 'Updated AUDIT',
        changes: [
            'Updated AUDIT.md with dynamic audit results',
        ]
    },
    {
        date: '2026-01-28',
        version: '15.4',
        title: 'Rollback: restore project to v1',
        changes: [
            'Rollback: restore project to v1.0.46 (2026-01-26) - Fix chat input layout for mobile',
        ]
    },
    {
        date: '2026-01-26',
        version: '15.3',
        title: 'Fix chat input layout for mobile - stack textarea above buttons',
        changes: [
            'Fix chat input layout for mobile - stack textarea above buttons',
        ]
    },
    {
        date: '2026-01-26',
        version: '15.2',
        title: 'Add Updates tab, notification management, and chat improvements',
        changes: [
            'Add Updates tab, notification management, and chat improvements',
        ]
    },
    {
        date: '2026-01-26',
        version: '15.1',
        title: 'Improve AI chat: voice input, thinking animation, natural responses',
        changes: [
            'Improve AI chat: voice input, thinking animation, natural responses',
        ]
    },
    {
        date: '2026-01-25',
        version: '15.0',
        title: 'message bugs update',
        changes: [
            'message bugs update',
        ]
    },
    {
        date: '2026-01-25',
        version: '14.9',
        title: 'API update',
        changes: [
            'API update',
        ]
    },
    {
        date: '2026-01-25',
        version: '14.8',
        title: 'Remove package',
        changes: [
            'Remove package.json to fix Railway Python deploy (prevent npm ci)',
        ]
    },
    {
        date: '2026-01-25',
        version: '14.7',
        title: 'Fix Railway deploy: allow pip install in Nixpacks immutable env',
        changes: [
            'Fix Railway deploy: allow pip install in Nixpacks immutable env',
        ]
    },
    {
        date: '2026-01-25',
        version: '14.6',
        title: 'Add nixpacks',
        changes: [
            'Add nixpacks.toml to force Python dependency install on Railway',
        ]
    },
    {
        date: '2026-01-25',
        version: '14.5',
        title: 'Add mobile app (Capacitor) and deployment documentation',
        changes: [
            'Add mobile app (Capacitor) and deployment documentation',
        ]
    },
    {
        date: '2026-01-24',
        version: '14.4',
        title: 'Major update: Fix database concurrency, user deletion, and messaging system',
        changes: [
            'Major update: Fix database concurrency, user deletion, and messaging system',
        ]
    },
    {
        date: '2026-01-24',
        version: '14.3',
        title: 'Add developer dashboard',
        changes: [
            'Add developer dashboard',
        ]
    },
    {
        date: '2026-01-23',
        version: '14.2',
        title: 'Add developer dashboard',
        changes: [
            'Add developer dashboard',
        ]
    },
    {
        date: '2026-01-25',
        version: '14.1',
        title: 'Add api',
        changes: [
            'Add api.py deep-audit and update roadmap with endpoint mapping and migration plan',
        ]
    },
    {
        date: '2026-01-25',
        version: '14.0',
        title: 'Update ROADMAP',
        changes: [
            'Update ROADMAP.md with detailed file-by-file audit and next steps (2026-01-25)',
        ]
    },
    {
        date: '2026-01-25',
        version: '13.9',
        title: 'Add roadmap and index for mobile app development',
        changes: [
            'Add roadmap and index for mobile app development',
        ]
    },
    {
        date: '2026-01-24',
        version: '13.8',
        title: 'docs: add Additional Features & Roadmap under future updates and ideas (2026-...',
        changes: [
            'docs: add Additional Features & Roadmap under future updates and ideas (2026-01-24)',
        ]
    },
    {
        date: '2026-01-24',
        version: '13.7',
        title: 'docs: update repository README and documentation index to reflect current fea...',
        changes: [
            'docs: update repository README and documentation index to reflect current features and usage (2026-01-24)',
        ]
    },
    {
        date: '2026-01-22',
        version: '13.6',
        title: 'legal: add role-specific disclaimers with comprehensive UK legal protection',
        changes: [
            'legal: add role-specific disclaimers with comprehensive UK legal protection',
        ]
    },
    {
        date: '2026-01-22',
        version: '13.5',
        title: 'docs: strengthen pitch—emphasize AI bridging gap between sessions and patient...',
        changes: [
            'docs: strengthen pitch—emphasize AI bridging gap between sessions and patient continuity',
        ]
    },
    {
        date: '2026-01-22',
        version: '13.4',
        title: 'docs: make clinician/patient guides website-only (remove developer instructions)',
        changes: [
            'docs: make clinician/patient guides website-only (remove developer instructions)',
        ]
    },
    {
        date: '2026-01-22',
        version: '13.3',
        title: 'docs: add non-technical web access guide and surface it in clinician/patient ...',
        changes: [
            'docs: add non-technical web access guide and surface it in clinician/patient guides',
        ]
    },
    {
        date: '2026-01-22',
        version: '13.2',
        title: 'ci: stabilize workflow, disable pytest plugin autoload, set test env vars',
        changes: [
            'ci: stabilize workflow, disable pytest plugin autoload, set test env vars',
        ]
    },
    {
        date: '2026-01-22',
        version: '13.1',
        title: 'chore: timezone-aware datetimes; optional browser smoke test + CI step',
        changes: [
            'chore: timezone-aware datetimes; optional browser smoke test + CI step',
        ]
    },
    {
        date: '2026-01-22',
        version: '13.0',
        title: 'fix: robust FHIR export handling; add integration chat+FHIR tests; add CI wor...',
        changes: [
            'fix: robust FHIR export handling; add integration chat+FHIR tests; add CI workflow',
        ]
    },
    {
        date: '2026-01-22',
        version: '12.9',
        title: 'chore: normalize timestamp queries, fix analytics; tests passing',
        changes: [
            'chore: normalize timestamp queries, fix analytics; tests passing',
        ]
    },
    {
        date: '2026-01-22',
        version: '12.8',
        title: 'fix(clinician): show appointments in patient dashboard; add attendance controls',
        changes: [
            'fix(clinician): show appointments in patient dashboard; add attendance controls',
        ]
    },
    {
        date: '2026-01-22',
        version: '12.7',
        title: 'feat: appointment attendance, notification fixes, deploy automation',
        changes: [
            'feat: appointment attendance, notification fixes, deploy automation',
        ]
    },
    {
        date: '2026-01-19',
        version: '12.6',
        title: 'Expand pet game: mini-games, mood, journal, daily challenges, healthy habit r...',
        changes: [
            'Expand pet game: mini-games, mood, journal, daily challenges, healthy habit rewards, and bugfixes. All tests passing.',
        ]
    },
    {
        date: '2026-01-19',
        version: '12.5',
        title: 'Fix patient analytics mood query: use entrestamp/mood_val instead of timestam...',
        changes: [
            'Fix patient analytics mood query: use entrestamp/mood_val instead of timestamp/mood_score',
        ]
    },
    {
        date: '2026-01-19',
        version: '12.4',
        title: 'Remove Analytics tab, redesign Appointments with calendar views (month/week/d...',
        changes: [
            'Remove Analytics tab, redesign Appointments with calendar views (month/week/day) for scalability',
        ]
    },
    {
        date: '2026-01-19',
        version: '12.3',
        title: 'Fix active patient tracking: update last_login on login, add clickable active...',
        changes: [
            'Fix active patient tracking: update last_login on login, add clickable active count with details modal',
        ]
    },
    {
        date: '2026-01-19',
        version: '12.2',
        title: 'Fix clinical_scales column names (scale_name/score not scale_type/total_score)',
        changes: [
            'Fix clinical_scales column names (scale_name/score not scale_type/total_score)',
        ]
    },
    {
        date: '2026-01-19',
        version: '12.1',
        title: 'Add analytics debug endpoint and refresh button',
        changes: [
            'Add analytics debug endpoint and refresh button',
        ]
    },
    {
        date: '2026-01-19',
        version: '12.0',
        title: 'Add documentation for Railway database wipe',
        changes: [
            'Add documentation for Railway database wipe',
        ]
    },
    {
        date: '2026-01-19',
        version: '11.9',
        title: 'Add admin database wipe endpoint and web interface for Railway',
        changes: [
            'Add admin database wipe endpoint and web interface for Railway',
        ]
    },
    {
        date: '2026-01-19',
        version: '11.8',
        title: 'Add detailed logging to auth endpoints and update version to v2026',
        changes: [
            'Add detailed logging to auth endpoints and update version to v2026.01.19.5',
        ]
    },
    {
        date: '2026-01-19',
        version: '11.7',
        title: 'Fix password reset email error handling - make SMTP failures graceful',
        changes: [
            'Fix password reset email error handling - make SMTP failures graceful',
        ]
    },
    {
        date: '2026-01-19',
        version: '11.6',
        title: 'Add 2FA verification system for signup with email and SMS support',
        changes: [
            'Add 2FA verification system for signup with email and SMS support',
        ]
    },
    {
        date: '2026-01-19',
        version: '11.5',
        title: 'database wipe 3',
        changes: [
            'database wipe 3.3.5',
        ]
    },
    {
        date: '2026-01-19',
        version: '11.4',
        title: 'Fix alerts query to use status column and add DOM render delay for analytics ...',
        changes: [
            'Fix alerts query to use status column and add DOM render delay for analytics load',
        ]
    },
    {
        date: '2026-01-19',
        version: '11.3',
        title: 'Add comprehensive logging for analytics dashboard and auto-load on clinician ...',
        changes: [
            'Add comprehensive logging for analytics dashboard and auto-load on clinician login',
        ]
    },
    {
        date: '2026-01-19',
        version: '11.2',
        title: 'Add migration for chat_session_id column and improve chat session creation er...',
        changes: [
            'Add migration for chat_session_id column and improve chat session creation error handling',
        ]
    },
    {
        date: '2026-01-19',
        version: '11.1',
        title: 'Add comprehensive error handling to AI chat endpoint - better debugging and c...',
        changes: [
            'Add comprehensive error handling to AI chat endpoint - better debugging and clearer error messages',
        ]
    },
    {
        date: '2026-01-19',
        version: '11.0',
        title: 'Fix analytics display handling null values, add patient notification when app...',
        changes: [
            'Fix analytics display handling null values, add patient notification when appointment cancelled, therapy notes already timestamped',
        ]
    },
    {
        date: '2026-01-19',
        version: '10.9',
        title: 'Restructure clinician dashboard: Overview shows only 3 stat cards, charts mov...',
        changes: [
            'Restructure clinician dashboard: Overview shows only 3 stat cards, charts moved to Analytics tab',
        ]
    },
    {
        date: '2026-01-19',
        version: '10.8',
        title: 'Fix analytics dashboard patient counting queries',
        changes: [
            'Fix analytics dashboard patient counting queries',
        ]
    },
    {
        date: '2026-01-19',
        version: '10.7',
        title: 'Add organized subtabs for patient detail view',
        changes: [
            'Add organized subtabs for patient detail view',
        ]
    },
    {
        date: '2026-01-19',
        version: '10.6',
        title: 'Reorganize clinician dashboard with organized subtabs',
        changes: [
            'Reorganize clinician dashboard with organized subtabs',
        ]
    },
    {
        date: '2026-01-19',
        version: '10.5',
        title: 'DB quick update',
        changes: [
            'DB quick update',
        ]
    },
    {
        date: '2026-01-19',
        version: '10.4',
        title: 'Fix login error handling and appointment display issues',
        changes: [
            'Fix login error handling and appointment display issues',
        ]
    },
    {
        date: '2026-01-19',
        version: '10.3',
        title: 'Add clinician analytics dashboard, report generator, and patient search features',
        changes: [
            'Add clinician analytics dashboard, report generator, and patient search features',
        ]
    },
    {
        date: '2026-01-19',
        version: '10.2',
        title: 'docs: Add comprehensive Android app conversion guide',
        changes: [
            'docs: Add comprehensive Android app conversion guide',
        ]
    },
    {
        date: '2026-01-18',
        version: '10.1',
        title: 'fix: Load appointments automatically when clinician logs in',
        changes: [
            'fix: Load appointments automatically when clinician logs in',
        ]
    },
    {
        date: '2026-01-18',
        version: '10.0',
        title: 'fix: Force refresh of appointments list by disabling browser cache',
        changes: [
            'fix: Force refresh of appointments list by disabling browser cache',
        ]
    },
    {
        date: '2026-01-18',
        version: '9.9',
        title: 'fix: Organize clinician appointments into clear sections',
        changes: [
            'fix: Organize clinician appointments into clear sections',
        ]
    },
    {
        date: '2026-01-18',
        version: '9.8',
        title: 'fix: Add patient notifications for appointments and improve clinician respons...',
        changes: [
            'fix: Add patient notifications for appointments and improve clinician response visibility',
        ]
    },
    {
        date: '2026-01-18',
        version: '9.7',
        title: 'feat: Auto-training on Railway + local dev setup',
        changes: [
            'feat: Auto-training on Railway + local dev setup',
        ]
    },
    {
        date: '2026-01-18',
        version: '9.6',
        title: 'feat: Background AI training system for independent learning',
        changes: [
            'feat: Background AI training system for independent learning',
        ]
    },
    {
        date: '2026-01-18',
        version: '9.5',
        title: 'feat: Multiple chat sessions with full clinician/ML access',
        changes: [
            'feat: Multiple chat sessions with full clinician/ML access',
        ]
    },
    {
        date: '2026-01-18',
        version: '9.4',
        title: 'feat: Add chat search, timestamps, and export with date range',
        changes: [
            'feat: Add chat search, timestamps, and export with date range',
        ]
    },
    {
        date: '2026-01-18',
        version: '9.3',
        title: 'docs: Add comprehensive web app validation report',
        changes: [
            'docs: Add comprehensive web app validation report',
        ]
    },
    {
        date: '2026-01-18',
        version: '9.2',
        title: 'Add diagnostic page for testing JavaScript loading',
        changes: [
            'Add diagnostic page for testing JavaScript loading',
        ]
    },
    {
        date: '2026-01-18',
        version: '9.1',
        title: 'CRITICAL FIX: Remove broken text breaking entire JavaScript execution',
        changes: [
            'CRITICAL FIX: Remove broken text breaking entire JavaScript execution',
        ]
    },
    {
        date: '2026-01-18',
        version: '9.0',
        title: 'Fix: Remove duplicate checkPetReturn function causing syntax error',
        changes: [
            'Fix: Remove duplicate checkPetReturn function causing syntax error',
        ]
    },
    {
        date: '2026-01-18',
        version: '8.9',
        title: 'Fix: Remove orphaned duplicate code causing login function to not load',
        changes: [
            'Fix: Remove orphaned duplicate code causing login function to not load',
        ]
    },
    {
        date: '2026-01-18',
        version: '8.8',
        title: 'fix: update node version in Dockerfile',
        changes: [
            'fix: update node version in Dockerfile',
        ]
    },
    {
        date: '2026-01-18',
        version: '8.7',
        title: 'login issues v1',
        changes: [
            'login issues v1.8',
        ]
    },
    {
        date: '2026-01-18',
        version: '8.6',
        title: 'docs: update copilot instructions for web API',
        changes: [
            'docs: update copilot instructions for web API',
        ]
    },
    {
        date: '2026-01-18',
        version: '8.5',
        title: 'landing page issue',
        changes: [
            'landing page issue',
        ]
    },
    {
        date: '2026-01-17',
        version: '8.4',
        title: 'feat: Add model training script and fix auth flow',
        changes: [
            'feat: Add model training script and fix auth flow',
        ]
    },
    {
        date: '2026-01-17',
        version: '8.3',
        title: '1',
        changes: [
            '1.1',
        ]
    },
    {
        date: '2026-01-17',
        version: '8.2',
        title: 'login flow bug fix',
        changes: [
            'login flow bug fix',
        ]
    },
    {
        date: '2026-01-17',
        version: '8.1',
        title: 'index missed fix',
        changes: [
            'index missed fix',
        ]
    },
    {
        date: '2026-01-17',
        version: '8.0',
        title: 'Menu Bug Fix',
        changes: [
            'Menu Bug Fix',
        ]
    },
    {
        date: '2026-01-17',
        version: '7.9',
        title: 'Fix: Remove duplicate walkCountdownInterval declarations causing syntax error',
        changes: [
            'Fix: Remove duplicate walkCountdownInterval declarations causing syntax error',
        ]
    },
    {
        date: '2026-01-17',
        version: '7.8',
        title: 'Add version tracking and debug logs for auth functions',
        changes: [
            'Add version tracking and debug logs for auth functions',
        ]
    },
    {
        date: '2026-01-17',
        version: '7.7',
        title: 'Add cache-busting meta tags to fix showClinicianAuth function not loading',
        changes: [
            'Add cache-busting meta tags to fix showClinicianAuth function not loading',
        ]
    },
    {
        date: '2026-01-17',
        version: '7.6',
        title: 'Fix pet game: increase modal z-index, add 30min walk cooldown with countdown ...',
        changes: [
            'Fix pet game: increase modal z-index, add 30min walk cooldown with countdown timer, show rewards',
        ]
    },
    {
        date: '2026-01-17',
        version: '7.5',
        title: 'Fix: Show appointments from last 30 days in clinician view (prevent disappear...',
        changes: [
            'Fix: Show appointments from last 30 days in clinician view (prevent disappearing after patient response)',
        ]
    },
    {
        date: '2026-01-17',
        version: '7.4',
        title: 'Add bidirectional appointments system with patient acknowledgment and respons...',
        changes: [
            'Add bidirectional appointments system with patient acknowledgment and response tracking',
        ]
    },
    {
        date: '2026-01-17',
        version: '7.3',
        title: 'Fix export errors and enhance signup forms',
        changes: [
            'Fix export errors and enhance signup forms',
        ]
    },
    {
        date: '2026-01-17',
        version: '7.2',
        title: 'Documentation: Add sleep chart feature documentation',
        changes: [
            'Documentation: Add sleep chart feature documentation',
        ]
    },
    {
        date: '2026-01-17',
        version: '7.1',
        title: 'Feature: Add sleep chart and custom date ranges to insights',
        changes: [
            'Feature: Add sleep chart and custom date ranges to insights',
        ]
    },
    {
        date: '2026-01-17',
        version: '7.0',
        title: 'Fix: Insights API column name mismatch',
        changes: [
            'Fix: Insights API column name mismatch',
        ]
    },
    {
        date: '2026-01-17',
        version: '6.9',
        title: 'Complete audit: All features verified and documented',
        changes: [
            'Complete audit: All features verified and documented',
        ]
    },
    {
        date: '2026-01-17',
        version: '6.8',
        title: 'Add appointment calendar system to web interface',
        changes: [
            'Add appointment calendar system to web interface',
        ]
    },
    {
        date: '2026-01-17',
        version: '6.7',
        title: 'Add show/hide password toggle to login screens',
        changes: [
            'Add show/hide password toggle to login screens',
        ]
    },
    {
        date: '2026-01-17',
        version: '6.6',
        title: 'Fix: Separate desktop and web code, fix tkinter import errors',
        changes: [
            'Fix: Separate desktop and web code, fix tkinter import errors',
        ]
    },
    {
        date: '2026-01-17',
        version: '6.5',
        title: 'Fix: Add About Me page, fix PDF/CSV exports with reportlab',
        changes: [
            'Fix: Add About Me page, fix PDF/CSV exports with reportlab',
        ]
    },
    {
        date: '2026-01-17',
        version: '6.4',
        title: 'Add API endpoints for appointments and patient profile',
        changes: [
            'Add API endpoints for appointments and patient profile',
        ]
    },
    {
        date: '2026-01-17',
        version: '6.3',
        title: 'Deploy to Railway - 2026-01-17 17:48:01',
        changes: [
            'Deploy to Railway - 2026-01-17 17:48:01',
        ]
    },
    {
        date: '2026-01-17',
        version: '6.2',
        title: 'Add patient About Me page and personal PDF export',
        changes: [
            'Add patient About Me page and personal PDF export',
        ]
    },
    {
        date: '2026-01-17',
        version: '6.1',
        title: 'Add completion summary for appointment system',
        changes: [
            'Add completion summary for appointment system',
        ]
    },
    {
        date: '2026-01-17',
        version: '6.0',
        title: 'Add clinician appointment calendar with PDF reports and notifications',
        changes: [
            'Add clinician appointment calendar with PDF reports and notifications',
        ]
    },
    {
        date: '2026-01-17',
        version: '5.9',
        title: 'Organize all documentation in documentation/ folder with comprehensive coverage',
        changes: [
            'Organize all documentation in documentation/ folder with comprehensive coverage',
        ]
    },
    {
        date: '2026-01-17',
        version: '5.8',
        title: 'Add comprehensive user guide for patients and clinicians',
        changes: [
            'Add comprehensive user guide for patients and clinicians',
        ]
    },
    {
        date: '2026-01-17',
        version: '5.7',
        title: 'Implement pet care features and assessment limits',
        changes: [
            'Implement pet care features and assessment limits',
        ]
    },
    {
        date: '2026-01-17',
        version: '5.6',
        title: 'Fix missing time import in api',
        changes: [
            'Fix missing time import in api.py',
        ]
    },
    {
        date: '2026-01-17',
        version: '5.5',
        title: 'Trigger Railway redeploy',
        changes: [
            'Trigger Railway redeploy',
        ]
    },
    {
        date: '2026-01-16',
        version: '5.4',
        title: 'Add pet rewards for all self-care activities',
        changes: [
            'Add pet rewards for all self-care activities',
        ]
    },
    {
        date: '2026-01-16',
        version: '5.3',
        title: 'Add session persistence and Remember Me functionality',
        changes: [
            'Add session persistence and Remember Me functionality',
        ]
    },
    {
        date: '2026-01-16',
        version: '5.2',
        title: 'Complete AI memory integration and chat initialization system',
        changes: [
            'Complete AI memory integration and chat initialization system',
        ]
    },
    {
        date: '2026-01-16',
        version: '5.1',
        title: 'Require full name, DOB, and medical conditions on patient signup',
        changes: [
            'Require full name, DOB, and medical conditions on patient signup',
        ]
    },
    {
        date: '2026-01-16',
        version: '5.0',
        title: 'Fix chat history loading with correct function names and async flow',
        changes: [
            'Fix chat history loading with correct function names and async flow',
        ]
    },
    {
        date: '2026-01-16',
        version: '4.9',
        title: 'Fix AI chat, add persistent chat history, make therapy default tab, include a...',
        changes: [
            'Fix AI chat, add persistent chat history, make therapy default tab, include all patient data in clinician dashboard',
        ]
    },
    {
        date: '2026-01-16',
        version: '4.8',
        title: 'Add deployment checklist for Railway setup',
        changes: [
            'Add deployment checklist for Railway setup',
        ]
    },
    {
        date: '2026-01-16',
        version: '4.7',
        title: 'Add Railway deployment support with GitHub Actions for 8pm mood reminders',
        changes: [
            'Add Railway deployment support with GitHub Actions for 8pm mood reminders',
        ]
    },
    {
        date: '2026-01-16',
        version: '4.6',
        title: 'Complete 8pm mood reminder system with cron automation',
        changes: [
            'Complete 8pm mood reminder system with cron automation',
        ]
    },
    {
        date: '2026-01-16',
        version: '4.5',
        title: 'Add cron job setup for 8pm mood reminders',
        changes: [
            'Add cron job setup for 8pm mood reminders',
        ]
    },
    {
        date: '2026-01-16',
        version: '4.4',
        title: 'clin notes/ai tracking/dupe prevention implementattion',
        changes: [
            'clin notes/ai tracking/dupe prevention implementattion',
        ]
    },
    {
        date: '2026-01-16',
        version: '4.3',
        title: 'overhall v1',
        changes: [
            'overhall v1.45',
        ]
    },
    {
        date: '2026-01-16',
        version: '4.2',
        title: 'Add Railway volume support',
        changes: [
            'Add Railway volume support',
        ]
    },
    {
        date: '2026-01-16',
        version: '4.1',
        title: 'Patient approval udate v1',
        changes: [
            'Patient approval udate v1.1',
        ]
    },
    {
        date: '2026-01-16',
        version: '4.0',
        title: 'email/api update',
        changes: [
            'email/api update',
        ]
    },
    {
        date: '2026-01-16',
        version: '3.9',
        title: 'clin dash update',
        changes: [
            'clin dash update',
        ]
    },
    {
        date: '2026-01-16',
        version: '3.8',
        title: 'Add implementation summary for email/phone and password reset features',
        changes: [
            'Add implementation summary for email/phone and password reset features',
        ]
    },
    {
        date: '2026-01-16',
        version: '3.7',
        title: 'Add email/phone to signup, forgot password/PIN functionality with email reset...',
        changes: [
            'Add email/phone to signup, forgot password/PIN functionality with email reset, and PostgreSQL setup guide',
        ]
    },
    {
        date: '2026-01-16',
        version: '3.6',
        title: 'Fix pending approvals not showing - correct property name from approvals to p...',
        changes: [
            'Fix pending approvals not showing - correct property name from approvals to pending_approvals',
        ]
    },
    {
        date: '2026-01-16',
        version: '3.5',
        title: 'Fix JavaScript syntax error - incorrect quote escaping in startAdventure func...',
        changes: [
            'Fix JavaScript syntax error - incorrect quote escaping in startAdventure function',
        ]
    },
    {
        date: '2026-01-16',
        version: '3.4',
        title: 'Add explicit pointer-events: auto and console logging to debug landing page b...',
        changes: [
            'Add explicit pointer-events: auto and console logging to debug landing page button clicks',
        ]
    },
    {
        date: '2026-01-16',
        version: '3.3',
        title: 'Fix landing page buttons - remove stacking context from app-container and add...',
        changes: [
            'Fix landing page buttons - remove stacking context from app-container and add explicit z-index to buttons',
        ]
    },
    {
        date: '2026-01-16',
        version: '3.2',
        title: 'Move disclaimer to registration flow - shows after user selects patient/clini...',
        changes: [
            'Move disclaimer to registration flow - shows after user selects patient/clinician during signup only',
        ]
    },
    {
        date: '2026-01-16',
        version: '3.1',
        title: 'Fix landing page button clicks - add z-index to auth-box',
        changes: [
            'Fix landing page button clicks - add z-index to auth-box',
        ]
    },
    {
        date: '2026-01-16',
        version: '3.0',
        title: 'Fix login after disclaimer acceptance - use stored auth data instead of re-au...',
        changes: [
            'Fix login after disclaimer acceptance - use stored auth data instead of re-authenticating',
        ]
    },
    {
        date: '2026-01-16',
        version: '2.9',
        title: 'Fix z-index issue on landing page - auth screen now properly overlays app',
        changes: [
            'Fix z-index issue on landing page - auth screen now properly overlays app',
        ]
    },
    {
        date: '2026-01-16',
        version: '2.8',
        title: 'Complete pet game implementation with shop, declutter, adventure, time decay ...',
        changes: [
            'Complete pet game implementation with shop, declutter, adventure, time decay + move menu to left sidebar',
        ]
    },
    {
        date: '2026-01-14',
        version: '2.7',
        title: 'database reset',
        changes: [
            'database reset',
        ]
    },
    {
        date: '2026-01-14',
        version: '2.6',
        title: 'Add developer README PDF and database reset endpoint for testing',
        changes: [
            'Add developer README PDF and database reset endpoint for testing',
        ]
    },
    {
        date: '2026-01-14',
        version: '2.5',
        title: 'Dev Files Update (v1',
        changes: [
            'Dev Files Update (v1.0.1)',
        ]
    },
    {
        date: '2026-01-14',
        version: '2.4',
        title: 'Fix missing clinician_id column and add password special character requiremen...',
        changes: [
            'Fix missing clinician_id column and add password special character requirement for both patient and clinician registration',
        ]
    },
    {
        date: '2026-01-14',
        version: '2.3',
        title: 'Add legal disclaimer, landing page for clinician/patient separation, and PIN ...',
        changes: [
            'Add legal disclaimer, landing page for clinician/patient separation, and PIN requirement for clinician registration',
        ]
    },
    {
        date: '2026-01-14',
        version: '2.2',
        title: 'Add comprehensive documentation for new features',
        changes: [
            'Add comprehensive documentation for new features',
        ]
    },
    {
        date: '2026-01-14',
        version: '2.1',
        title: 'Add 2FA PIN authentication, password strength validation, patient approval wo...',
        changes: [
            'Add 2FA PIN authentication, password strength validation, patient approval workflow, and notification system',
        ]
    },
    {
        date: '2026-01-14',
        version: '2.0',
        title: 'Implement professional clinician system: clinician registration, patient-clin...',
        changes: [
            'Implement professional clinician system: clinician registration, patient-clinician linking, role-based dashboard access, clinician filtering',
        ]
    },
    {
        date: '2026-01-14',
        version: '1.9',
        title: 'Add ALL missing features: Community Board, Safety Plan, Progress Insights wit...',
        changes: [
            'Add ALL missing features: Community Board, Safety Plan, Progress Insights with charts, CSV/PDF export, Sleep Hygiene, Professional Dashboard - complete feature parity with desktop app',
        ]
    },
    {
        date: '2026-01-14',
        version: '1.8',
        title: 'Complete feature implementation: all original app functionality now in web ve...',
        changes: [
            'Complete feature implementation: all original app functionality now in web version',
        ]
    },
    {
        date: '2026-01-14',
        version: '1.7',
        title: 'database update',
        changes: [
            'database update',
        ]
    },
    {
        date: '2026-01-12',
        version: '1.6',
        title: 'Fix registration error: remove main',
        changes: [
            'Fix registration error: remove main. prefix from hash functions',
        ]
    },
    {
        date: '2026-01-12',
        version: '1.5',
        title: 'push for web app',
        changes: [
            'push for web app',
        ]
    },
    {
        date: '2026-01-12',
        version: '1.4',
        title: 'Fix syntax error in api',
        changes: [
            'Fix syntax error in api.py hash_pin function',
        ]
    },
    {
        date: '2026-01-12',
        version: '1.3',
        title: 'Fix Railway deployment: Remove tkinter dependency from API',
        changes: [
            'Fix Railway deployment: Remove tkinter dependency from API',
        ]
    },
    {
        date: '2026-01-12',
        version: '1.2',
        title: 'Add Railway deployment guide (with placeholders for secrets)',
        changes: [
            'Add Railway deployment guide (with placeholders for secrets)',
        ]
    },
    {
        date: '2026-01-12',
        version: '1.1',
        title: 'Add Flask API for Railway deployment',
        changes: [
            'Add Flask API for Railway deployment',
        ]
    },
    {
        date: '2026-01-12',
        version: '1.0',
        title: 'Initial commit: Mental health companion app with AI therapy',
        changes: [
            'Initial commit: Mental health companion app with AI therapy',
        ]
    },
];
