# QUICK REFERENCE CHEAT SHEET

**Healing Space - Mental Health Therapy AI**  
**One-page project overview for fast lookup**

---

## 🎯 PROJECT ELEVATOR PITCH

**What**: Flask REST API + Tkinter desktop GUI for AI-powered mental health therapy  
**Status**: Phase 2 security hardening complete, Phase 3 (messaging) starting Feb 5  
**Team**: 1 primary developer, security reviewer, QA tester  
**When**: Started Jan 5, 2026 | MVP target Jun 30, 2026 | v1.0 by Dec 31, 2026  
**Budget**: ~$18,100 annual (mostly labor @ $100/hr)

---

## 📊 CURRENT METRICS

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Security CVSS | 1.6 | < 2.0 | ✅ |
| Test Coverage | 72% | > 60% | ✅ |
| API Response | 145ms | < 200ms | ✅ |
| Uptime | 99.8% | > 99% | ✅ |
| Active Users | 5 | 10-20 | 📈 |
| Vulnerabilities | 0 critical | 0 | ✅ |

---

## 🎯 PHASES AT A GLANCE

| Phase | Status | Effort | Impact |
|-------|--------|--------|--------|
| 1: Auth & Sessions | ✅ Done | 6.5 hrs | CVSS 8.5→4.1 |
| 2: Input Validation | ✅ Done | 3 hrs | CVSS 4.1→1.6 |
| 3: Messaging | ⏳ Next | 8-10 hrs | Enable team comms |
| 4: DB Constraints | 📅 Mar | 8-10 hrs | Data integrity |
| 5: Advanced Logging | 📅 Mar | 10-12 hrs | Observability |
| 6: Performance | 📅 Mar | 12-16 hrs | Scaling |
| 7: Features | 📅 Apr+ | 20+ hrs | Advanced features |

---

## 🚀 THIS WEEK'S PRIORITIES

### ✅ Completed (Feb 4)
- Phase 2 security hardening (CVSS 4.1 → 1.6)
- All 18 critical vulnerabilities fixed
- Input validation on all endpoints
- CSRF protection enabled

### ⏳ In Progress This Week
- Phase 3 messaging system design
- Testing & QA for Phase 2 fixes
- Documentation updates

### 📅 Starting Next Week (Feb 5+)
- Phase 3: Internal messaging implementation
- Dev ↔ Clinician ↔ User messaging
- No user-to-clinician direct messaging

### ⚠️ Blockers / Decisions Needed
- **Messaging scope**: Minimal vs. Balanced vs. Full (affects 6-10 hour effort)
- **DB migration**: When to migrate SQLite → PostgreSQL?
- **E2E testing**: Which framework? (Playwright vs. Cypress)

---

## 🏗️ ARCHITECTURE

### Backend (Flask API - production)
```
api.py (65+ endpoints)
├── Auth: Login, register, 2FA, password reset
├── Therapy: Chat, mood, clinical notes
├── Gamification: Pet game, rewards
├── GDPR: Data export, anonymization
├── Admin: User management, audits
└── Integration: Groq LLM, webhooks
```

### Frontend (Desktop GUI - legacy)
```
legacy_desktop/main.py (Tkinter)
├── Login & Registration
├── Chat interface
├── Mood tracking
├── Pet game
└── User settings
```

### Databases
```
therapist_app.db    - Main app data (users, chat, mood, clinical)
pet_game.db         - Gamification state
ai_training_data.db - GDPR-compliant training data
```

---

## 🔐 SECURITY POSTURE

### Current State: CVSS 1.6 (LOW RISK)
✅ Session-based authentication (secure cookies)  
✅ Role-based access control (dev, clinician, user)  
✅ Argon2 password hashing (+ bcrypt + PBKDF2 fallback)  
✅ Fernet encryption (AES-128 + HMAC)  
✅ Input validation on all endpoints  
✅ CSRF token protection  
✅ Security headers (CSP, HSTS, X-Frame-Options)  
✅ Rate limiting for brute-force protection  
✅ Audit logging for compliance  

### Remaining Risks: MINIMAL
- [ ] OAuth2 (planned Phase 7)
- [ ] Two-factor authentication (planned Phase 7)
- [ ] Advanced intrusion detection (planned Phase 5)

---

## 📈 NEXT 30 DAYS

### Week 1 (Feb 5-11): Messaging System Design
- [ ] Finalize messaging scope (decision needed)
- [ ] Design database schema
- [ ] Plan API endpoints
- [ ] Set up testing framework

### Week 2 (Feb 12-18): Messaging Implementation
- [ ] Build message send/receive endpoints
- [ ] Implement role-based permissions
- [ ] Add conversation threading
- [ ] Write tests

### Week 3 (Feb 19-25): Testing & QA
- [ ] Complete test suite
- [ ] Security testing
- [ ] Integration testing
- [ ] Performance testing

### Week 4 (Feb 26-Mar 3): Phase 3 Completion
- [ ] Phase 3 finalization
- [ ] Documentation update
- [ ] Production deployment
- [ ] Phase 4 kickoff (DB constraints)

---

## 💰 RESOURCE ALLOCATION

### Time Budget (Annual)
- Phase 1-2 (Done): 9.5 hrs
- Phase 3-5: 28-34 hrs
- Phase 6-7: 40+ hrs
- Maintenance/Support: 20+ hrs
- **Total**: ~100-125 hrs (annual)

### Cost Breakdown
| Item | Cost | Notes |
|------|------|-------|
| Railway hosting | $7/mo | Base tier |
| API keys (Groq) | Free | Tier 1 |
| Domain | $0 | Using Railway domain |
| Other services | $0 | Built-in or free |
| **Monthly**: | ~$7 | Infrastructure |
| **Annual**: | ~$85 | + Labor costs |

### Labor (Estimated)
- Dev work: 100-125 hrs @ $100/hr = $10,000-12,500
- Security review: 10 hrs @ $150/hr = $1,500
- QA testing: 15 hrs @ $50/hr = $750
- **Total Labor**: ~$12,250-14,750
- **Total 2026**: ~$12,500-15,000

---

## 🔗 KEY LINKS

### Documentation Hub
- [project_management/README.md](project_management/README.md) - Navigation hub
- [project_management/ACTIVE_STATUS.md](project_management/ACTIVE_STATUS.md) - Daily status
- [project_management/ROADMAP.md](project_management/ROADMAP.md) - Detailed roadmap
- [project_management/DECISIONS.md](project_management/DECISIONS.md) - Open decisions
- [project_management/QUARTERLY_PLANNING.md](project_management/QUARTERLY_PLANNING.md) - Quarterly goals

### Code & Implementation
- [api.py](api.py) - Flask API (65+ endpoints)
- [legacy_desktop/main.py](legacy_desktop/main.py) - Desktop GUI
- [tests/to-do.md](tests/to-do.md) - Developer tasks

### Security & Audits
- [API_SECURITY_AUDIT_2026.md](API_SECURITY_AUDIT_2026.md) - Full audit
- [PHASE_2_COMPLETION_REPORT.md](PHASE_2_COMPLETION_REPORT.md) - Latest phase report

### Deployment
- [Procfile](Procfile) - Railway deployment config
- [RAILWAY_DEPLOYMENT_FIXES_2026.md](RAILWAY_DEPLOYMENT_FIXES_2026.md) - Deployment guide

---

## 🎯 DECISION POINTS (Action Required)

### ❓ Decision #1: Messaging System Scope
**Options**: Minimal (6h) | Balanced (8h) ⭐ | Full (10h)  
**Deadline**: Feb 5  
**Impact**: Messaging system feature completeness  
**Recommendation**: Balanced scope

### ❓ Decision #2: Database Migration Strategy
**Options**: Inline (risky) | Staged (safe) ⭐ | Rebuild (safest)  
**Deadline**: Feb 10  
**Impact**: Downtime risk during Phase 4  
**Recommendation**: Staged migration

### ❓ Decision #3: E2E Testing Framework
**Options**: Pytest | Playwright ⭐ | Cypress  
**Deadline**: Feb 12  
**Impact**: Test quality & DX  
**Recommendation**: Playwright

### ❓ Decision #4: Logging & Monitoring
**Options**: Native | ELK | Loki+Grafana ⭐ | Datadog  
**Deadline**: Feb 20  
**Impact**: Operational visibility  
**Recommendation**: Loki+Grafana

### ❓ Decision #5: SQLite → PostgreSQL Migration
**Options**: Stay | Migrate ⭐ for growth | Hybrid  
**Deadline**: Mar 1  
**Impact**: Long-term scalability  
**Recommendation**: Migrate in Phase 6

---

## ✅ QUICK CHECKLIST

### Starting a New Task?
- [ ] Check [project_management/ROADMAP.md](project_management/ROADMAP.md) for specifications
- [ ] Check [tests/to-do.md](tests/to-do.md) for task assignment
- [ ] Review [project_management/DECISIONS.md](project_management/DECISIONS.md) for dependencies
- [ ] Read related phase completion report
- [ ] Set up test file before coding

### Before Committing Code?
- [ ] Tests pass locally: `pytest -v tests/`
- [ ] Code follows style: PEP 8
- [ ] Security reviewed: No SQL injection, XSS, CSRF
- [ ] Documentation updated
- [ ] Version numbers incremented

### Before Deploying?
- [ ] All tests passing ✅
- [ ] Security audit passed ✅
- [ ] Changelog updated ✅
- [ ] Database backups created ✅
- [ ] Rollback plan documented ✅

---

## 📞 WHO TO ASK

| Question | Who | Reference |
|----------|-----|-----------|
| Project status | Lead | [ACTIVE_STATUS.md](project_management/ACTIVE_STATUS.md) |
| Next phase details | Dev | [ROADMAP.md](project_management/ROADMAP.md) |
| Open decisions | PM | [DECISIONS.md](project_management/DECISIONS.md) |
| Security questions | Security | [API_SECURITY_AUDIT_2026.md](API_SECURITY_AUDIT_2026.md) |
| Technical details | Dev | [api.py](api.py) or [PHASE_2_COMPLETION_REPORT.md](PHASE_2_COMPLETION_REPORT.md) |
| Testing help | QA | [tests/to-do.md](tests/to-do.md) |

---

## 🚨 COMMON ISSUES & SOLUTIONS

### API Not Starting?
```bash
# Check environment variables
export DEBUG=1
export ENCRYPTION_KEY="[44-char Fernet key]"
export PIN_SALT="[your PIN salt]"
export GROQ_API_KEY="[your API key]"

# Run API
python3 api.py
```

### Tests Failing?
```bash
# Run all tests with verbose output
pytest -v tests/

# Run specific test file
pytest -v tests/test_auth.py

# Run with debugging
pytest -v tests/ -s
```

### Database Issues?
```bash
# Check database integrity
sqlite3 therapist_app.db ".tables"

# Backup current database
cp therapist_app.db therapist_app.db.backup

# Reset for development
rm therapist_app.db
python3 api.py  # Creates fresh database
```

### Security Concerns?
Check [API_SECURITY_AUDIT_2026.md](API_SECURITY_AUDIT_2026.md) for:
- Vulnerability details
- Mitigation steps
- Testing procedures

---

## 📚 LEARNING RESOURCES

### Project Docs
- README.md - Project overview
- AI_TRAINING_GUIDE.md - AI model training
- CLINICIAN_FEATURES_2025.md - Feature docs
- 2FA_SETUP.md - Two-factor auth

### Code Examples
- [api.py](api.py) - See endpoints starting at line 200+
- [tests/](tests/) - See test patterns
- [legacy_desktop/main.py](legacy_desktop/main.py) - Desktop implementation

### External Resources
- Flask docs: https://flask.palletsprojects.com/
- SQLite docs: https://www.sqlite.org/docs.html
- Groq API: https://www.groq.com/
- Railway docs: https://docs.railway.app/

---

## 🎯 SUCCESS METRICS (How We Know We're Winning)

- ✅ Security CVSS < 1.0 (currently 1.6)
- ✅ Zero critical vulnerabilities (currently 0 ✓)
- ✅ Test coverage > 80% (currently 72%)
- ✅ API response time < 100ms (currently 145ms)
- ✅ Production uptime > 99.99% (currently 99.8%)
- ✅ Support 500+ concurrent users (planning)
- ✅ GDPR compliance certified
- ✅ SOC2 compliance (future)

---

## 📝 VERSION INFO

| Item | Value |
|------|-------|
| Project Start | Jan 5, 2026 |
| Current Date | Feb 4, 2026 |
| Current Phase | Phase 2 → 3 |
| Phase Progress | 22% Q1 complete |
| API Version | 1.0.0-beta |
| Database Schema | v2.5 (SQLite) |
| Security Level | CVSS 1.6 (LOW) |
| Production Status | ACTIVE |

---

**Last Updated**: February 4, 2026 | **Next Update**: February 11, 2026  
**Maintained by**: Development Team | **For Questions**: See contact list above

---

## 🔄 FEEDBACK & UPDATES

This cheat sheet is kept updated with:
- Weekly status updates (Mondays)
- Decision approvals (as needed)
- Phase completions (end of week)
- Metric updates (end of month)

**Found something outdated?** Update it or request an update!
