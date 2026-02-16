# Theme System Guide

**Version**: 2.0.0
**Date**: February 16, 2026
**For**: Developers working on Healing Space UK

---

## Overview

Healing Space UK uses a comprehensive design system with built-in dark/light theme support. This guide explains how to use the system effectively.

---

## Quick Start

### Using CSS Variables

Always use CSS variables from our design system instead of hardcoded values:

```css
/* ❌ DON'T do this */
.my-component {
    background: #ffffff;
    color: #333333;
    border: 1px solid #e0e0e0;
}

/* ✅ DO this */
.my-component {
    background: var(--bg-primary);
    color: var(--text-primary);
    border: 1px solid var(--border-primary);
}
```

### Using Component Classes

Leverage pre-built component classes:

```html
<!-- ❌ DON'T create custom styles -->
<button style="background: #667eea; color: white; padding: 8px 24px;">
    Submit
</button>

<!-- ✅ DO use component classes -->
<button class="btn btn-primary">
    Submit
</button>
```

---

## Available CSS Variables

### Colors

#### Background Colors
```css
--bg-primary       /* Main background */
--bg-secondary     /* Secondary surfaces */
--bg-tertiary      /* Tertiary surfaces */
--bg-elevated      /* Cards, modals */
--bg-input         /* Form inputs */
--bg-hover         /* Hover states */
--bg-active        /* Active states */
--bg-sidebar       /* Sidebar background */
```

#### Text Colors
```css
--text-primary     /* Main text */
--text-secondary   /* Secondary text */
--text-tertiary    /* Tertiary text */
--text-muted       /* Muted/placeholder text */
--text-inverse     /* Text on dark backgrounds */
--text-link        /* Hyperlinks */
--text-link-hover  /* Link hover state */
```

#### Border Colors
```css
--border-primary   /* Default borders */
--border-secondary /* Secondary borders */
--border-focus     /* Focus states */
--border-error     /* Error states */
--border-success   /* Success states */
```

#### Status Colors
```css
--status-success       /* Success text/icons */
--status-success-bg    /* Success backgrounds */
--status-success-border /* Success borders */

--status-warning       /* Warning text/icons */
--status-warning-bg    /* Warning backgrounds */
--status-warning-border /* Warning borders */

--status-error         /* Error text/icons */
--status-error-bg      /* Error backgrounds */
--status-error-border  /* Error borders */

--status-info          /* Info text/icons */
--status-info-bg       /* Info backgrounds */
--status-info-border   /* Info borders */
```

#### Interactive Colors
```css
--interactive-primary        /* Primary buttons */
--interactive-primary-hover  /* Primary hover */
--interactive-primary-active /* Primary active */
--interactive-secondary      /* Secondary buttons */
--interactive-tertiary       /* Tertiary buttons */
```

### Spacing
```css
--space-xs    /* 4px */
--space-sm    /* 8px */
--space-md    /* 16px */
--space-lg    /* 24px */
--space-xl    /* 32px */
--space-2xl   /* 48px */
--space-3xl   /* 64px */
```

### Typography
```css
--font-size-xs     /* 12px */
--font-size-sm     /* 14px */
--font-size-base   /* 16px */
--font-size-lg     /* 18px */
--font-size-xl     /* 20px */
--font-size-2xl    /* 24px */
--font-size-3xl    /* 30px */

--font-weight-normal    /* 400 */
--font-weight-medium    /* 500 */
--font-weight-semibold  /* 600 */
--font-weight-bold      /* 700 */
```

### Border Radius
```css
--radius-sm     /* 4px */
--radius-md     /* 8px */
--radius-lg     /* 12px */
--radius-xl     /* 16px */
--radius-2xl    /* 24px */
--radius-full   /* 9999px - circles */
```

### Shadows
```css
--shadow-xs   /* Subtle shadow */
--shadow-sm   /* Small shadow */
--shadow-md   /* Medium shadow */
--shadow-lg   /* Large shadow */
--shadow-xl   /* Extra large shadow */
--shadow-2xl  /* Massive shadow */
```

---

## Component Classes

### Buttons

```html
<!-- Primary button -->
<button class="btn btn-primary">Primary Action</button>

<!-- Secondary button -->
<button class="btn btn-secondary">Secondary Action</button>

<!-- Tertiary button -->
<button class="btn btn-tertiary">Tertiary Action</button>

<!-- Danger button -->
<button class="btn btn-danger">Delete</button>

<!-- Success button -->
<button class="btn btn-success">Save</button>

<!-- Sizes -->
<button class="btn btn-primary btn-sm">Small</button>
<button class="btn btn-primary">Regular</button>
<button class="btn btn-primary btn-lg">Large</button>

<!-- Disabled -->
<button class="btn btn-primary" disabled>Disabled</button>
```

### Cards

```html
<!-- Basic card -->
<div class="card">
    <p>Card content</p>
</div>

<!-- Card with header and footer -->
<div class="card">
    <div class="card-header">
        <h3 class="card-title">Card Title</h3>
    </div>
    <div class="card-body">
        <p>Main content goes here</p>
    </div>
    <div class="card-footer">
        <button class="btn btn-primary">Action</button>
    </div>
</div>

<!-- Interactive card (clickable) -->
<div class="card card-interactive" onclick="handleClick()">
    <p>Click me</p>
</div>
```

### Forms

```html
<!-- Form group -->
<div class="form-group">
    <label class="form-label" for="username">Username</label>
    <input type="text" id="username" class="input" placeholder="Enter username">
    <span class="form-help">Choose a unique username</span>
</div>

<!-- With error -->
<div class="form-group">
    <label class="form-label" for="email">Email</label>
    <input type="email" id="email" class="input input-error" placeholder="you@example.com">
    <span class="form-error">Please enter a valid email</span>
</div>

<!-- Textarea -->
<div class="form-group">
    <label class="form-label" for="message">Message</label>
    <textarea id="message" class="textarea" rows="4"></textarea>
</div>

<!-- Select -->
<div class="form-group">
    <label class="form-label" for="country">Country</label>
    <select id="country" class="select">
        <option>Select a country</option>
        <option>United Kingdom</option>
        <option>United States</option>
    </select>
</div>
```

### Alerts

```html
<!-- Success alert -->
<div class="alert alert-success">
    Operation completed successfully!
</div>

<!-- Warning alert -->
<div class="alert alert-warning">
    Please review this information carefully.
</div>

<!-- Error alert -->
<div class="alert alert-error">
    An error occurred. Please try again.
</div>

<!-- Info alert -->
<div class="alert alert-info">
    This is informational content.
</div>
```

### Badges

```html
<span class="badge badge-primary">Primary</span>
<span class="badge badge-success">Active</span>
<span class="badge badge-warning">Pending</span>
<span class="badge badge-error">Error</span>
<span class="badge badge-info">Info</span>
```

### Modals

```html
<!-- Modal backdrop -->
<div class="modal-backdrop">
    <!-- Modal content -->
    <div class="modal">
        <div class="modal-header">
            <h2 class="modal-title">Modal Title</h2>
        </div>
        <div class="modal-body">
            <p>Modal content goes here...</p>
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary">Cancel</button>
            <button class="btn btn-primary">Confirm</button>
        </div>
    </div>
</div>
```

### Loading States

```html
<!-- Spinner -->
<div class="spinner"></div>

<!-- Skeleton loader -->
<div class="skeleton" style="width: 200px; height: 20px;"></div>
```

---

## Theme Toggle Implementation

The theme system automatically works across the app. Theme state is managed via the `data-theme` attribute:

```javascript
// Get current theme
const currentTheme = document.documentElement.getAttribute('data-theme');
// Returns: 'dark' or null (light is default)

// Set dark theme
document.documentElement.setAttribute('data-theme', 'dark');

// Set light theme
document.documentElement.removeAttribute('data-theme');

// Toggle theme
const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
if (isDark) {
    document.documentElement.removeAttribute('data-theme');
} else {
    document.documentElement.setAttribute('data-theme', 'dark');
}

// Persist theme
localStorage.setItem('theme', isDark ? 'light' : 'dark');
```

---

## Adding New Components

### Step 1: Define Using Variables

```css
.my-new-component {
    /* Use existing variables */
    background: var(--bg-elevated);
    color: var(--text-primary);
    border: 1px solid var(--border-primary);
    padding: var(--space-md);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
}
```

### Step 2: Add Hover/Active States

```css
.my-new-component:hover {
    background: var(--bg-hover);
    box-shadow: var(--shadow-md);
}

.my-new-component:active {
    background: var(--bg-active);
}
```

### Step 3: Test in Both Themes

1. View in light mode
2. Toggle to dark mode
3. Verify all states work correctly
4. Check contrast using `check_contrast.py` if adding new colors

---

## Testing Checklist

Before committing theme-related changes:

- [ ] Component looks good in light mode
- [ ] Component looks good in dark mode
- [ ] All interactive states work (hover, active, focus)
- [ ] Text is readable in both themes
- [ ] No hardcoded colors used
- [ ] Spacing uses variables
- [ ] Transitions are smooth
- [ ] Mobile responsive
- [ ] Passes `check_contrast.py` if new colors added

---

## Common Patterns

### Pattern: Status Indicator

```html
<div class="card" style="border-left: 4px solid var(--status-success);">
    <div class="card-body">
        <h4 style="color: var(--status-success);">Success</h4>
        <p>Operation completed successfully</p>
    </div>
</div>
```

### Pattern: Split Layout

```css
.split-layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-lg);
    padding: var(--space-xl);
}
```

### Pattern: Icon Button

```html
<button class="btn btn-tertiary" aria-label="Settings">
    ⚙️
</button>
```

---

## Accessibility Guidelines

### Always Provide

1. **Focus states**: Use `:focus-visible` for keyboard navigation
2. **ARIA labels**: For icon-only buttons and links
3. **Color independence**: Don't rely solely on color to convey meaning
4. **Sufficient contrast**: Use `check_contrast.py` to verify

### Example: Accessible Button

```html
<button
    class="btn btn-primary"
    aria-label="Save your progress"
    aria-describedby="save-help"
>
    💾 Save
</button>
<span id="save-help" class="sr-only">
    This will save all your changes
</span>
```

---

## Troubleshooting

### Issue: Colors not changing with theme

**Solution**: Make sure you're using CSS variables, not hardcoded colors

```css
/* ❌ Wrong - won't change with theme */
.element {
    color: #333;
}

/* ✅ Correct - will adapt to theme */
.element {
    color: var(--text-primary);
}
```

### Issue: New color doesn't have enough contrast

**Solution**: Run the contrast checker

```bash
python3 check_contrast.py
```

Then adjust your color to meet AA standards (4.5:1 for normal text).

### Issue: Theme not persisting

**Solution**: Ensure localStorage is being used

```javascript
// Save theme
localStorage.setItem('theme', 'dark');

// Load theme on page load
const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
}
```

---

## Best Practices

1. ✅ **Always use CSS variables** for colors
2. ✅ **Use component classes** when available
3. ✅ **Test in both themes** before committing
4. ✅ **Run contrast checker** for new colors
5. ✅ **Follow spacing system** (don't use arbitrary values)
6. ✅ **Keep accessibility in mind** (ARIA, contrast, focus)
7. ✅ **Document new patterns** if creating reusable components

---

## Resources

- **Main Styles**: `static/css/theme-variables.css`
- **Components**: `static/css/components.css`
- **Contrast Checker**: `check_contrast.py`
- **Full Guide**: `DOCUMENTATION/Prompts/UI_MODERNIZATION_AND_THEMING.md`

---

**Need help?** Check the full implementation summary in `THEME_IMPLEMENTATION_SUMMARY.md`
