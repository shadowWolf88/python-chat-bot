#!/bin/bash

FILES_TO_ARCHIVE=(
    # Phase completions
    "PHASE_1_COMPLETION_REPORT.md"
    "PHASE_1_STATUS_COMPLETE.md"
    "PHASE_2_COMPLETION_REPORT.md"
    "PHASE_3_MESSAGING_CHECKLIST.md"
    "PHASE_5_COMPLETION_REPORT.md"
    "PHASE_5_DB_MIGRATION_KICKOFF.md"
    "PHASE_5_DOCUMENTATION_INDEX.md"
    "PHASE_5_STEP5_COMPLETE.md"
    "PHASE_5_STEP6_COMPLETE.md"
    "PHASE_5_STEP7_COMPLETE.md"
    "PHASE_5_VERIFICATION_COMPLETE.md"
    
    # Project status reports
    "PROJECT_AUDIT_2026.md"
    "PROJECT_COMPLETION_PHASE_1_5.md"
    "PROJECT_MANAGEMENT_HUB_READY.md"
    "CONSOLIDATION_COMPLETE.md"
    "all_steps_completed.md"
    "SAVEPOINT_FEB4_2026.md"
    "DECISIONS_IMPLEMENTED.md"
    "IMPLEMENTATION_COMPLETE.md"
    "IMPLEMENTATION_REPORT.md"
    
    # Superseded status/session reports
    "SESSION_SUMMARY_PHASE_3.md"
    "DEPLOYMENT_BLOCKED_CRITICAL.md"
    "DEPLOYMENT_FIX_COMPLETE.md"
    "DEPLOYMENT_WEBHOOK_STATUS.md"
    "FEB_4_BUG_FIX_SUMMARY.md"
    
    # Test results (keep latest only)
    "TEST_RESULTS.md"
    
    # Misc/logs
    "WEBHOOK_TEST.txt"
    "SQLITE_REMOVAL_COMPLETE.md"
)

for file in "${FILES_TO_ARCHIVE[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" documentation/archive/ 2>/dev/null && echo "✓ Moved $file"
    fi
done

echo "✓ Archived $(ls documentation/archive | wc -l) files"
