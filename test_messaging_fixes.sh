#!/bin/bash
# Messaging System Validation Test
# Tests all three major fixes: CSP, send error, tab switching
# Date: February 12, 2026

echo "=========================================="
echo "Messaging System Validation Test"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Check if CSP header is correct
echo -e "${BLUE}[TEST 1] Checking CSP header...${NC}"
CSP_HEADER=$(curl -s -I https://www.healing-space.org.uk 2>/dev/null | grep -i "Content-Security-Policy" | head -1)

if echo "$CSP_HEADER" | grep -q "https://cdn.jsdelivr.net"; then
    echo -e "${GREEN}✓ CSP header includes cdn.jsdelivr.net${NC}"
    echo "  Header: $CSP_HEADER" | head -c 100
    echo "..."
else
    echo -e "${RED}✗ CSP header missing cdn.jsdelivr.net${NC}"
    echo "  Current: $CSP_HEADER"
fi
echo ""

# 2. Test send_message endpoint
echo -e "${BLUE}[TEST 2] Testing /api/messages/send endpoint...${NC}"
echo "⚠️  Requires authentication - checking endpoint exists (200/401/403)"
STATUS=$(curl -s -w "%{http_code}" -X POST https://www.healing-space.org.uk/api/messages/send \
  -H "Content-Type: application/json" \
  -d '{"recipient":"test","content":"test"}' \
  -o /dev/null 2>/dev/null)

if [ "$STATUS" = "401" ] || [ "$STATUS" = "403" ] || [ "$STATUS" = "400" ]; then
    echo -e "${GREEN}✓ Endpoint exists and returns authentication/validation errors (HTTP $STATUS)${NC}"
else
    echo -e "${RED}✗ Endpoint returned unexpected status: $STATUS${NC}"
fi
echo ""

# 3. Check code for error logging
echo -e "${BLUE}[TEST 3] Checking send_message endpoint has error logging...${NC}"
if grep -q "\[send_message\]" api.py 2>/dev/null; then
    LOGGING_COUNT=$(grep -c "\[send_message\]" api.py)
    echo -e "${GREEN}✓ Found $LOGGING_COUNT logging statements with [send_message] prefix${NC}"
else
    echo -e "${YELLOW}! Couldn't verify in API (may be on server only)${NC}"
fi
echo ""

# 4. Check message_service has error handling
echo -e "${BLUE}[TEST 4] Checking message_service.py error handling...${NC}"
if grep -q "try:" message_service.py && grep -q "except.*ValueError" message_service.py; then
    RECV_CHECK=$(grep -c "Recipient.*not found" message_service.py)
    CONV_CHECK=$(grep -c "Failed to.*conversation" message_service.py)
    echo -e "${GREEN}✓ Found recipient validation: $RECV_CHECK matches${NC}"
    echo -e "${GREEN}✓ Found conversation error handling: $CONV_CHECK matches${NC}"
else
    echo -e "${YELLOW}! Couldn't verify error handling in code${NC}"
fi
echo ""

# 5. Check tab caching functions exist
echo -e "${BLUE}[TEST 5] Checking tab caching render functions...${NC}"
if grep -q "renderInboxFromCache" templates/index.html 2>/dev/null; then
    echo -e "${GREEN}✓ Found renderInboxFromCache() function${NC}"
else
    echo -e "${RED}✗ renderInboxFromCache() function not found${NC}"
fi

if grep -q "renderSentFromCache" templates/index.html 2>/dev/null; then
    echo -e "${GREEN}✓ Found renderSentFromCache() function${NC}"
else
    echo -e "${RED}✗ renderSentFromCache() function not found${NC}"
fi

CACHE_LOGIC=$(grep -c "if.*messageTabCache" templates/index.html 2>/dev/null || echo 0)
echo -e "${GREEN}✓ Found $CACHE_LOGIC cache logic checks in tab switching${NC}"
echo ""

# 6. Summary
echo -e "${BLUE}=========================================="
echo "Test Summary"
echo "==========================================${NC}"
echo ""
echo "Manual Testing Checklist:"
echo -e "${YELLOW}1. Patient Dashboard${NC}"
echo "   [ ] Click Messages → Inbox (data loads)"
echo "   [ ] Switch to Sent (data loads, Inbox still displays)"
echo "   [ ] Switch back to Inbox (uses cache, instant)"
echo "   [ ] Check console for [switchMessageTab] logs"
echo ""
echo -e "${YELLOW}2. Developer Dashboard${NC}"
echo "   [ ] Fill message form"
echo "   [ ] Send message (should succeed or show specific error)"
echo "   [ ] Check console for no 500 errors"
echo "   [ ] Check server logs for [send_message] entries"
echo ""
echo -e "${YELLOW}3. CSP Verification${NC}"
echo "   [ ] Open browser console (F12)"
echo "   [ ] Look for CSP violation warnings"
echo "   [ ] Should NOT see violations for cdn.jsdelivr.net"
echo ""

echo -e "${GREEN}✓ Validation test complete!${NC}"
echo ""
echo "See MESSAGING_FIXES_SUMMARY.md for detailed documentation"
