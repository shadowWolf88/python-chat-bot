#!/bin/bash
#
# Setup Cron Job for Automated Training Data Export
#
# This script sets up a cron job to automatically export anonymized
# training data from consented users.
#
# Usage: ./setup_training_export_cron.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPORT_SCRIPT="$SCRIPT_DIR/export_training_data.py"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/training_export.log"

echo "=============================================="
echo "Training Data Export - Cron Setup"
echo "=============================================="
echo ""

# Check if export script exists
if [ ! -f "$EXPORT_SCRIPT" ]; then
    echo "Error: export_training_data.py not found!"
    exit 1
fi

# Make export script executable
chmod +x "$EXPORT_SCRIPT"
echo "✓ Made export script executable"

# Create logs directory
mkdir -p "$LOG_DIR"
echo "✓ Created logs directory: $LOG_DIR"

# Create cron job entry
CRON_CMD="0 2 * * * cd \"$SCRIPT_DIR\" && /usr/bin/python3 export_training_data.py >> \"$LOG_FILE\" 2>&1"

echo ""
echo "Cron job command:"
echo "$CRON_CMD"
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "export_training_data.py"; then
    echo "⚠ Cron job already exists. Remove it first? (y/n)"
    read -r response
    if [ "$response" = "y" ]; then
        # Remove existing cron job
        (crontab -l 2>/dev/null | grep -v "export_training_data.py") | crontab -
        echo "✓ Removed existing cron job"
    else
        echo "Keeping existing cron job"
        exit 0
    fi
fi

# Add cron job
(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
echo "✓ Cron job installed successfully!"

echo ""
echo "=============================================="
echo "Setup Complete!"
echo "=============================================="
echo ""
echo "Export will run daily at 2:00 AM"
echo "Logs will be written to: $LOG_FILE"
echo ""
echo "To view current crontab:"
echo "  crontab -l"
echo ""
echo "To remove the cron job:"
echo "  crontab -l | grep -v export_training_data.py | crontab -"
echo ""
echo "To test the export manually:"
echo "  python3 export_training_data.py"
echo ""
echo "To view logs:"
echo "  tail -f $LOG_FILE"
echo ""
