#!/bin/bash

# TrainerHub - Availability API Test Script
# Tests all Epic 2 endpoints

BASE_URL="http://localhost:8000"
echo "======================================"
echo "TrainerHub Availability API Tests"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Register a new user (Trainer)
echo -e "${YELLOW}Test 1: Register User${NC}"
REGISTER_RESPONSE=$(curl -s -X POST ${BASE_URL}/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testtrainer@example.com",
    "username": "testtrainer",
    "first_name": "Test",
    "last_name": "Trainer",
    "password": "testpass123",
    "password_confirm": "testpass123"
  }')

TOKEN=$(echo $REGISTER_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo -e "${YELLOW}User already exists, trying to login...${NC}"
    
    # Try to login instead
    LOGIN_RESPONSE=$(curl -s -X POST ${BASE_URL}/api/users/login/ \
      -H "Content-Type: application/json" \
      -d '{
        "email": "testtrainer@example.com",
        "password": "testpass123"
      }')
    
    TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('token', ''))" 2>/dev/null)
fi

if [ -z "$TOKEN" ]; then
    echo -e "${RED}✗ Failed to get authentication token${NC}"
    echo "Response: $REGISTER_RESPONSE"
    exit 1
else
    echo -e "${GREEN}✓ Authentication successful${NC}"
    echo "Token: ${TOKEN:0:20}..."
fi

echo ""

# Test 2: Get current user profile
echo -e "${YELLOW}Test 2: Get Current User Profile${NC}"
USER_RESPONSE=$(curl -s -X GET ${BASE_URL}/api/users/me/ \
  -H "Authorization: Token ${TOKEN}")

USER_ID=$(echo $USER_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

if [ -z "$USER_ID" ]; then
    echo -e "${RED}✗ Failed to get user profile${NC}"
    exit 1
else
    echo -e "${GREEN}✓ User profile retrieved (ID: ${USER_ID})${NC}"
fi

echo ""

# Note: We need to create a Trainer profile manually through Django shell or admin
# For this test, we'll check if trainer profile exists

# Test 3: Create Availability Slot (Monday 9am-5pm)
echo -e "${YELLOW}Test 3: Create Availability Slot${NC}"
SLOT_RESPONSE=$(curl -s -X POST ${BASE_URL}/api/availability-slots/ \
  -H "Authorization: Token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "day_of_week": 0,
    "start_time": "09:00:00",
    "end_time": "17:00:00",
    "is_recurring": true,
    "is_active": true
  }')

echo "$SLOT_RESPONSE"

if echo "$SLOT_RESPONSE" | grep -q "trainer_profile"; then
    echo -e "${YELLOW}⚠ User needs a trainer profile. Please create one via admin panel.${NC}"
    echo "Visit: ${BASE_URL}/admin/"
else
    SLOT_ID=$(echo $SLOT_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
    if [ ! -z "$SLOT_ID" ]; then
        echo -e "${GREEN}✓ Availability slot created (ID: ${SLOT_ID})${NC}"
    fi
fi

echo ""

# Test 4: List Availability Slots
echo -e "${YELLOW}Test 4: List Availability Slots${NC}"
LIST_RESPONSE=$(curl -s -X GET ${BASE_URL}/api/availability-slots/ \
  -H "Authorization: Token ${TOKEN}")

echo "$LIST_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LIST_RESPONSE"
echo ""

# Test 5: Query Available Slots
echo -e "${YELLOW}Test 5: Query Available Slots${NC}"
# This requires a trainer_id, we'll use 1 as an example
AVAILABLE_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/availability-slots/available-slots/?trainer_id=1&start_date=2025-01-01&end_date=2025-01-31" \
  -H "Authorization: Token ${TOKEN}")

echo "$AVAILABLE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$AVAILABLE_RESPONSE"
echo ""

# Test 6: Create Trainer Break
echo -e "${YELLOW}Test 6: Create Trainer Break${NC}"
BREAK_RESPONSE=$(curl -s -X POST ${BASE_URL}/api/breaks/ \
  -H "Authorization: Token ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-01-15T00:00:00Z",
    "end_date": "2025-01-20T23:59:59Z",
    "reason": "Holiday vacation"
  }')

echo "$BREAK_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$BREAK_RESPONSE"
echo ""

# Test 7: List Trainer Breaks
echo -e "${YELLOW}Test 7: List Trainer Breaks${NC}"
BREAKS_LIST=$(curl -s -X GET ${BASE_URL}/api/breaks/ \
  -H "Authorization: Token ${TOKEN}")

echo "$BREAKS_LIST" | python3 -m json.tool 2>/dev/null || echo "$BREAKS_LIST"
echo ""

echo "======================================"
echo -e "${GREEN}API Testing Complete!${NC}"
echo "======================================"
echo ""
echo "Note: Some tests may fail if trainer profile doesn't exist."
echo "Create a trainer profile via admin panel: ${BASE_URL}/admin/"
echo ""

