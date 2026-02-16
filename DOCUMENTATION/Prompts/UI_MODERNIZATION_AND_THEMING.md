# UI Modernization & Dark/Light Theme Implementation - World-Class Prompt

**Version**: 1.0
**Created**: February 16, 2026
**Purpose**: Comprehensive UI modernization and theme consistency across entire application
**Scope**: All templates, components, and stylesheets

---

## 🎯 Objective

Modernize all UI components and ensure a fully functional, accessible dark/light theme system with WCAG 2.1 AA compliant contrast ratios across the entire Healing Space UK application.

---

## 📋 Pre-Execution Checklist

Before running this prompt, ensure:
- [ ] Virtual environment activated: `source venv/bin/activate`
- [ ] All dependencies installed
- [ ] Backup created: `git add . && git commit -m "Pre-UI modernization backup"`
- [ ] Development server can start successfully

---

## 🔍 Phase 1: Comprehensive Audit

### 1.1 Discover All UI Files

**Task**: Catalog all UI-related files in the application.

**Files to audit**:
```bash
# Templates
templates/*.html (7 files)

# CBT Components
cbt_tools/components/*.html (15 files)

# Stylesheets
static/css/*.css (2+ files)

# JavaScript files with UI logic
static/js/*.js
```

**Output**: Create `UI_AUDIT_REPORT.md` with:
- Complete file inventory
- Current theme implementation status per file
- Files missing theme support
- Hardcoded color values that need CSS variables
- Accessibility issues found

### 1.2 Analyze Current Theme System

**Examine**:
- `templates/index.html` (lines 76-130): CSS variable definitions
- `static/css/ux-enhancements.css`: Theme utilities
- Check for theme toggle implementation
- Identify inconsistencies in CSS variable usage

**Document**:
- Which CSS variables exist
- Which files use them consistently
- Which files have inline styles or hardcoded colors
- Theme persistence mechanism (localStorage?)

---

## 🎨 Phase 2: Design System Modernization

### 2.1 Enhanced CSS Variables System

**Create**: `static/css/theme-variables.css` with comprehensive design tokens:

```css
:root {
    /* ============================================
       SPACING SYSTEM
       ============================================ */
    --space-xs: 4px;
    --space-sm: 8px;
    --space-md: 16px;
    --space-lg: 24px;
    --space-xl: 32px;
    --space-2xl: 48px;
    --space-3xl: 64px;

    /* ============================================
       TYPOGRAPHY
       ============================================ */
    --font-family-base: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    --font-family-heading: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;

    --font-size-xs: 0.75rem;    /* 12px */
    --font-size-sm: 0.875rem;   /* 14px */
    --font-size-base: 1rem;     /* 16px */
    --font-size-lg: 1.125rem;   /* 18px */
    --font-size-xl: 1.25rem;    /* 20px */
    --font-size-2xl: 1.5rem;    /* 24px */
    --font-size-3xl: 1.875rem;  /* 30px */
    --font-size-4xl: 2.25rem;   /* 36px */

    --font-weight-normal: 400;
    --font-weight-medium: 500;
    --font-weight-semibold: 600;
    --font-weight-bold: 700;

    --line-height-tight: 1.25;
    --line-height-normal: 1.5;
    --line-height-relaxed: 1.75;

    /* ============================================
       LIGHT THEME COLORS
       ============================================ */
    /* Backgrounds */
    --bg-primary: #ffffff;
    --bg-secondary: #f8f9fa;
    --bg-tertiary: #e9ecef;
    --bg-elevated: #ffffff;
    --bg-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --bg-overlay: rgba(0, 0, 0, 0.5);

    /* Text colors */
    --text-primary: #1a202c;        /* WCAG AAA on white */
    --text-secondary: #4a5568;      /* WCAG AA on white */
    --text-tertiary: #718096;       /* WCAG AA on white */
    --text-muted: #a0aec0;
    --text-inverse: #ffffff;
    --text-link: #3182ce;
    --text-link-hover: #2c5aa0;

    /* Border colors */
    --border-primary: #e2e8f0;
    --border-secondary: #cbd5e0;
    --border-focus: #667eea;

    /* Interactive elements */
    --interactive-primary: #667eea;
    --interactive-primary-hover: #5568d3;
    --interactive-primary-active: #4c51bf;
    --interactive-secondary: #764ba2;
    --interactive-secondary-hover: #68409a;

    /* Status colors */
    --status-success: #38a169;      /* Green - WCAG AA */
    --status-success-bg: #f0fff4;
    --status-warning: #dd6b20;      /* Orange - WCAG AA */
    --status-warning-bg: #fffaf0;
    --status-error: #e53e3e;        /* Red - WCAG AA */
    --status-error-bg: #fff5f5;
    --status-info: #3182ce;         /* Blue - WCAG AA */
    --status-info-bg: #ebf8ff;

    /* Mental health specific colors */
    --emotion-calm: #bee3f8;        /* Calming blue */
    --emotion-energized: #fbd38d;   /* Energizing yellow */
    --emotion-grounded: #9ae6b4;    /* Grounding green */
    --emotion-safe: #e9d8fd;        /* Safe purple */

    /* Shadows */
    --shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);

    /* Border radius */
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;
    --radius-xl: 16px;
    --radius-full: 9999px;

    /* Transitions */
    --transition-fast: 150ms ease-in-out;
    --transition-base: 250ms ease-in-out;
    --transition-slow: 350ms ease-in-out;

    /* Z-index layers */
    --z-dropdown: 1000;
    --z-sticky: 1100;
    --z-modal-backdrop: 1200;
    --z-modal: 1300;
    --z-tooltip: 1400;
}

/* ============================================
   DARK THEME COLORS
   ============================================ */
[data-theme="dark"] {
    /* Backgrounds */
    --bg-primary: #1a202c;
    --bg-secondary: #2d3748;
    --bg-tertiary: #4a5568;
    --bg-elevated: #2d3748;
    --bg-gradient: linear-gradient(135deg, #4c51bf 0%, #553c9a 100%);
    --bg-overlay: rgba(0, 0, 0, 0.7);

    /* Text colors */
    --text-primary: #f7fafc;        /* WCAG AAA on dark */
    --text-secondary: #e2e8f0;      /* WCAG AA on dark */
    --text-tertiary: #cbd5e0;       /* WCAG AA on dark */
    --text-muted: #a0aec0;
    --text-inverse: #1a202c;
    --text-link: #63b3ed;
    --text-link-hover: #90cdf4;

    /* Border colors */
    --border-primary: #4a5568;
    --border-secondary: #718096;
    --border-focus: #667eea;

    /* Interactive elements */
    --interactive-primary: #667eea;
    --interactive-primary-hover: #7c8df0;
    --interactive-primary-active: #5568d3;
    --interactive-secondary: #9f7aea;
    --interactive-secondary-hover: #b794f4;

    /* Status colors - adjusted for dark background */
    --status-success: #48bb78;
    --status-success-bg: #22543d;
    --status-warning: #ed8936;
    --status-warning-bg: #744210;
    --status-error: #fc8181;
    --status-error-bg: #742a2a;
    --status-info: #4299e1;
    --status-info-bg: #2c5282;

    /* Mental health specific colors - dark mode variants */
    --emotion-calm: #2c5282;
    --emotion-energized: #975a16;
    --emotion-grounded: #276749;
    --emotion-safe: #553c9a;

    /* Shadows - enhanced for dark mode */
    --shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
    --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.4), 0 1px 2px 0 rgba(0, 0, 0, 0.3);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.3);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -2px rgba(0, 0, 0, 0.4);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.6), 0 10px 10px -5px rgba(0, 0, 0, 0.5);
}

/* ============================================
   REDUCED MOTION
   ============================================ */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* ============================================
   HIGH CONTRAST MODE
   ============================================ */
@media (prefers-contrast: high) {
    :root {
        --border-primary: #000000;
        --text-primary: #000000;
    }

    [data-theme="dark"] {
        --border-primary: #ffffff;
        --text-primary: #ffffff;
    }
}
```

### 2.2 Component Base Styles

**Create**: `static/css/components.css` with reusable component classes:

```css
/* Buttons */
.btn-primary {
    background: var(--interactive-primary);
    color: var(--text-inverse);
    border: none;
    padding: var(--space-sm) var(--space-lg);
    border-radius: var(--radius-md);
    font-weight: var(--font-weight-medium);
    transition: all var(--transition-base);
    cursor: pointer;
}

.btn-primary:hover {
    background: var(--interactive-primary-hover);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}

.btn-primary:active {
    background: var(--interactive-primary-active);
    transform: translateY(0);
}

/* Cards */
.card {
    background: var(--bg-elevated);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-lg);
    padding: var(--space-lg);
    box-shadow: var(--shadow-sm);
    transition: box-shadow var(--transition-base);
}

.card:hover {
    box-shadow: var(--shadow-md);
}

/* Inputs */
.input {
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    color: var(--text-primary);
    padding: var(--space-sm) var(--space-md);
    border-radius: var(--radius-md);
    font-size: var(--font-size-base);
    transition: all var(--transition-base);
}

.input:focus {
    outline: none;
    border-color: var(--border-focus);
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* And more components... */
```

---

## 🛠️ Phase 3: Implementation

### 3.1 Update Main Templates

**For each template in `templates/`**:

1. Add theme toggle button to header:
```html
<button id="themeToggle" class="theme-toggle" aria-label="Toggle dark mode">
    <span class="theme-icon-light">🌙</span>
    <span class="theme-icon-dark hidden">☀️</span>
</button>
```

2. Replace all inline styles with CSS variables
3. Remove hardcoded color values
4. Add `data-theme` attribute handler
5. Implement theme persistence:

```javascript
// Theme management
const themeToggle = document.getElementById('themeToggle');
const htmlElement = document.documentElement;

// Load saved theme
const savedTheme = localStorage.getItem('theme') || 'light';
htmlElement.setAttribute('data-theme', savedTheme);
updateThemeIcon(savedTheme);

themeToggle?.addEventListener('click', () => {
    const currentTheme = htmlElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';

    htmlElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
});

function updateThemeIcon(theme) {
    const lightIcon = document.querySelector('.theme-icon-light');
    const darkIcon = document.querySelector('.theme-icon-dark');

    if (theme === 'dark') {
        lightIcon?.classList.add('hidden');
        darkIcon?.classList.remove('hidden');
    } else {
        lightIcon?.classList.remove('hidden');
        darkIcon?.classList.add('hidden');
    }
}

// Respect system preference
if (!localStorage.getItem('theme')) {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const systemTheme = prefersDark ? 'dark' : 'light';
    htmlElement.setAttribute('data-theme', systemTheme);
    updateThemeIcon(systemTheme);
}
```

### 3.2 Update CBT Components

**For each file in `cbt_tools/components/`**:

1. Ensure component inherits theme from parent
2. Replace hardcoded colors with CSS variables
3. Test component in both light and dark modes
4. Verify text remains readable in both themes

### 3.3 Update Stylesheets

**Tasks**:
1. Consolidate theme-related CSS into `theme-variables.css`
2. Update `ux-enhancements.css` to use new variables
3. Remove duplicate color definitions
4. Ensure all colors use CSS variables

---

## ✅ Phase 4: Accessibility & Contrast Compliance

### 4.1 WCAG Contrast Requirements

**Standards to meet**:
- **Normal text (< 18pt)**: 4.5:1 contrast ratio (AA) or 7:1 (AAA)
- **Large text (≥ 18pt)**: 3:1 contrast ratio (AA) or 4.5:1 (AAA)
- **Interactive elements**: 3:1 against background

### 4.2 Automated Contrast Checking

**Create**: `check_contrast.py`

```python
#!/usr/bin/env python3
"""
WCAG 2.1 Contrast Checker for Healing Space UK
Validates all color combinations meet AA/AAA standards
"""

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def relative_luminance(rgb):
    """Calculate relative luminance of RGB color"""
    def adjust(channel):
        channel = channel / 255.0
        if channel <= 0.03928:
            return channel / 12.92
        return ((channel + 0.055) / 1.055) ** 2.4

    r, g, b = [adjust(c) for c in rgb]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast_ratio(color1, color2):
    """Calculate contrast ratio between two colors"""
    lum1 = relative_luminance(hex_to_rgb(color1))
    lum2 = relative_luminance(hex_to_rgb(color2))

    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)

    return (lighter + 0.05) / (darker + 0.05)

def check_wcag_compliance(ratio, level='AA', size='normal'):
    """Check if contrast ratio meets WCAG requirements"""
    requirements = {
        'AA': {'normal': 4.5, 'large': 3.0},
        'AAA': {'normal': 7.0, 'large': 4.5}
    }
    return ratio >= requirements[level][size]

# Test color combinations
light_theme = {
    'bg': '#ffffff',
    'text-primary': '#1a202c',
    'text-secondary': '#4a5568',
    'interactive-primary': '#667eea',
}

dark_theme = {
    'bg': '#1a202c',
    'text-primary': '#f7fafc',
    'text-secondary': '#e2e8f0',
    'interactive-primary': '#667eea',
}

print("=== LIGHT THEME CONTRAST RATIOS ===\n")
for text_name, text_color in [(k, v) for k, v in light_theme.items() if k != 'bg']:
    ratio = contrast_ratio(text_color, light_theme['bg'])
    aa = check_wcag_compliance(ratio, 'AA', 'normal')
    aaa = check_wcag_compliance(ratio, 'AAA', 'normal')
    status = '✅ PASS' if aa else '❌ FAIL'
    print(f"{text_name}: {ratio:.2f}:1 {status} (AA: {aa}, AAA: {aaa})")

print("\n=== DARK THEME CONTRAST RATIOS ===\n")
for text_name, text_color in [(k, v) for k, v in dark_theme.items() if k != 'bg']:
    ratio = contrast_ratio(text_color, dark_theme['bg'])
    aa = check_wcag_compliance(ratio, 'AA', 'normal')
    aaa = check_wcag_compliance(ratio, 'AAA', 'normal')
    status = '✅ PASS' if aa else '❌ FAIL'
    print(f"{text_name}: {ratio:.2f}:1 {status} (AA: {aa}, AAA: {aaa})")
```

**Run**:
```bash
python3 check_contrast.py
```

**Fix any failing combinations** by adjusting color values until all pass AA minimum.

### 4.3 Manual Testing Checklist

**Test in both themes**:
- [ ] All text is readable
- [ ] Buttons have clear states (hover, focus, active)
- [ ] Form inputs are clearly defined
- [ ] Error/success messages stand out
- [ ] Links are distinguishable
- [ ] Modal overlays don't obscure critical info
- [ ] Charts/graphs use colorblind-friendly palettes

---

## 🧪 Phase 5: Testing

### 5.1 Visual Testing

**Test each page**:
1. Load in light mode - verify appearance
2. Toggle to dark mode - verify transition
3. Refresh page - verify theme persists
4. Test on mobile viewport
5. Test with system dark mode preference

**Pages to test**:
- [ ] Landing page (`/`)
- [ ] Patient dashboard
- [ ] Clinician dashboard
- [ ] Messaging interface
- [ ] Admin panels
- [ ] All 15 CBT components
- [ ] Diagnostic page
- [ ] Developer dashboard

### 5.2 Accessibility Testing

**Tools**:
- Browser DevTools Lighthouse audit
- axe DevTools extension
- WAVE browser extension
- Keyboard navigation testing

**Run**:
```bash
# Install Pa11y for automated accessibility testing
npm install -g pa11y

# Test main pages
pa11y http://localhost:5000
pa11y http://localhost:5000/patient-dashboard
```

### 5.3 Functional Testing

**Verify**:
- [ ] Theme toggle works on all pages
- [ ] Theme preference persists across sessions
- [ ] Theme applies to dynamically loaded content
- [ ] Modals/popups respect theme
- [ ] Charts update colors when theme changes
- [ ] Print styles use light theme regardless

---

## 📊 Phase 6: Documentation

### 6.1 Create Theme Usage Guide

**Create**: `DOCUMENTATION/6-DEVELOPMENT/Theme-System-Guide.md`

**Include**:
- Available CSS variables
- How to add new themed components
- Dark mode best practices
- Contrast checking workflow
- How to test theme changes

### 6.2 Update Component Documentation

**For each component**, document:
- Which CSS variables it uses
- Any theme-specific behavior
- Accessibility considerations

---

## 🚀 Phase 7: Deployment

### 7.1 Pre-Deployment Checklist

- [ ] All contrast ratios meet WCAG AA
- [ ] Theme toggle present on all pages
- [ ] Theme persistence works
- [ ] No console errors
- [ ] Mobile responsive in both themes
- [ ] Performance impact < 50ms
- [ ] Lighthouse accessibility score > 90

### 7.2 Rollout Plan

1. **Test environment**: Deploy and verify
2. **User testing**: Get feedback from 2-3 test users
3. **Production**: Deploy with feature flag
4. **Monitor**: Check for theme-related bugs
5. **Iterate**: Address any issues

---

## 📝 Deliverables

Upon completion, provide:

1. **UI_AUDIT_REPORT.md** - Initial audit findings
2. **theme-variables.css** - Complete design system
3. **components.css** - Reusable component styles
4. **check_contrast.py** - Contrast validation script
5. **Theme-System-Guide.md** - Developer documentation
6. **THEME_IMPLEMENTATION_SUMMARY.md** - What was changed and why

---

## 🎯 Success Criteria

✅ **All pages support dark/light themes**
✅ **All text meets WCAG 2.1 AA contrast ratios**
✅ **Theme preference persists across sessions**
✅ **No hardcoded colors remain**
✅ **Mobile responsive in both themes**
✅ **Lighthouse accessibility score > 90**
✅ **User can toggle theme from any page**
✅ **Theme system documented for future developers**

---

## 💡 Tips for Excellence

1. **Use system preferences**: Detect `prefers-color-scheme` on first visit
2. **Smooth transitions**: Use CSS transitions when changing themes
3. **Test with real users**: Especially those who use dark mode regularly
4. **Consider images**: Ensure logos/images work in both themes
5. **Chart colors**: Use theme-aware color schemes for Chart.js
6. **Focus states**: Ensure visible in both themes
7. **Loading states**: Theme skeleton screens and spinners
8. **Print styles**: Always use light theme for printing

---

## 🔧 Maintenance

**Regular tasks**:
- [ ] Run contrast checker monthly
- [ ] Test new components in both themes before merging
- [ ] Update theme guide when adding new variables
- [ ] Gather user feedback on theme experience

---

## 📚 Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [CSS Variables MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)
- [Dark Mode Best Practices](https://web.dev/prefers-color-scheme/)

---

**End of Prompt - Ready for Execution**

Save this file and run it whenever you need to audit or improve the theme system.
