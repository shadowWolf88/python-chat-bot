# TIER 1.5-1.10 Visual Roadmap
**Timeline**: Feb 9-15, 2026 | **Effort**: 40 hours | **Status**: Ready to Start

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     TIER 1.5-1.10 SECURITY HARDENING                        │
│                                                                             │
│  Phase 1: Quick Wins (12 hrs) ──► Phase 2: Infrastructure (16 hrs) ──┐    │
│  ├─ 1.10: Salt (2h)             ├─ 1.9: DB Pooling (6h)            │    │
│  ├─ 1.7: Access (4h)            └─ 1.6: Error Handling (10h)       │    │
│  └─ 1.5: Sessions (6h)                                              │    │
│                                                                      │    │
│  Phase 3: Frontend (12 hrs) ◄───────────────────────────────────────┘    │
│  └─ 1.8: XSS Prevention (12h)                                             │
│                                                                             │
│  Total: 40 hours | 6-7 days | All critical security issues fixed           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📅 Week-by-Week Breakdown

```
WEEK OF FEB 9-15, 2026
═════════════════════════════════════════════════════════════════

MON FEB 9
┌─────────────────────────────────────────────────────────────┐
│ ⚡ START HERE: Item 1.10 - Anonymization Salt              │
│                                                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ QUICK WINS PHASE (12 hours total)                       │ │
│ │                                                          │ │
│ │ 🔧 1.10 Anonymization Salt                  ~2 hours    │ │
│ │    └─ Commit by EOD                                     │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
│ 📋 Review: TIER_1_10_QUICK_START.md (read ahead)           │
└─────────────────────────────────────────────────────────────┘

TUE FEB 10
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│ 🔐 1.7 Access Control (Clinician Identity)  ~4 hours       │
│    ├─ Find professional endpoints                           │
│    ├─ Fix identity verification                            │
│    └─ Commit                                                │
│                                                              │
│ 🕐 1.5 Session Management Hardening        ~6 hours        │
│    ├─ Reduce 30→7 day lifetime                             │
│    ├─ Add rotation on login                                │
│    ├─ Add 30-min inactivity timeout                        │
│    ├─ Add invalidation on password change                  │
│    └─ Commit                                                │
│                                                              │
│ ✅ Phase 1 COMPLETE: All quick wins done                   │
└─────────────────────────────────────────────────────────────┘

WED FEB 11 - THU FEB 12
┌─────────────────────────────────────────────────────────────┐
│ INFRASTRUCTURE PHASE (16 hours total)                        │
│                                                              │
│ 🗄️  1.9 Database Connection Pooling        ~6 hours        │
│    ├─ Create ThreadedConnectionPool                         │
│    ├─ Migrate calls (iterative)                             │
│    ├─ Test under load                                       │
│    └─ Commit                                                │
│                                                              │
│ 📊 1.6 Error Handling & Debug Cleanup      ~10 hours       │
│    ├─ Configure structured logging                          │
│    ├─ Replace 100+ bare exceptions                          │
│    ├─ Remove debug print statements                         │
│    ├─ Audit sensitive data in logs                          │
│    └─ Commit                                                │
│                                                              │
│ ✅ Phase 2 COMPLETE: Infrastructure hardened               │
└─────────────────────────────────────────────────────────────┘

FRI FEB 14 - SAT FEB 15
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND PHASE (12 hours)                                    │
│                                                              │
│ 🛡️  1.8 XSS Prevention - innerHTML Audit   ~12 hours       │
│    ├─ Add DOMPurify library                                 │
│    ├─ Audit 138 innerHTML instances                         │
│    ├─ Replace user data with textContent                    │
│    ├─ Sanitize rich content                                 │
│    ├─ Create sanitization helpers                           │
│    └─ Commit                                                │
│                                                              │
│ 🎉 ALL TIER 1.5-1.10 COMPLETE!                             │
│    ├─ 6 security items implemented                          │
│    ├─ 40 hours of hardening complete                        │
│    ├─ Production-ready security posture                     │
│    └─ Ready for TIER 1.1 (Dashboard)                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Hours Allocation

```
                    TIER 1.5-1.10 BREAKDOWN
                    ════════════════════════════════

1.10 Anonymization Salt          ███           2 hours (5%)
1.7  Access Control              ███████       4 hours (10%)
1.5  Session Management          ██████████   6 hours (15%)
────────────────────────────────────────────────────────────
1.9  Database Pooling            ██████████   6 hours (15%)
1.6  Error Handling              ████████████████ 10 hours (25%)
────────────────────────────────────────────────────────────
1.8  XSS Prevention              ████████████████ 12 hours (30%)
────────────────────────────────────────────────────────────

Total: 40 hours (100%) over 6-7 days
```

---

## 🎯 Daily Targets

| Day | Target | Hours | Status |
|-----|--------|-------|--------|
| **Mon Feb 9** | Complete 1.10 | 2 | [ ] |
| **Tue Feb 10** | Complete 1.7 + 1.5 | 10 | [ ] |
| **Wed Feb 11** | Start 1.9 | 6 | [ ] |
| **Thu Feb 12** | Complete 1.9 + 1.6 | 10 | [ ] |
| **Fri Feb 14** | Start 1.8 | 6 | [ ] |
| **Sat Feb 15** | Complete 1.8 | 6 | [ ] |
| **TOTAL** | All 6 items | **40** | [ ] |

---

## 🚀 Getting Started

### Right Now (Next 15 minutes)

```bash
# 1. Read this file (you're doing it!)
cat TIER_1_5_TO_1_10_VISUAL_ROADMAP.md  ✓

# 2. Read quick start
cat TIER_1_10_QUICK_START.md

# 3. Create feature branch
git checkout -b security/tier1-1.10

# 4. Start implementing item 1.10
vim training_data_manager.py
vim .env.example
# Follow steps 1-9 in TIER_1_10_QUICK_START.md

# 5. Test and commit
pytest tests/ -v
python3 -m py_compile training_data_manager.py
git commit -m "security(1.10): remove hardcoded anonymization salt"
git push origin security/tier1-1.10
```

**Time to complete first item**: 1-2 hours

---

## 📚 Documents You Have

```
📋 Planning & Reference
├─ TIER_1_5_TO_1_10_SUMMARY.md              ← Start here (overview)
├─ TIER_1_5_TO_1_10_IMPLEMENTATION_PLAN.md  ← Full technical details
├─ TIER_1_5_TO_1_10_CODE_LOCATIONS.md       ← Quick file/line reference
├─ TIER_1_5_TO_1_10_VISUAL_ROADMAP.md       ← This file
└─ TIER_1_5_TO_1_10_TRACKER.md              ← Progress checklist

⚡ Quick Starts
└─ TIER_1_10_QUICK_START.md                 ← Step-by-step for first item

📖 Background Context
├─ .github/copilot-instructions.md          ← Code patterns & conventions
└─ docs/9-ROADMAP/Priority-Roadmap.md       ← Full project roadmap
```

---

## ✅ Success Milestones

```
┌──────────────────────────────────────────────────────┐
│ MILESTONE 1: Quick Wins (12 hours)                   │
│ ✅ 1.10 Salt - Environment-based instead of hardcode │
│ ✅ 1.7 Access Control - No clinician spoofing         │
│ ✅ 1.5 Sessions - 7-day max, timeout, rotation       │
│ All original tests passing                           │
│ Ready for Phase 2                                    │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ MILESTONE 2: Infrastructure (16 hours)               │
│ ✅ 1.9 Pooling - No connection exhaustion            │
│ ✅ 1.6 Errors - Structured logs, no debug leaks      │
│ All original tests still passing                     │
│ Ready for Phase 3                                    │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ MILESTONE 3: Frontend (12 hours)                     │
│ ✅ 1.8 XSS - textContent + DOMPurify sanitization    │
│ All 13 original tests passing                        │
│ NEW XSS injection tests passing                      │
│ Production-ready security posture achieved! 🎉       │
│ Ready for TIER 1.1 (Clinician Dashboard)             │
└──────────────────────────────────────────────────────┘
```

---

## 🔄 Between Items Workflow

After each item is DONE:

```
ITEM COMPLETE
    │
    ├─► Run Tests: pytest tests/ -v  [all must pass]
    │
    ├─► Update TRACKER: TIER_1_5_TO_1_10_TRACKER.md
    │   └─ Mark status: DONE
    │   └─ Add commit SHA
    │   └─ Note time spent
    │
    ├─► Push: git push origin security/tier1-ITEM
    │
    ├─► Verify: Check CI/tests pass on Railway
    │
    └─► Move to NEXT ITEM in sequence
        1.10 → 1.7 → 1.5 → 1.9 → 1.6 → 1.8
```

---

## 🎓 What You'll Learn

By Feb 15, you'll be expert at:

| Skill | Item |
|-------|------|
| Config management & secrets | 1.10 |
| Authentication & authorization | 1.7 |
| Session security | 1.5 |
| Performance optimization | 1.9 |
| Logging & observability | 1.6 |
| Frontend security | 1.8 |

**These patterns apply to EVERY endpoint and module going forward.**

---

## 🚨 Important Notes

- **Can be done iteratively**: You don't need to do them all at once. Spread over a week.
- **Independent commits**: Each item = separate feature branch + commit. Clean history.
- **Test infrastructure separate**: Claude extension is building tests in parallel. You implement fixes; tests verify them.
- **No rollback needed**: Each fix is backwards-compatible or fail-safe.
- **Documentation available**: Every step has detailed instructions in the guides.

---

## 📞 Quick Reference

| Need | Document |
|------|----------|
| Overview of what's happening | This file (VISUAL_ROADMAP.md) |
| Step-by-step for first item | TIER_1_10_QUICK_START.md |
| Technical details per item | TIER_1_5_TO_1_10_IMPLEMENTATION_PLAN.md |
| File locations & grep commands | TIER_1_5_TO_1_10_CODE_LOCATIONS.md |
| Progress tracking | TIER_1_5_TO_1_10_TRACKER.md |
| Code patterns & conventions | .github/copilot-instructions.md |
| Full project roadmap | docs/9-ROADMAP/Priority-Roadmap.md |

---

## 🎯 TL;DR

**Start now**: Read TIER_1_10_QUICK_START.md (2 min)  
**First item**: 1-2 hours on 1.10 (Anonymization Salt)  
**Full phase**: 40 hours over 6-7 days (6 items)  
**Result**: Production-ready security, ready for TIER 1.1 Dashboard  
**Next**: Move to clinician dashboard (20-25 hours)

---

**Created**: Feb 9, 2026  
**Status**: Ready to Execute  
**Next Action**: Open TIER_1_10_QUICK_START.md and start!
