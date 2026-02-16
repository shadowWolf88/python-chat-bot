#!/usr/bin/env python3
"""
============================================
WCAG 2.1 Contrast Checker for Healing Space UK
============================================

Version: 1.0.0
Date: February 16, 2026
Purpose: Validate all color combinations meet AA/AAA standards
Standards: WCAG 2.1 Level AA minimum

Contrast Requirements:
- Normal text (< 18pt): 4.5:1 (AA) or 7:1 (AAA)
- Large text (≥ 18pt): 3:1 (AA) or 4.5:1 (AAA)
- UI components: 3:1 (AA)

============================================
"""

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def relative_luminance(rgb):
    """
    Calculate relative luminance of RGB color
    Formula from WCAG 2.1: https://www.w3.org/TR/WCAG21/#dfn-relative-luminance
    """
    def adjust(channel):
        channel = channel / 255.0
        if channel <= 0.03928:
            return channel / 12.92
        return ((channel + 0.055) / 1.055) ** 2.4

    r, g, b = [adjust(c) for c in rgb]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast_ratio(color1, color2):
    """
    Calculate contrast ratio between two colors
    Formula from WCAG 2.1: https://www.w3.org/TR/WCAG21/#dfn-contrast-ratio
    """
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

def print_test(name, fg, bg, size='normal'):
    """Print formatted test result"""
    ratio = contrast_ratio(fg, bg)
    aa = check_wcag_compliance(ratio, 'AA', size)
    aaa = check_wcag_compliance(ratio, 'AAA', size)

    status = '✅ PASS' if aa else '❌ FAIL'
    level = 'AAA' if aaa else ('AA' if aa else 'FAIL')

    print(f"{name:35} {fg:10} on {bg:10} = {ratio:5.2f}:1  {status} ({level})")
    return aa

# ============================================
# COLOR DEFINITIONS
# ============================================

light_theme = {
    'bg': '#ffffff',
    'bg-secondary': '#f8f9fa',
    'text-primary': '#1a202c',
    'text-secondary': '#4a5568',
    'text-tertiary': '#718096',
    'text-muted': '#a0aec0',
    'text-link': '#3182ce',
    'interactive-primary': '#667eea',
    'status-success': '#2f855a',
    'status-warning': '#d97706',
    'status-error': '#c53030',
    'status-info': '#2c5282',
}

dark_theme = {
    'bg': '#1a202c',
    'bg-secondary': '#2d3748',
    'text-primary': '#f7fafc',
    'text-secondary': '#e2e8f0',
    'text-tertiary': '#cbd5e0',
    'text-muted': '#a0aec0',
    'text-link': '#63b3ed',
    'interactive-primary': '#667eea',
    'status-success': '#48bb78',
    'status-warning': '#ed8936',
    'status-error': '#fc8181',
    'status-info': '#4299e1',
}

# ============================================
# RUN TESTS
# ============================================

print("=" * 100)
print("WCAG 2.1 Contrast Compliance Report - Healing Space UK")
print("=" * 100)
print()

# Light Theme Tests
print("=" * 100)
print("LIGHT THEME (Default)")
print("=" * 100)
print()

print("Text on Primary Background (#ffffff):")
print("-" * 100)
all_pass = True
all_pass &= print_test("Primary text", light_theme['text-primary'], light_theme['bg'])
all_pass &= print_test("Secondary text", light_theme['text-secondary'], light_theme['bg'])
all_pass &= print_test("Tertiary text", light_theme['text-tertiary'], light_theme['bg'])
all_pass &= print_test("Muted text (large only)", light_theme['text-muted'], light_theme['bg'], 'large')
all_pass &= print_test("Links", light_theme['text-link'], light_theme['bg'])
print()

print("Text on Secondary Background (#f8f9fa):")
print("-" * 100)
all_pass &= print_test("Primary text", light_theme['text-primary'], light_theme['bg-secondary'])
all_pass &= print_test("Secondary text", light_theme['text-secondary'], light_theme['bg-secondary'])
print()

print("Status Colors on White:")
print("-" * 100)
all_pass &= print_test("Success text", light_theme['status-success'], light_theme['bg'])
all_pass &= print_test("Warning text", light_theme['status-warning'], light_theme['bg'])
all_pass &= print_test("Error text", light_theme['status-error'], light_theme['bg'])
all_pass &= print_test("Info text", light_theme['status-info'], light_theme['bg'])
print()

print("Interactive Elements:")
print("-" * 100)
all_pass &= print_test("Primary button on white", light_theme['interactive-primary'], light_theme['bg'])
print()

# Dark Theme Tests
print("=" * 100)
print("DARK THEME")
print("=" * 100)
print()

print("Text on Primary Background (#1a202c):")
print("-" * 100)
all_pass &= print_test("Primary text", dark_theme['text-primary'], dark_theme['bg'])
all_pass &= print_test("Secondary text", dark_theme['text-secondary'], dark_theme['bg'])
all_pass &= print_test("Tertiary text", dark_theme['text-tertiary'], dark_theme['bg'])
all_pass &= print_test("Muted text (large only)", dark_theme['text-muted'], dark_theme['bg'], 'large')
all_pass &= print_test("Links", dark_theme['text-link'], dark_theme['bg'])
print()

print("Text on Secondary Background (#2d3748):")
print("-" * 100)
all_pass &= print_test("Primary text", dark_theme['text-primary'], dark_theme['bg-secondary'])
all_pass &= print_test("Secondary text", dark_theme['text-secondary'], dark_theme['bg-secondary'])
print()

print("Status Colors on Dark Background:")
print("-" * 100)
all_pass &= print_test("Success text", dark_theme['status-success'], dark_theme['bg'])
all_pass &= print_test("Warning text", dark_theme['status-warning'], dark_theme['bg'])
all_pass &= print_test("Error text", dark_theme['status-error'], dark_theme['bg'])
all_pass &= print_test("Info text", dark_theme['status-info'], dark_theme['bg'])
print()

print("Interactive Elements:")
print("-" * 100)
all_pass &= print_test("Primary button on dark", dark_theme['interactive-primary'], dark_theme['bg'])
print()

# Final Summary
print("=" * 100)
print("SUMMARY")
print("=" * 100)
if all_pass:
    print("✅ ALL TESTS PASSED - All color combinations meet WCAG 2.1 AA standards!")
else:
    print("❌ SOME TESTS FAILED - Review and adjust failing color combinations")
print("=" * 100)
