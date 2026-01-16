#!/bin/bash
# Cron Job Setup Script for Mood Reminders

echo "=== Setting Up Daily Mood Reminders at 8pm ==="
echo ""

# Get the absolute path to the script
SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)/send_mood_reminders.sh"

echo "Script location: $SCRIPT_PATH"
echo ""

# Check if script is executable
if [ ! -x "$SCRIPT_PATH" ]; then
    echo "Making script executable..."
    chmod +x "$SCRIPT_PATH"
fi

# Create the cron job entry
CRON_JOB="0 20 * * * $SCRIPT_PATH"

echo "This will add the following cron job:"
echo "$CRON_JOB"
echo ""
echo "Translation: Run at 8:00 PM every day"
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "send_mood_reminders.sh"; then
    echo "⚠️  Cron job already exists!"
    echo ""
    echo "Current crontab:"
    crontab -l | grep "send_mood_reminders.sh"
    echo ""
    read -p "Do you want to replace it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
    # Remove old entry
    (crontab -l 2>/dev/null | grep -v "send_mood_reminders.sh") | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Cron job added successfully!"
echo ""
echo "Verification:"
crontab -l | grep "send_mood_reminders.sh"
echo ""
echo "📋 Logs will be saved to: /tmp/mood_reminder_cron.log"
echo ""
echo "🧪 Test the script now with:"
echo "   ./send_mood_reminders.sh"
echo ""
echo "🔍 View logs with:"
echo "   tail -f /tmp/mood_reminder_cron.log"
echo ""
echo "🗑️  To remove the cron job later:"
echo "   crontab -e"
echo "   (Delete the line with send_mood_reminders.sh)"
