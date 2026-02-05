import os
from pathlib import Path

# Group files by category based on naming
ROOT = "/home/computer001/Documents/python chat bot"

categories = {
    "Phase Completions": [
        "PHASE_1_COMPLETION_REPORT.md", "PHASE_1_STATUS_COMPLETE.md",
        "PHASE_2_COMPLETION_REPORT.md", "PHASE_3_MESSAGING_CHECKLIST.md",
        "PHASE_5_COMPLETION_REPORT.md", "PHASE_5_DB_MIGRATION_KICKOFF.md",
        "PHASE_5_DOCUMENTATION_INDEX.md", "PHASE_5_STEP5_COMPLETE.md",
        "PHASE_5_STEP6_COMPLETE.md", "PHASE_5_STEP7_COMPLETE.md",
        "PHASE_5_VERIFICATION_COMPLETE.md"
    ],
    "Project Status Reports": [
        "PROJECT_AUDIT_2026.md", "PROJECT_COMPLETION_PHASE_1_5.md",
        "PROJECT_MANAGEMENT_HUB_READY.md", "CONSOLIDATION_COMPLETE.md",
        "all_steps_completed.md", "SAVEPOINT_FEB4_2026.md"
    ],
    "Railway Deployment (Multiple Versions)": [
        "RAILWAY_DEPLOYMENT_FIXES_2026.md", "RAILWAY_DEPLOY_NOW.md",
        "RAILWAY_DIAGNOSIS_DEBUG.md", "RAILWAY_ENV_VARS.md",
        "RAILWAY_SECRET_KEY_FIX.md", "RAILWAY_STATUS_AND_FIX.md",
        "RAILWAY_WIPE.md"
    ],
    "Messaging System (Multiple Versions)": [
        "MESSAGING_DEVELOPER_GUIDE.md", "MESSAGING_FIX_SUMMARY.md",
        "MESSAGING_INDEX.md", "MESSAGING_SYSTEM_COMPLETE.md",
        "MESSAGING_USER_GUIDE.md", "PHASE_3_MESSAGING_CHECKLIST.md"
    ],
    "Database/Migration": [
        "DB_MIGRATION_PLAN_SQLITE_TO_POSTGRESQL.md", "DB_AUDIT_REPORT.txt"
    ],
    "Security Audits": [
        "API_SECURITY_AUDIT_2026.md", "AUDIT_REPORT_INDEX.md",
        "audit.md", "SECURITY_AUDIT_SUMMARY.txt",
        "SECURITY_HARDENING_COMPLETE.md"
    ],
    "Developer Dashboard": [
        "DEVELOPER_DASHBOARD_GUIDE.md", "DEVELOPER_DASHBOARD_IMPLEMENTATION.md",
        "DEVELOPER_ISSUES_FEB_4.md"
    ],
    "Deployment & Fixes": [
        "DEPLOYMENT_BLOCKED_CRITICAL.md", "DEPLOYMENT_FIX_COMPLETE.md",
        "DEPLOYMENT_WEBHOOK_STATUS.md", "GITHUB_WEBHOOK_SETUP.md",
        "FIX_401_SESSION_ERRORS.md", "FEB_4_BUG_FIX_SUMMARY.md",
        "EMERGENCY_HOTFIX_SUMMARY.md"
    ],
    "Documentation/Roadmaps": [
        "NEXT_STEPS.md", "FUTURE_UPDATES_ROADMAP.md",
        "PRIORITY_ROADMAP.md", "MULTI_PLATFORM_DEPLOYMENT_PLAN.md"
    ],
    "Training/AI": [
        "AI_TRAINING_GUIDE.md", "TRAINING_CLARIFICATION.md"
    ],
    "Feature Documentation": [
        "CLINICIAN_FEATURES_2025.md", "FEATURE_STATUS.md",
        "SESSION_SUMMARY_PHASE_3.md"
    ],
    "Testing/Reports": [
        "TEST_RESULTS.md", "TEST_RESULTS_2026_02_05.md",
        "VALIDATION_REPORT.md"
    ],
    "Setup/Integration Guides": [
        "2FA_SETUP.md", "Prod_readiness.md",
        "REGISTRATION_LOGIN_FLOW_ANALYSIS.md", "Healing_Space_UK_Intro.md"
    ],
    "Misc/Logs": [
        "IMPLEMENTATION_COMPLETE.md", "IMPLEMENTATION_REPORT.md",
        "DECISIONS_IMPLEMENTED.md", "VERSION_HISTORY.txt",
        "SQLITE_REMOVAL_COMPLETE.md", "WEBHOOK_TEST.txt"
    ]
}

print("\n📋 DOCUMENTATION CONSOLIDATION STRATEGY")
print("=" * 80)

for category, files in categories.items():
    print(f"\n{category} ({len(files)} files)")
    print("-" * 80)
    for f in sorted(files):
        path = os.path.join(ROOT, f)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  • {f:50} ({size:,} bytes)")
        else:
            print(f"  • {f:50} (NOT FOUND)")

total_files = sum(len(files) for files in categories.values())
print(f"\n\n📊 CONSOLIDATION SUMMARY")
print("=" * 80)
print(f"Root-level docs to consolidate: {total_files}")
print(f"\n🎯 STRATEGY:")
print("  1. Archive Phase 1-5 completion reports → archive/")
print("  2. Consolidate Railway docs → documentation/infra_and_deployment/RAILWAY.md")
print("  3. Consolidate Messaging → documentation/ (already has good structure)")
print("  4. Keep security audits → consolidate into documentation/audit_and_compliance/")
print("  5. Keep feature docs → move to appropriate folders")
print("  6. Keep roadmap → documentation/roadmaps_and_plans/")
print("  7. Archive old session summaries/savepoints → archive/")
print("  8. Create NEW main README.md and QUICK_START.md at root")
print("  9. Update documentation/00_INDEX.md with new structure")
print("  10. Delete NEXT_STEPS.md and phase status files")

