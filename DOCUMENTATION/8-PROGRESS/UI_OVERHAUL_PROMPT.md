# Healing Space UK — Complete UI Overhaul Prompt

## MISSION

You are a senior UI/UX engineer and design system architect. Your task is to perform a
**complete, meticulously detailed UI overhaul** of the Healing Space UK mental health
platform — a full-stack Flask web application. The result must feel **world-class,
modern, and futuristic** while remaining calming, professional, and clinically appropriate.
Reference aesthetic: Linear.app meets Vercel dashboard meets a premium health app.

---

## NON-NEGOTIABLE RULES — READ BEFORE TOUCHING ANYTHING

### ❌ NEVER rename, remove, or structurally alter:

**HTML element IDs (backend/JS depends on these):**
- All tab content IDs: `homeTab`, `therapyTab`, `safetyTab`, `gratitudeTab`, `cbtTab`,
  `petTab`, `clinicalTab`, `historyTab`, `communityTab`, `messagesTab`, `updatesTab`,
  `insightsTab`, `appointmentsTab`, `aboutmeTab`, `professionalTab`, `developerTab`
- All subtab IDs: `clinicalOverviewTab`, `clinicalPatientsTab`, `clinicalMessagesTab`,
  `clinicalAppointmentsTab`, `clinicalApprovalsTab`, `clinicalRiskmonitorTab`
- All auth screen IDs: `authScreen`, `appScreen`, `authMessage`, `landingPage`,
  `patientLoginForm`, `clinicianLoginForm`, `registerForm`, `clinicianRegisterForm`,
  `forgotPasswordForm`
- All functional IDs: `chatContainer`, `chatMessages`, `messageInput`, `sendBtn`,
  `sidebarNav`, `assessmentModal`, `assessmentQuestions`, `assessmentProgressBar`,
  `moodChart`, `sleepChart`, `calendarMonth`, `calendarDaysGrid`,
  `activePatientsCount`, `appointmentsList`, `messagesTabBtn`, `professionalTabBtn`,
  `developerTabBtn`, `authDarkModeToggle`, `darkModeToggle`, `themeToggle`, `themeIcon`
- All messaging IDs: `conversations-list`, `conversation-thread`, `recipient-input`,
  `subject-input`, `message-input`, `search-input`, `search-results`, `unread-badge`

**JavaScript function names (called by inline onclick handlers):**
- `login(userType)`, `register()`, `clinicianRegister()`, `forgotPassword()`
- `showLanding()`, `showPatientAuth()`, `showClinicianAuth()`, `hideAllAuthForms()`
- `togglePassword(inputId, button)`
- `switchTab(name, element)`, `switchClinicalTab(name, element)`,
  `switchPatientMessageTab(name, element)`
- `sendMessage()`, `loadConversation(id)`, `deleteMessage(id)`
- `startCSSRS()`, `nextAssessmentQuestion()`, `prevAssessmentQuestion()`,
  `submitAssessment()`, `showRiskAlert(riskLevel)`, `updateSafetyPlan()`
- `updateProfile()`, `changePassword()`, `exportData()`, `deleteAccount()`
- `recordMood(rating)`, `recordSleep(hours)`, `trackEmotion(type)`
- `adjustForCrisisBar()`, `dismissCrisisBar()`, `syncThemeIcon()`
- `showScreen(name)` (landing page showcase tabs)

**CSS variable NAMES (values can change, names cannot):**
- All `--bg-*`, `--text-*`, `--border-*`, `--shadow-*`, `--accent-*` variable names
- `--brand-gradient`, `--brand-primary`, `--brand-secondary`
- `--transition-fast`, `--transition-base`, `--transition-slow`
- `--nav-bg`, `--nav-border`, `--footer-bg`, `--footer-text`, `--footer-heading`

**CSS class names used by JavaScript:**
- `.tab-btn`, `.tab-content`, `.active` (tab system)
- `.clinical-subtab-btn`, `.clinical-subtab-content`
- `.message-subtab-btn`, `.message-subtab-content`
- `.messaging-tab`, `.messaging-panel`
- `.conversation-item`, `.message-thread`, `.message`, `.message.sent`,
  `.message.received`
- `.modal`, `.modal-content`, `.modal-header`, `.modal-body`, `.modal-footer`,
  `.close-modal`
- `.notification`, `.notification.show`, `.notification.success`,
  `.notification.error`, `.notification.info`
- `.navbar`, `.navbar-container`, `.navbar-logo`, `.navbar-menu`, `.logo-icon`
- `.page-watermark-fixed`
- `.crisis-bar`, `.crisis-bar-dismiss`
- `.btn-primary`, `.btn-secondary`, `.btn-small`, `.btn-small.delete`
- `.badge`, `.badge.unread`, `.badge.public`, `.badge.private`
- `.empty-state`, `.unread-badge`

**Jinja2 template syntax:**
- All `{{ variable }}` and `{% block %}` expressions — preserve exactly
- All `url_for('static', filename='...')` calls
- All `{{ url_for(...) }}` route references

**Form field names/IDs:**
- All `<input name="...">` and `<input id="...">` used in form submissions to Flask
- Any `data-*` attribute used by JS

---

## NEW DESIGN SYSTEM

### 1. Typography

**Primary Font (replace system stack everywhere):**
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
```
- **UI font:** `'Inter', -apple-system, BlinkMacSystemFont, sans-serif`  
  → Used for body text, labels, inputs, nav links, table cells
- **Display font:** `'Plus Jakarta Sans', 'Inter', sans-serif`  
  → Used for headings (h1–h3), hero titles, dashboard section headers, card titles
- **Mono font:** `'Fira Code', 'SF Mono', 'Cascadia Code', monospace`  
  → Used for code blocks, dev dashboard, diagnostic output, API keys

**Type Scale:**
```
--text-xs:   0.75rem   / 12px  — labels, badges, timestamps
--text-sm:   0.875rem  / 14px  — secondary text, table cells, metadata
--text-base: 1rem      / 16px  — body text, form inputs
--text-lg:   1.125rem  / 18px  — card titles, subheadings
--text-xl:   1.25rem   / 20px  — section titles, tab headings
--text-2xl:  1.5rem    / 24px  — page headings, modal titles
--text-3xl:  1.875rem  / 30px  — major section headers
--text-4xl:  2.25rem   / 36px  — hero subtitles
--text-5xl:  3rem      / 48px  — hero title
--text-6xl:  3.75rem   / 60px  — landing hero (desktop)
```

**Font Weights:**
```
300 — thin decorative text
400 — body copy
500 — medium emphasis (nav links, table headers)
600 — semibold (card titles, button labels)
700 — bold (section headers, primary headings)
800 — extra bold (hero titles, display headings)
```

**Line Heights:**
```
1.2 — headings, display text
1.5 — body copy
1.7 — long-form text (about sections, feature descriptions)
```

---

### 2. Color Palette

Keep the existing indigo/purple brand identity but upgrade every token:

**Brand (unchanged hue, refined):**
```css
--brand-primary:   #6366f1;  /* Indigo 500 — replaces #667eea */
--brand-secondary: #8b5cf6;  /* Violet 500 — replaces #764ba2 */
--brand-tertiary:  #06b6d4;  /* Cyan 500 — new accent for highlights */
--brand-gradient:  linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
--brand-gradient-dark: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
```

**Semantic Colors:**
```css
--success:  #10b981;  /* Emerald 500 */
--warning:  #f59e0b;  /* Amber 500 */
--danger:   #ef4444;  /* Red 500 */
--info:     #3b82f6;  /* Blue 500 */
--success-light: rgba(16,185,129,0.12);
--warning-light: rgba(245,158,11,0.12);
--danger-light:  rgba(239,68,68,0.12);
--info-light:    rgba(59,130,246,0.12);
```

**Light Mode Neutrals:**
```css
--bg-page:        #f8f9ff;   /* Very slight indigo tint — not pure white */
--bg-surface:     #ffffff;
--bg-elevated:    #ffffff;
--bg-card:        #ffffff;
--bg-input:       #ffffff;
--bg-sidebar:     #f4f5fd;
--bg-hover:       #f0f1fd;
--text-primary:   #0f0f23;   /* Near-black with indigo tint */
--text-secondary: #4b5280;   /* Slate-indigo */
--text-muted:     #9496b8;
--border-color:   #e5e7f5;   /* Indigo-tinted border */
--shadow-color:   rgba(99,102,241,0.08);
--accent-color:   #6366f1;
--accent-gradient: linear-gradient(135deg, #6366f1, #8b5cf6);
```

**Dark Mode Neutrals:**
```css
--bg-page:        #080812;   /* Deep space black */
--bg-surface:     #0e0e1c;   /* Slightly lighter */
--bg-elevated:    #14142a;   /* Card backgrounds */
--bg-card:        #14142a;
--bg-input:       #1c1c38;
--bg-sidebar:     #0a0a18;
--bg-hover:       #1c1c38;
--text-primary:   #e8e8ff;   /* Lavender-white */
--text-secondary: #9090c0;
--text-muted:     #5050a0;
--border-color:   rgba(99,102,241,0.18);
--shadow-color:   rgba(0,0,0,0.4);
--accent-color:   #818cf8;   /* Lighter indigo for dark */
--accent-gradient: linear-gradient(135deg, #818cf8, #a78bfa);
```

**Glow effects (dark mode only):**
```css
--glow-primary: 0 0 20px rgba(99,102,241,0.35);
--glow-success: 0 0 20px rgba(16,185,129,0.30);
--glow-danger:  0 0 20px rgba(239,68,68,0.30);
--glow-cyan:    0 0 20px rgba(6,182,212,0.30);
```

---

### 3. Spacing Scale

```css
--space-1:  0.25rem   /*  4px */
--space-2:  0.5rem    /*  8px */
--space-3:  0.75rem   /* 12px */
--space-4:  1rem      /* 16px */
--space-5:  1.25rem   /* 20px */
--space-6:  1.5rem    /* 24px */
--space-8:  2rem      /* 32px */
--space-10: 2.5rem    /* 40px */
--space-12: 3rem      /* 48px */
--space-16: 4rem      /* 64px */
--space-20: 5rem      /* 80px */
--space-24: 6rem      /* 96px */
```

---

### 4. Border Radius

```css
--radius-sm:   4px
--radius-base: 8px
--radius-md:   12px
--radius-lg:   16px
--radius-xl:   20px
--radius-2xl:  28px
--radius-full: 9999px  /* Pills, tags, avatars */
```

---

### 5. Shadow System

**Light mode:**
```css
--shadow-xs:  0 1px 3px rgba(99,102,241,0.06), 0 1px 2px rgba(0,0,0,0.04);
--shadow-sm:  0 2px 8px rgba(99,102,241,0.08), 0 1px 4px rgba(0,0,0,0.05);
--shadow-md:  0 4px 16px rgba(99,102,241,0.10), 0 2px 8px rgba(0,0,0,0.06);
--shadow-lg:  0 8px 32px rgba(99,102,241,0.12), 0 4px 16px rgba(0,0,0,0.08);
--shadow-xl:  0 16px 56px rgba(99,102,241,0.15), 0 8px 28px rgba(0,0,0,0.10);
--shadow-2xl: 0 24px 80px rgba(99,102,241,0.18), 0 12px 40px rgba(0,0,0,0.12);
```

**Dark mode — replace with glow shadows:**
```css
--shadow-xs:  0 1px 3px rgba(0,0,0,0.3);
--shadow-sm:  0 2px 8px rgba(0,0,0,0.4);
--shadow-md:  0 4px 16px rgba(0,0,0,0.5), 0 0 0 1px rgba(99,102,241,0.08);
--shadow-lg:  0 8px 32px rgba(0,0,0,0.6), 0 0 0 1px rgba(99,102,241,0.12);
--shadow-xl:  0 0 40px rgba(99,102,241,0.20), 0 16px 56px rgba(0,0,0,0.6);
--shadow-2xl: 0 0 60px rgba(99,102,241,0.25), 0 24px 80px rgba(0,0,0,0.7);
```

---

### 6. Animation System

All new animations must respect `prefers-reduced-motion`:
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

**New keyframe animations to add:**

```css
/* Floating glow blob for auth/hero backgrounds */
@keyframes blob-float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33%       { transform: translate(24px, -18px) scale(1.05); }
  66%       { transform: translate(-12px, 20px) scale(0.97); }
}

/* Shimmer for loading states */
@keyframes shimmer {
  0%   { background-position: -400px 0; }
  100% { background-position: 400px 0; }
}

/* Slide up entrance */
@keyframes slide-up {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Scale pop for notifications and badges */
@keyframes scale-pop {
  0%, 100% { transform: scale(1); }
  50%       { transform: scale(1.08); }
}

/* Pulse ring for active states */
@keyframes pulse-ring {
  0%   { box-shadow: 0 0 0 0 rgba(99,102,241,0.4); }
  70%  { box-shadow: 0 0 0 10px rgba(99,102,241,0); }
  100% { box-shadow: 0 0 0 0 rgba(99,102,241,0); }
}

/* Gradient shift (for accent borders) */
@keyframes gradient-shift {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
```

**Transition standards:**
```css
--transition-fast:   150ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-base:   250ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-slow:   400ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-spring: 500ms cubic-bezier(0.34, 1.56, 0.64, 1);  /* Bouncy */
```

---

### 7. Glassmorphism Tokens

Apply to: modals, auth boxes, floating cards, crisis bar, sticky CTAs.

```css
/* Light mode glass */
--glass-bg:     rgba(255,255,255,0.72);
--glass-border: rgba(255,255,255,0.45);
--glass-blur:   blur(16px) saturate(1.8);

/* Dark mode glass */
--glass-bg-dark:     rgba(14,14,28,0.78);
--glass-border-dark: rgba(99,102,241,0.18);
--glass-blur-dark:   blur(20px) saturate(1.6);
```

---

## GLOBAL CHANGES (apply everywhere)

### Scrollbar Styling
```css
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: rgba(99,102,241,0.3);
  border-radius: var(--radius-full);
}
::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,0.55); }
```

### Selection
```css
::selection {
  background: rgba(99,102,241,0.25);
  color: inherit;
}
```

### Focus Rings
```css
:focus-visible {
  outline: 2px solid var(--brand-primary);
  outline-offset: 3px;
  border-radius: var(--radius-sm);
}
```

### Body
```css
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: var(--text-base);
  line-height: 1.6;
  color: var(--text-primary);
  background: var(--bg-page);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

---

## COMPONENT REDESIGNS

### BUTTONS

**Primary:**
```css
.btn-primary {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  padding: 10px 20px;
  font-family: 'Inter', sans-serif;
  font-size: var(--text-sm);
  font-weight: 600;
  letter-spacing: 0.01em;
  color: #ffffff;
  background: var(--brand-gradient);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-base);
  box-shadow: 0 2px 12px rgba(99,102,241,0.35);
  position: relative;
  overflow: hidden;
  white-space: nowrap;
}
/* Shimmer on hover */
.btn-primary::before {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(105deg, transparent 40%, rgba(255,255,255,0.18) 60%, transparent 70%);
  transform: translateX(-100%);
  transition: transform 0.45s ease;
}
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 6px 24px rgba(99,102,241,0.45); }
.btn-primary:hover::before { transform: translateX(100%); }
.btn-primary:active { transform: translateY(0); }
```

**Secondary:**
```css
.btn-secondary {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  padding: 10px 20px;
  font-size: var(--text-sm); font-weight: 600;
  color: var(--brand-primary);
  background: transparent;
  border: 1.5px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-base);
}
.btn-secondary:hover {
  background: var(--bg-hover);
  border-color: var(--brand-primary);
  transform: translateY(-1px);
}
[data-theme="dark"] .btn-secondary:hover { box-shadow: var(--glow-primary); }
```

**Ghost / Icon buttons:**
```css
.btn-icon {
  display: inline-flex; align-items: center; justify-content: center;
  width: 36px; height: 36px;
  background: var(--bg-hover); border: none; border-radius: var(--radius-base);
  color: var(--text-secondary); cursor: pointer;
  transition: all var(--transition-fast);
}
.btn-icon:hover { background: var(--brand-primary); color: #fff; transform: scale(1.05); }
```

**Danger:**
```css
.btn-danger {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: #fff; border: none; border-radius: var(--radius-md);
  padding: 10px 20px; font-weight: 600; font-size: var(--text-sm);
  cursor: pointer; transition: all var(--transition-base);
  box-shadow: 0 2px 12px rgba(239,68,68,0.30);
}
.btn-danger:hover { transform: translateY(-2px); box-shadow: 0 6px 24px rgba(239,68,68,0.40); }
```

---

### CARDS

**Standard card:**
```css
.card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
  transition: box-shadow var(--transition-base), transform var(--transition-base),
              border-color var(--transition-base);
}
.card:hover { box-shadow: var(--shadow-lg); border-color: var(--border-accent); }
[data-theme="dark"] .card { background: var(--bg-elevated); }
[data-theme="dark"] .card:hover { box-shadow: var(--shadow-xl); }
```

**Glass card (modals, auth box, floating panels):**
```css
.card-glass {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-xl);
}
[data-theme="dark"] .card-glass {
  background: var(--glass-bg-dark);
  border-color: var(--glass-border-dark);
}
```

**Stat card (dashboard metrics):**
```css
.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  padding: var(--space-5) var(--space-6);
  display: flex; flex-direction: column; gap: var(--space-3);
  position: relative; overflow: hidden;
  transition: all var(--transition-base);
}
/* Accent left border + top-right glow blob */
.stat-card::before {
  content: ''; position: absolute; top: 0; left: 0;
  width: 3px; height: 100%;
  background: var(--brand-gradient);
  border-radius: var(--radius-full);
}
.stat-card::after {
  content: ''; position: absolute; top: -20px; right: -20px;
  width: 80px; height: 80px; border-radius: 50%;
  background: radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%);
}
.stat-card .stat-value { font-size: var(--text-3xl); font-weight: 800; color: var(--brand-primary); }
.stat-card .stat-label { font-size: var(--text-sm); font-weight: 500; color: var(--text-secondary); }
```

---

### INPUTS & FORMS

```css
.form-group { display: flex; flex-direction: column; gap: var(--space-2); }
.form-label {
  font-size: var(--text-sm); font-weight: 600;
  color: var(--text-secondary); letter-spacing: 0.02em;
}

.form-input, input[type="text"], input[type="email"], input[type="password"],
input[type="number"], textarea, select {
  width: 100%;
  padding: 11px 14px;
  font-family: 'Inter', sans-serif;
  font-size: var(--text-base);
  color: var(--text-primary);
  background: var(--bg-input);
  border: 1.5px solid var(--border-color);
  border-radius: var(--radius-md);
  outline: none;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  -webkit-appearance: none;
}
.form-input:hover { border-color: rgba(99,102,241,0.4); }
.form-input:focus {
  border-color: var(--brand-primary);
  box-shadow: 0 0 0 3px rgba(99,102,241,0.15);
}
[data-theme="dark"] .form-input:focus {
  box-shadow: 0 0 0 3px rgba(99,102,241,0.25), var(--glow-primary);
}
.form-input::placeholder { color: var(--text-muted); }
```

---

### BADGES & TAGS

```css
.badge {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 10px;
  font-size: var(--text-xs); font-weight: 600; letter-spacing: 0.04em;
  border-radius: var(--radius-full);
  border: 1px solid transparent;
}
.badge.unread  { background: var(--danger-light);  color: var(--danger);  border-color: rgba(239,68,68,0.25); }
.badge.public  { background: var(--info-light);    color: var(--info);    border-color: rgba(59,130,246,0.25); }
.badge.private { background: var(--warning-light); color: var(--warning); border-color: rgba(245,158,11,0.25); }
.badge.success { background: var(--success-light); color: var(--success); border-color: rgba(16,185,129,0.25); }
.badge.primary { background: rgba(99,102,241,0.12); color: var(--brand-primary); border-color: rgba(99,102,241,0.25); }
```

---

### MODAL

```css
.modal {
  position: fixed; inset: 0; z-index: 9000;
  display: flex; align-items: center; justify-content: center;
  padding: var(--space-4);
  background: rgba(0,0,0,0.55);
  backdrop-filter: blur(6px);
  opacity: 0; visibility: hidden;
  transition: opacity var(--transition-base), visibility var(--transition-base);
}
.modal.active { opacity: 1; visibility: visible; }
.modal-content {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-2xl);
  width: 100%; max-width: 540px; max-height: 88vh; overflow-y: auto;
  animation: slide-up var(--transition-base) cubic-bezier(0.34, 1.56, 0.64, 1);
}
[data-theme="dark"] .modal-content {
  background: var(--glass-bg-dark); border-color: var(--glass-border-dark);
}
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--space-5) var(--space-6);
  border-bottom: 1px solid var(--border-color);
}
.modal-header h2, .modal-header h3 { font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; }
.modal-body   { padding: var(--space-6); }
.modal-footer { padding: var(--space-4) var(--space-6); border-top: 1px solid var(--border-color); display: flex; gap: var(--space-3); justify-content: flex-end; }
.close-modal  {
  display: flex; align-items: center; justify-content: center;
  width: 32px; height: 32px; border-radius: var(--radius-base);
  background: var(--bg-hover); border: none; cursor: pointer;
  color: var(--text-secondary); font-size: 18px;
  transition: all var(--transition-fast);
}
.close-modal:hover { background: var(--danger-light); color: var(--danger); transform: rotate(90deg); }
```

---

### NOTIFICATION / TOAST

```css
.notification {
  position: fixed; bottom: 24px; right: 24px; z-index: 10100;
  display: flex; align-items: flex-start; gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  min-width: 300px; max-width: 420px;
  background: var(--glass-bg); backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  transform: translateX(120%); opacity: 0;
  transition: transform var(--transition-slow), opacity var(--transition-slow);
}
.notification.show   { transform: translateX(0); opacity: 1; }
.notification.success { border-left: 3px solid var(--success); }
.notification.error   { border-left: 3px solid var(--danger); }
.notification.info    { border-left: 3px solid var(--info); }
[data-theme="dark"] .notification { background: var(--glass-bg-dark); border-color: var(--glass-border-dark); }
```

---

### TABS (main dashboard)

```css
.tab-bar {
  display: flex; gap: 2px; padding: 4px;
  background: var(--bg-surface); border-radius: var(--radius-lg);
  overflow-x: auto; -ms-overflow-style: none; scrollbar-width: none;
}
.tab-bar::-webkit-scrollbar { display: none; }

.tab-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 16px; white-space: nowrap;
  font-size: var(--text-sm); font-weight: 500;
  color: var(--text-secondary);
  background: transparent; border: none; border-radius: var(--radius-base);
  cursor: pointer;
  transition: all var(--transition-fast);
}
.tab-btn:hover   { background: var(--bg-hover); color: var(--text-primary); }
.tab-btn.active  {
  background: var(--bg-card); color: var(--brand-primary);
  font-weight: 600;
  box-shadow: var(--shadow-sm);
}
[data-theme="dark"] .tab-btn.active {
  background: var(--bg-elevated); color: var(--accent-color);
  box-shadow: 0 0 0 1px rgba(99,102,241,0.2);
}
```

---

## PAGE-BY-PAGE REQUIREMENTS

---

### PAGE 1: `landing.html` — Public Landing Page

**Overall feel:** Premium SaaS landing page. The existing sections are good — refine and polish them.

**Nav bar:**
- Frosted glass effect when scrolled (`backdrop-filter: blur(20px)`)
- Pill-shaped login button with gradient border in unscrolled state
- Inter font for wordmark; adjust weight to 700
- Mobile hamburger transitions to X with smooth animation
- Add subtle gradient underline animation on hover for nav links
- Ensure the dark mode toggle has a polished style (circular button, 40×40px, transitions between ☀️ and 🌙 with a slight rotation)

**Hero section:**
- In light mode: existing `#667eea → #764ba2` purple gradient — KEEP but refine with a subtle radial overlay
- In dark mode: existing `#1e2a6e → #2d1554` darker gradient — KEEP
- Add animated mesh gradient (CSS only, 2-3 large blurred circles with `blob-float` animation)
- Floating particles: increase opacity slightly, add colour variation (some cyan, some violet)
- Hero badge: pill shape, gradient border, frosted glass background
- Hero title: gradient text (`background-clip: text; -webkit-text-fill-color: transparent`) using brand gradient
- CTAs: primary button with shimmer on hover; ghost button with animated border
- Hero watermark: KEEP as-is

**Stats strip:**
- Dark background (existing) — add gradient border-top
- Stats: large number in gradient text, label in muted text
- Animated counter via IntersectionObserver when the strip enters viewport (add JS, preserving existing functions)

**Features section:**
- Feature cards: `--radius-xl`, gradient icon containers (each feature gets a colour variant), hover lifts card and shows coloured glow
- Section headings: gradient accent word (e.g. "core" in brand gradient)

**Product showcase tabs:**
- Existing tab structure KEEP — restyle with pill-shaped tabs, smooth underline slide
- Browser mockup: rounded to `--radius-xl`, deeper shadow, subtle gradient border

**How it works:**
- Number badges: gradient circles
- Step connectors: dashed gradient line between steps

**Clinician section:**
- Keep the two-column layout but upgrade visual hierarchy

**Testimonials:**
- Cards with frosted glass effect, avatar area with gradient ring border
- Star ratings rendered as actual coloured star icons

**Pricing:**
- Feature card for recommended plan: gradient border, `--shadow-2xl`, slightly larger
- Add a subtle animated gradient ring around the recommended plan badge
- Checkmark icons: brand-coloured, not plain emoji

**Trust / Security badges:**
- Pill-shaped, semi-transparent backgrounds, small brand icons or text badges

**FAQ:**
- Smooth accordion animation on open/close (height transition with overflow: hidden)
- Chevron icon rotates 180° on open

**Footer:**
- Dark gradient footer (existing) — add horizontal gradient border-top
- Footer logo uses `filter: brightness(1.5) saturate(1.15)` already — KEEP
- Social links (if present): circular icon buttons

**Crisis bar:**
- KEEP all existing JS — only restyle: gradient left border instead of solid; frosted glass background; close button with hover rotation

---

### PAGE 2: `index.html` — Auth Screen + Patient/Clinician/Admin Dashboard

**Auth Screen (login page):**
- Body: KEEP `var(--bg-primary)` purple gradient as background
- Add 2-3 large blurred blob divs (`position: absolute`, `filter: blur(80px)`, `animation: blob-float`) for depth — these are purely decorative divs added BEFORE the auth container
- Auth box: glass morphism — `background: rgba(255,255,255,0.85); backdrop-filter: blur(24px)` in light; `background: rgba(14,14,28,0.85)` in dark
- Auth box border: `border: 1px solid rgba(255,255,255,0.3)` in light; `border: 1px solid rgba(99,102,241,0.25)` in dark
- Auth box shadow: `var(--shadow-2xl)`, in dark mode also add `var(--glow-primary)`
- Logo: `auth-logo-img` — KEEP SIZE/POSITION, update drop-shadow to use brand colour
- Tab switcher (Patient / Clinician): styled as pill toggle, gradient underline on active tab, NOT just border-bottom
- Form inputs: updated to new form-input spec above
- Buttons: updated to new btn-primary spec above
- Verify email button: style as ghost button, with a cyan accent
- Dark mode toggle on auth page (`id="authDarkModeToggle"`): KEEP — restyle to match landing page toggle

**App Navigation (sidebar):**
- `#sidebarNav` — convert from plain list to a frosted glass sidebar
- In dark mode: `background: rgba(8,8,18,0.9); backdrop-filter: blur(12px); border-right: 1px solid rgba(99,102,241,0.12)`
- Tab buttons (`.tab-btn`) with `.active` state: active = gradient left border (3px) + brand colour text + soft bg highlight
- Tab button icons: if emoji icons are used, wrap in a 28×28px gradient circle when active
- Mobile: sidebar collapses to a bottom navigation bar on screens ≤768px

**App Header:**
- `header-logo-img` — KEEP — add gradient glow drop-shadow in dark mode (already done)
- "Healing Space UK" wordmark: Inter 700
- Dark mode toggle: match landing page design
- User info chips: pill-shaped, subtle background

**Home Tab (`homeTab`):**
- Welcome card: upgrade gradient; add large semi-transparent emoji or icon in top-right as decoration
- Daily tasks: checkbox-style list items with smooth check animation
- Quick navigation grid: icon buttons with gradient icon containers, hover lift effect
- Pet display: rounded card with soft gradient background

**Therapy/Chat Tab (`therapyTab`):**
- Chat messages: `sent` bubbles = brand gradient, `received` bubbles = card background
- Bubble border-radius: `20px 20px 4px 20px` (sent) / `20px 20px 20px 4px` (received)
- Add subtle timestamp on hover for each message
- Input area: glass morphism container, gradient border-top, send button = gradient circle icon button
- Sessions list: pill-shaped session name chips

**Mood Tracking:**
- Mood options: large emoji buttons with animated scale on selection, selected state has gradient ring
- Charts: if Chart.js — use purple gradient fills, custom tooltips

**Safety Tab (`safetyTab`):**
- Crisis resources box: upgrade to a bold card with red gradient top border, NOT just a coloured div
- Safety plan items: checkboxes replaced with toggle switches styled with brand gradient

**Clinical Tab (`clinicalTab`) — clinician only:**
- Subtab navigation: pill tabs matching the main tab bar spec above
- Patient cards: gradient left border (3px), hover lifts card
- Risk indicator badges: use new badge spec
- Stats row: use new stat-card spec

**Messages Tab (`messagesTab`):**
- Match the new messaging page styling (see messaging pages below)

**Settings / About Me:**
- Section dividers: gradient horizontal rules (1px gradient line, not grey)
- Avatar/profile image: 80px circle with gradient ring border

**Assessments / Modals:**
- All modals: apply glass morphism modal spec above
- Progress bar: gradient fill (brand gradient), rounded ends
- Question cards: `--radius-xl`, `var(--shadow-sm)`

---

### PAGE 3: `messaging.html` — Patient Messaging

**Overall:**
- Background: `var(--bg-page)` — inherits theme (NOT hardcoded `#f5f6fa`)
- Navbar: KEEP structure, apply new navbar spec from messaging pages

**Navbar (all messaging pages share this):**
```css
.navbar {
  background: var(--brand-gradient);
  backdrop-filter: none; /* gradient, no blur */
  padding: 0;
  box-shadow: 0 4px 20px rgba(99,102,241,0.30);
}
.navbar-container { padding: 0 24px; height: 64px; }
.navbar-logo { font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; font-size: 1.1rem; }
.logo-icon { filter: brightness(0) invert(1); /* White silhouette on gradient — KEEP */ }
.navbar-menu a {
  font-size: var(--text-sm); font-weight: 500; color: rgba(255,255,255,0.82);
  padding: 6px 12px; border-radius: var(--radius-base);
  transition: all var(--transition-fast);
}
.navbar-menu a:hover, .navbar-menu a.active {
  color: #fff; background: rgba(255,255,255,0.15);
}
```

**Tab bar (`.messaging-tabs`):**
- Apply pill tab spec above — horizontal scroll on mobile, gradient underline slide on active

**Conversation layout:**
- Sidebar: card background, rounded, shadow
- Conversation items: smooth hover, active = gradient left border + brand tint background
- Unread dot: cyan accent dot (6px circle)

**Message thread:**
- Sent: gradient bubble (brand gradient), white text, right-aligned
- Received: card background, primary text, left-aligned
- Avatar initials: gradient circle
- Timestamps: fade in on hover (`var(--text-muted)`, `var(--text-xs)`)

**Input section:**
- Full-width glass card pinned to bottom
- Inputs: new form-input spec
- Send button: gradient circle button (48px)

---

### PAGE 4: `clinician-messaging.html` — Clinician Messaging Dashboard

**Same navbar and tab bar as messaging.html.**

**Dashboard stats cards (`.dashboard-card`):**
- Apply new stat-card spec
- Value in brand gradient text
- Icon in gradient circle (40px)

**Patient cards (`.patient-card`):**
- `border-left: 3px solid var(--brand-primary)` → upgrade to gradient border using the `::before` pseudo-element trick
- Risk badge: use new badge spec (`badge.danger`, `badge.warning`, `badge.success`)
- Hover: lift + glow

---

### PAGE 5: `admin-messaging.html` — Admin Messaging Console

**Same navbar and tab bar.**

**Stat cards (`.stat-card`):**
- Purple variant: replace `#6c5ce7` solid gradient with brand gradient
- Green variant (`.secondary`): use `var(--success)` gradient
- Red variant (`.danger`): use `var(--danger)` gradient
- Apply new stat-card spec (gradient left border, glow blob)

**Broadcast / message tables:**
- Table headers: `var(--bg-surface)`, `var(--text-secondary)`, `font-weight: 600`, uppercase, `letter-spacing: 0.06em`
- Table rows: hover background `var(--bg-hover)`
- Table borders: `var(--border-color)`
- Alternating rows: very subtle (1-2% lighter than base)

---

### PAGE 6: `developer-dashboard.html` — Developer Dashboard

**Background:** KEEP existing purple gradient (`linear-gradient(135deg, #667eea, #764ba2)`) — it's a private page, the gradient is fine.

**Dashboard container:**
- White/card sections: apply `--radius-xl`, `--shadow-lg`
- Add gradient border-top to the container header card (3px gradient line at top)

**Auth section:**
- Style as a distinct glass card inside the main container

**Buttons:** Apply new `.btn-primary` and `.btn-secondary` styles, replacing all hardcoded `background: #667eea; color: white; border: none`.

**Code output/logs section:**
- Dark background: `#0a0a18`; font: monospace stack; text: `#a0ffb0` (terminal green)
- Border: `1px solid rgba(99,102,241,0.2)`, border-radius `--radius-md`
- Add subtle scanline gradient overlay for terminal feel

**AI chat section (if present):**
- Apply chat bubble spec from therapy tab above

---

### PAGE 7: `admin-wipe.html` — Admin Data Wipe

**Background:** KEEP purple gradient — it's intentionally ominous for a destructive action page.

**Container card:**
- Glass morphism — `rgba(255,255,255,0.10)` glass on the gradient
- Border: `rgba(239,68,68,0.40)` (red tint — danger warning)
- Add a pulsing red dot or warning icon at the top

**Buttons:**
- Wipe/confirm actions: use `.btn-danger` spec above (red gradient, glow)
- Cancel/back: use `.btn-secondary`

**Log output:**
- Terminal style (same as developer dashboard)

**Warning text:**
- `--danger` colour, bold, possibly with a ⚠️ prefix icon

---

### PAGE 8: `diagnostic.html` — Diagnostic Test Page

**Background:** `var(--bg-page)` (light grey / dark page based on OS preference via `prefers-color-scheme`)

**Test box:**
- Apply `.card` spec — `--radius-xl`, `--shadow-md`
- Header: gradient text for "Healing Space Diagnostic Test"
- Status indicators: green dot (pulse animation) = pass, red dot = fail
- Test result list items: alternating background rows, green/red icons

---

## DARK MODE CONSISTENCY RULES

1. **Every page must respect `data-theme="dark"` OR `@media (prefers-color-scheme: dark)`** — never both patterns on the same page. Standardise: index.html and landing.html use `[data-theme="dark"]`; messaging pages use `@media (prefers-color-scheme: dark)`.

2. **Glow on dark:** In dark mode, every interactive element that is focused, active, or hovered must emit a soft glow using `var(--glow-primary)` or a coloured variant.

3. **Glass card borders in dark:** Use `rgba(99,102,241,0.18)` not pure white rgba — white borders on near-black look harsh.

4. **Page watermarks in dark:** KEEP existing CSS — white silhouette on dark/gradient pages; natural colours on light pages.

5. **Logo brightness in dark:** KEEP existing CSS — `filter: brightness(1.5) drop-shadow(...)`.

---

## ANIMATION IMPLEMENTATION RULES

1. **Tab switches:** add `animation: slide-up 200ms ease` on `.tab-content` elements when they gain `.active`.

2. **Modal open:** `animation: slide-up var(--transition-base)` on `.modal-content`.

3. **Card hover lifts:** `transform: translateY(-3px)` — always pair with box-shadow deepening.

4. **Button hovers:** `transform: translateY(-2px)` for primary; `translateY(-1px)` for secondary.

5. **Blob backgrounds:** purely `CSS animation: blob-float` — no JS needed. Apply 2-3 per page that uses a gradient body (auth page, dev dashboard, admin wipe, hero section).

6. **IntersectionObserver counter animation:** Add to all stat numbers on landing page. Use `requestAnimationFrame` loop, no external libraries. Do NOT add any new global variables or function names that conflict with existing JS.

7. **Shimmer on primary buttons:** CSS `::before` pseudo-element, `transform: translateX(-100%) → translateX(100%)` on hover.

8. **Accordion FAQ:** `max-height` transition from `0` to `max-height: 1000px`, paired with `overflow: hidden`.

9. **All animations must wrap in `prefers-reduced-motion` media query.**

---

## RESPONSIVE / MOBILE RULES

**Breakpoints:**
```
xs:  0–479px    (phones portrait)
sm:  480–767px  (phones landscape)
md:  768–1023px (tablets)
lg:  1024–1279px (small desktop)
xl:  1280px+    (full desktop)
```

**Navigation mobile patterns:**
- Landing: KEEP existing hamburger → slide-down mobile menu, apply new styles
- index.html: sidebar nav collapses to a bottom tab bar on ≤768px; tab buttons show icon + short label only
- Messaging pages: KEEP existing responsive styles, update colours only

**Cards:** `grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))` — ensure cards stack on mobile without overflow.

**Modals:** Full-screen below 480px (`width: 100%; height: 100%; border-radius: 0` or just top-rounded).

**Buttons:** Full-width on mobile when inside a form; keep auto-width when in toolbars.

**Tables:** Horizontal scroll on mobile (`overflow-x: auto` on parent wrapper).

---

## ACCESSIBILITY REQUIREMENTS

- All interactive elements: WCAG 2.1 AA contrast ratio (4.5:1 text, 3:1 UI components)
- Focus rings: `outline: 2px solid var(--brand-primary); outline-offset: 3px` — NEVER suppress focus rings
- ARIA labels: preserve all existing `aria-*` attributes, add to any new interactive elements
- Keyboard navigation: all tabs, modals, accordions must be keyboard-accessible
- Error states: not just colour — add an icon AND descriptive text
- Dark mode: must not reduce contrast below AA

---

## IMPLEMENTATION SEQUENCE

Execute in this strict order to avoid breaking functionality:

1. **Update CSS files first:**
   - Update `theme-variables.css` — new design tokens, expanded variable set
   - Update `components.css` — new component CSS (buttons, cards, inputs, badges, modals, notifications, tabs, scrollbars, selection, focus)
   - Update `messaging.css` — navbar, tab bar, conversation layout, message bubbles
   - Update `theme-fixes.css` — remove overrides that are now handled by proper CSS
   - Update `ux-enhancements.css` — new toast spec, loading states, progress bars

2. **Update landing.html:**
   - Add font imports in `<head>` (Inter + Plus Jakarta Sans)
   - Update CSS variables in `:root` to new palette
   - Apply new component styles to each section
   - Add blob-float decorative divs to hero
   - Add IntersectionObserver counter animation for stats
   - Add FAQ accordion JS (small, self-contained, no global name conflicts)

3. **Update index.html:**
   - Add font imports
   - Update `:root` CSS variables to new palette
   - Add blob decorative divs to auth screen (before `#authScreen`)
   - Apply new card/input/button specs to auth forms
   - Apply new sidebar/tab styles
   - Apply new chat bubble styles
   - Update all modal styles

4. **Update messaging pages (all three):**
   - Apply new navbar CSS
   - Apply new tab bar CSS
   - Apply new conversation/message bubble CSS
   - Apply new input section CSS

5. **Update developer-dashboard.html, admin-wipe.html, diagnostic.html:**
   - Font imports
   - Updated button/card/input styles
   - Watermarks already in place — do not change

6. **Test each page in both light and dark mode after each file update.**

---

## COMMON ANTI-PATTERNS TO AVOID

- ❌ Never use `!important` unless overriding a third-party library
- ❌ Never use `#` ID selectors in CSS — use class selectors only
- ❌ Never add `z-index` values above 10000 (crisis bar is already at 10001 — leave it)
- ❌ Never add `overflow: hidden` to `<body>` — it breaks the scrolling on long pages
- ❌ Never add a `position: fixed` element without verifying it doesn't block existing fixed elements
- ❌ Never change a Jinja2 `{{ variable }}` to a hardcoded value
- ❌ Never remove an element with `id="..."` used by JS — only change its CSS class or style
- ❌ Never change `onclick="functionName()"` handler strings
- ❌ Never use `var()` for vendor-prefixed properties without a plain fallback value
- ❌ Never remove `aria-*`, `role`, or `tabindex` attributes
- ❌ Never reduce the click/tap target size below 44×44px for any interactive element

---

## FINAL QUALITY CHECKLIST

Before considering the overhaul complete, verify ALL of the following:

- [ ] Every page loads without JS errors in browser console
- [ ] All tabs switch correctly in index.html (patient, clinician, admin, developer views)
- [ ] Login, register, forgot-password flows all still submit to backend
- [ ] Messaging send/receive works in all three messaging pages
- [ ] Crisis bar appears, is dismissible, and does NOT cover the nav
- [ ] Watermark visible on all pages, appropriate contrast for each background
- [ ] Dark mode toggled correctly on landing.html and index.html (no FOUC)
- [ ] Messaging pages respond to `prefers-color-scheme: dark`
- [ ] All modals open and close (focus trapped, ESC closes)
- [ ] All forms validate and show errors
- [ ] Mobile navigation works (hamburger / bottom tab bar)
- [ ] No horizontal overflow on any page at 375px viewport width
- [ ] Tab bar on dashboard scrolls horizontally without showing scrollbar
- [ ] All interactive elements have visible focus rings
- [ ] Contrast ratios pass WCAG AA for all text/background combinations
- [ ] Reduced motion: all animations stop when `prefers-reduced-motion: reduce` is active
- [ ] No broken images (all logo/favicon references intact)
- [ ] Page watermarks not clickable (`pointer-events: none`)
- [ ] Favicon shows in browser tab on all pages
- [ ] Admin wipe and developer dashboard only accessible from correct user types (logic unchanged)
