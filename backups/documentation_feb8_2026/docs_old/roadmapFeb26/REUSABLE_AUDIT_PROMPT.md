# THE ULTIMATE APP AUDIT PROMPT
## Copy-Paste This to Iterate Toward Perfection

---

## HOW TO USE THIS DOCUMENT

1. Copy the prompt below into a new Claude Code conversation (or any AI assistant with codebase access)
2. Let it run the full audit
3. Review the output against the previous MASTER_ROADMAP.md
4. Mark completed items, identify new issues, reprioritize
5. Repeat every 1-2 weeks (or after each major milestone)
6. Each iteration will catch things the last one missed and validate fixes

---

## THE PROMPT

```
You are a world-class full-stack developer, clinical systems architect, cybersecurity auditor, GDPR/NHS compliance specialist, mental health UX expert, and accessibility consultant. You are conducting an iterative deep audit of a mental health therapy application called "Healing Space UK."

CONTEXT:
- This is a clinical mental health web application (Flask + PostgreSQL + Groq AI)
- It serves patients AND clinicians with therapy chat, mood tracking, C-SSRS suicide risk assessment, CBT tools, a virtual pet, community features, and a clinician dashboard
- Target deployment: UK NHS / University setting
- Must comply with: UK GDPR, NHS Digital Standards, WCAG 2.1 AA, DCB0129 Clinical Safety, NICE guidelines
- Previous audit roadmap exists at: docs/MASTER_ROADMAP.md

YOUR TASK - EXECUTE ALL 7 PHASES:

=== PHASE 1: STRUCTURAL SCAN ===
- Map every file in the project (exclude node_modules, .git, venv, __pycache__)
- Identify: source code files, config files, documentation, test files, dead/orphaned files
- Count lines of code per file
- Flag any files that shouldn't be in the repo (secrets, credentials, large binaries, personal data)

=== PHASE 2: SECURITY AUDIT ===
Read every source file and check for:
- Authentication & authorization flaws (bypass, privilege escalation, IDOR)
- Injection vulnerabilities (SQL injection, XSS, command injection, prompt injection)
- Session management issues (weak keys, long lifetimes, no rotation, no timeout)
- CSRF protection gaps (missing decorators, DEBUG bypasses)
- Rate limiting gaps (unprotected endpoints: login, registration, password reset, clinical)
- Hardcoded secrets, credentials, API keys, debug backdoors
- Unsafe error handling (exception details exposed, silent failures)
- Input validation gaps (missing type/range/format checks)
- Cryptographic issues (weak algorithms, hardcoded salts, key management)
- Dependency vulnerabilities (outdated packages, unnecessary dependencies)
- CORS misconfiguration
- File upload vulnerabilities
- Insecure direct object references

For EACH issue found:
- Exact file and line number
- Severity (CRITICAL / HIGH / MEDIUM / LOW)
- Attack scenario (how it could be exploited)
- Recommended fix (specific code change)

=== PHASE 3: CLINICAL SAFETY AUDIT ===
- Review the AI therapy system: prompt construction, safety guardrails, response filtering
- Review C-SSRS implementation: scoring accuracy, clinical protocol compliance, alert triggers
- Review crisis response flow: detection → alert → notification → escalation → resolution
- Review safety planning: completeness, enforcement, clinician notification
- Review risk monitoring: keyword detection, pattern analysis, false positive/negative rates
- Check: Does the system ever give medical advice? Does it know its boundaries?
- Check: Can a user in crisis reach help within 60 seconds from any screen?
- Check: Are emergency numbers visible and clickable on every high-risk screen?

=== PHASE 4: FRONTEND UX/UI/ACCESSIBILITY AUDIT ===
- Map every screen, tab, modal, and user flow
- WCAG 2.1 AA compliance check: ARIA labels, keyboard navigation, focus management, color contrast, semantic HTML, skip links, screen reader compatibility
- Mobile responsiveness: test at 320px, 375px, 768px, 1024px, 1440px
- Trauma-informed design: calming colors, user agency, content warnings, grounding tools accessibility, pacing control, safe exit options
- Error state UX: are errors gentle and helpful? Do they provide next steps?
- Loading state UX: are loading states calming, not anxiety-inducing?
- Performance: page load time, bundle size, memory leaks, event listener cleanup
- Information architecture: can users find what they need in <3 clicks?

=== PHASE 5: DATA PROTECTION & COMPLIANCE AUDIT ===
- UK GDPR: lawful basis, consent mechanism, data subject rights (access, deletion, portability, objection), data minimization, storage limitation, breach notification
- NHS Digital Standards: DCB0129 Clinical Safety, DSPT, IG Toolkit
- Data retention: what data is stored, how long, is auto-deletion implemented?
- Encryption: at rest (field-level for sensitive data), in transit (TLS)
- Audit logging: who accessed what data when, tamper-evident, retention
- Cross-border data transfer: where is data processed/stored?
- Third-party data sharing: what goes to Groq API? Is it disclosed?
- Consent tracking: granular consent for each data use (therapy, training, analytics, research)

=== PHASE 6: ARCHITECTURE & CODE QUALITY AUDIT ===
- Code organization: monolith vs modular, separation of concerns, DRY violations
- Database design: normalization, indexing, foreign keys, naming consistency, migration strategy
- API design: RESTfulness, consistency, documentation, versioning
- Error handling patterns: consistent approach, structured logging, monitoring hooks
- Test coverage: which features have tests, which don't, coverage percentage estimate
- Dead code: unused files, functions, imports, commented-out code
- Technical debt: shortcuts taken, TODO/FIXME/HACK comments, workarounds
- Scalability: connection pooling, query optimization, caching, pagination
- Documentation accuracy: does documentation match actual implementation?

=== PHASE 7: COMPETITIVE ANALYSIS & INNOVATION ===
Think about what would make this THE BEST mental health app in the world:
- What do Headspace, Calm, Woebot, Wysa, BetterHelp, Talkspace do that this doesn't?
- What clinical tools are missing that therapists actually need?
- What engagement mechanics keep users coming back without being manipulative?
- What AI capabilities are emerging that could transform therapy support?
- What accessibility features would make this usable by the widest possible population?
- What integration points would make this indispensable in a clinical setting?
- What data insights could genuinely improve patient outcomes?
- What would make a university or NHS trust say "we MUST have this"?

=== OUTPUT FORMAT ===

Produce TWO documents:

DOCUMENT 1: Updated MASTER_ROADMAP.md
- Priority-ordered (Tier 0-6) with specific file:line references
- Each item: description, file location, risk level, effort estimate, recommended fix
- Mark items from previous roadmap as: DONE / IN PROGRESS / NOT STARTED / NEW ISSUE
- Track progress percentage per tier
- Updated grand total estimate

DOCUMENT 2: New (or udpated) AUDIT_DELTA_REPORT.md
- What changed since last audit?
- New issues discovered
- Issues that got worse
- Issues that were fixed (verify the fix is correct)
- Regressions introduced
- Updated risk assessment
- Recommendation for next sprint focus

=== IMPORTANT RULES ===
1. READ EVERY FILE. Do not skip files because they look unimportant.
2. Be SPECIFIC. "Security issue in api.py" is useless. "SQL injection via f-string interpolation in INTERVAL clause at api.py:10248" is useful.
3. Be HONEST. If something is broken, say it's broken. Don't soften findings.
4. Think like an ATTACKER for security. Think like a PATIENT IN CRISIS for UX. Think like an NHS AUDITOR for compliance. Think like a SENIOR DEVELOPER for code quality.
5. Cross-reference documentation claims against actual code. Flag every contradiction.
6. Consider the CLINICAL CONTEXT. A bug in a therapy app isn't like a bug in a todo app. People's lives may depend on this working correctly.
7. Don't just find problems - propose specific, actionable solutions with effort estimates.
```

---

## ITERATION TRACKING TABLE

Use this table to track each audit cycle:

| Audit # | Date | Tier 0 Issues | Tier 1 Issues | Tier 2 Issues | Total Issues | Fixed Since Last | New Since Last |
|---------|------|---------------|---------------|---------------|--------------|-----------------|----------------|
| 1 | Feb 8, 2026 | 7 | 10 | 7 | 60+ | N/A (baseline) | N/A (baseline) |
| 2 | | | | | | | |
| 3 | | | | | | | |
| 4 | | | | | | | |
| 5 | | | | | | | |

---

## REFINEMENT TIPS

After each audit cycle:

1. **Challenge assumptions**: Ask the AI "What did you miss?" and "What would a hostile penetration tester find?"
2. **Shift perspective**: Run the audit prompt with added context like "Focus specifically on what a suicidal 19-year-old university student would experience" or "Audit as if you're the NHS Digital assessment team"
3. **Add domain specifics**: After each cycle, append new requirements you've learned about to the prompt (e.g., specific NHS trust requirements, university ethics board feedback)
4. **Test the fixes**: After implementing fixes from one audit, the next audit should verify they were done correctly
5. **Expand scope**: Each cycle, add one new audit dimension (e.g., "Audit the deployment pipeline", "Audit the backup/restore process", "Audit the onboarding flow for new clinicians")
6. **Benchmark against competitors**: Periodically add "Compare feature X against [specific competitor] and identify gaps"
7. **Include user feedback**: If you have beta user feedback, include it as context for the next audit

---

## SPECIALIZED FOLLOW-UP PROMPTS

Use these targeted prompts between full audits for deep-dives:

### Security Penetration Test
```
Act as a hostile penetration tester. You have access to the full source code of this mental health application. Your goal is to: (1) Access another user's therapy chat history, (2) Escalate a patient account to clinician privileges, (3) Manipulate the AI to give harmful advice, (4) Extract the database credentials, (5) Cause a denial of service. For each attack, document the exact steps, affected files/endpoints, and whether it succeeds or fails. Then provide the fix.
```

### Crisis UX Walkthrough
```
You are a 19-year-old university student experiencing suicidal thoughts at 2am. You open Healing Space for the first time. Walk through every screen you would see. Document: (1) How many seconds until you see a crisis helpline number, (2) How many clicks to reach a human, (3) Does the AI say anything that could make things worse, (4) Is the C-SSRS assessment approachable or clinical/intimidating, (5) What happens if you close the app mid-assessment, (6) Does the app follow you up. Be brutally honest about the experience.
```

### NHS Compliance Readiness
```
You are an NHS Digital Assessment Team member evaluating this application for deployment in a university counseling service. Using the DCB0129 Clinical Safety standard and the NHS Data Security and Protection Toolkit (DSPT), assess: (1) Clinical safety case completeness, (2) Information governance maturity, (3) Technical security controls, (4) Incident response capability, (5) Staff training requirements, (6) Patient consent and rights management. Score each area 1-5 and provide the specific evidence gaps that would prevent approval.
```

### Code Quality Deep-Dive
```
You are a senior software architect reviewing this codebase for a team that will need to maintain it for 5+ years. Assess: (1) Can a new developer understand the code in <1 day? (2) Can features be added without breaking existing ones? (3) Is the test suite trustworthy? (4) Are there ticking time bombs (race conditions, memory leaks, data corruption risks)? (5) What would you refactor FIRST and why? Provide specific refactoring plans with before/after code examples.
```

### Accessibility Compliance
```
You are a WCAG 2.1 AA auditor testing this application with: (1) Screen reader only (no mouse, no visual), (2) Keyboard only (no mouse), (3) High contrast mode, (4) 200% zoom, (5) Reduced motion preference. For each mode, attempt to: register, log a mood, chat with the AI, complete a C-SSRS assessment, read community posts, and view insights. Document every failure with WCAG criterion reference (e.g., "1.1.1 Non-text Content: Image at line X missing alt text").
```

---

## THE ULTIMATE GOAL

After 5-10 iterations of this audit cycle, you will have:

1. **Zero known critical/high security vulnerabilities**
2. **Full NHS compliance documentation with sign-offs**
3. **WCAG 2.1 AA accessibility certification**
4. **>95% test coverage on clinical features**
5. **Clinical validation of all assessment tools**
6. **A codebase any developer can understand in a day**
7. **A UX that a person in crisis would find genuinely helpful**
8. **Features that make NHS trusts and universities compete to deploy it**
9. **An architecture that scales to 100,000+ users**
10. **The confidence to say: "This app saves lives, and I can prove it."**

---

*This prompt was designed to be used iteratively. Each cycle catches things the previous one missed, validates fixes, and raises the bar. The app gets better every single time you run it.*
