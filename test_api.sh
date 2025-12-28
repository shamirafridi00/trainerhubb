#!/bin/bash

# TrainerHub API Testing Script
# Usage: bash test_api.sh

BASE_URL="http://localhost:8000/api"

echo "🚀 TrainerHub API Testing Script"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: User Registration
echo -e "${YELLOW}Test 1: User Registration${NC}"
RESPONSE=$(curl -s -X POST $BASE_URL/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "trainer1@example.com",
    "username": "trainer1",
    "first_name": "Jane",
    "last_name": "Smith",
    "password": "trainer123",
    "password_confirm": "trainer123"
  }')
  
if [[ $RESPONSE == *"token"* ]]; then
    echo -e "${GREEN}✓ Registration successful${NC}"
    TOKEN=$(echo $RESPONSE | grep -o '"token":"[^"]*' | sed 's/"token":"//')
    echo "Token: $TOKEN"
else
    echo -e "${RED}✗ Registration failed${NC}"
    echo $RESPONSE
fi
echo ""

# Test 2: User Login
echo -e "${YELLOW}Test 2: User Login${NC}"
RESPONSE=$(curl -s -X POST $BASE_URL/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "trainer1@example.com",
    "password": "trainer123"
  }')
  
if [[ $RESPONSE == *"token"* ]]; then
    echo -e "${GREEN}✓ Login successful${NC}"
    TOKEN=$(echo $RESPONSE | grep -o '"token":"[^"]*' | sed 's/"token":"//')
    echo "Token: $TOKEN"
else
    echo -e "${RED}✗ Login failed${NC}"
    echo $RESPONSE
fi
echo ""

# Test 3: Get User Profile
echo -e "${YELLOW}Test 3: Get User Profile${NC}"
RESPONSE=$(curl -s -X GET $BASE_URL/users/me/ \
  -H "Authorization: Token $TOKEN")
  
if [[ $RESPONSE == *"email"* ]]; then
    echo -e "${GREEN}✓ Profile retrieved successfully${NC}"
    echo $RESPONSE | python3 -m json.tool 2>/dev/null || echo $RESPONSE
else
    echo -e "${RED}✗ Profile retrieval failed${NC}"
    echo $RESPONSE
fi
echo ""

# Test 4: Update Profile
echo -e "${YELLOW}Test 4: Update Profile${NC}"
RESPONSE=$(curl -s -X PATCH $BASE_URL/users/update-profile/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890"
  }')
  
if [[ $RESPONSE == *"phone_number"* ]]; then
    echo -e "${GREEN}✓ Profile updated successfully${NC}"
    echo $RESPONSE | python3 -m json.tool 2>/dev/null || echo $RESPONSE
else
    echo -e "${RED}✗ Profile update failed${NC}"
    echo $RESPONSE
fi
echo ""

# Test 5: Logout
echo -e "${YELLOW}Test 5: Logout${NC}"
RESPONSE=$(curl -s -X POST $BASE_URL/users/logout/ \
  -H "Authorization: Token $TOKEN")
  
if [[ $RESPONSE == *"success"* ]]; then
    echo -e "${GREEN}✓ Logout successful${NC}"
else
    echo -e "${RED}✗ Logout failed${NC}"
    echo $RESPONSE
fi
echo ""

echo "================================"
echo -e "${GREEN}✅ EPIC 1 Testing Complete!${NC}"
echo "================================"

