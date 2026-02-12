#!/bin/bash
# Quick messaging system test - verifies the fixes are working on Railway

echo "🧪 Messaging System Verification Test"
echo "======================================"
echo ""
echo "⏳ Waiting for Railway rebuild (2-3 minutes)..."
sleep 120

# Get your production URL from Railway
PROD_URL="https://healing-space-uk-production.up.railway.app"

echo ""
echo "Testing endpoints..."
echo ""

# Test 1: Check if inbox endpoint is working
echo "1️⃣ Testing /api/messages/inbox endpoint..."
INBOX_TEST=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Cookie: session=<YOUR_SESSION_COOKIE>" \
  "$PROD_URL/api/messages/inbox")

if [ "$INBOX_TEST" = "200" ]; then
    echo "   ✅ Inbox endpoint responding (200)"
else
    echo "   ⚠️ Inbox returned: $INBOX_TEST (expected 200 or 401 if not authenticated)"
fi

echo ""
echo "2️⃣ Testing /api/messages/sent endpoint..."
SENT_TEST=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Cookie: session=<YOUR_SESSION_COOKIE>" \
  "$PROD_URL/api/messages/sent")

if [ "$SENT_TEST" = "200" ]; then
    echo "   ✅ Sent endpoint responding (200)"
else
    echo "   ⚠️ Sent returned: $SENT_TEST (expected 200 or 401 if not authenticated)"
fi

echo ""
echo "3️⃣ Frontend Tab Test (Manual)"
echo "   Please test in browser:"
echo "   - Click 'Messages' tab"
echo "   - Verify inbox loads with conversations"
echo "   - Click 'Sent' tab - should show sent messages"
echo "   - Click 'New Message' tab - should show compose form"
echo "   - Switch back to Inbox - should still show data (cached)"
echo ""
echo "✅ Tests complete! Check browser for UI verification."
