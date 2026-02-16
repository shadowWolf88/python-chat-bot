#!/bin/bash
# Daily Mood Reminder Script
# Runs at 8pm to notify users who haven't logged their mood

# Determine the API URL (use localhost for local dev, or your Railway URL for production)
API_URL="${API_URL:-http://localhost:5000}"

# Log start
echo "$(date): Starting mood reminder check..." >> /tmp/mood_reminder_cron.log

# Send reminder check request and capture response
RESPONSE=$(curl -X POST "$API_URL/api/mood/check-reminder" \
  -H "Content-Type: application/json" \
  -s -w "\nHTTP_CODE:%{http_code}" \
  2>&1)

# Extract HTTP code
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | grep -v "HTTP_CODE:")

# Log the result
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Success: $BODY" >> /tmp/mood_reminder_cron.log
else
    echo "❌ Failed (HTTP $HTTP_CODE): $BODY" >> /tmp/mood_reminder_cron.log
fi
echo "---" >> /tmp/mood_reminder_cron.log
