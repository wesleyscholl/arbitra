#!/bin/bash

# Quick Test Script for Arbitra API

echo "🧪 Testing Arbitra API Endpoints..."
echo ""

BASE_URL="http://localhost:8000"

# Test 1: Health check
echo "1️⃣  Health Check"
curl -s $BASE_URL/health | python -m json.tool
echo ""

# Test 2: Account info
echo "2️⃣  Account Information"
curl -s $BASE_URL/api/trading/account | python -m json.tool
echo ""

# Test 3: Get quote for AAPL
echo "3️⃣  Latest Quote for AAPL"
curl -s $BASE_URL/api/trading/quote/AAPL | python -m json.tool
echo ""

# Test 4: Current positions
echo "4️⃣  Current Positions"
curl -s $BASE_URL/api/trading/positions | python -m json.tool
echo ""

echo "✅ Tests complete!"
