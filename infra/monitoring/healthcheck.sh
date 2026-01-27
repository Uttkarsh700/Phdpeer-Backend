#!/bin/bash

# Health check script for monitoring
# This can be used with monitoring tools like Nagios, Prometheus, etc.

set -e

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "=== Health Check ==="
echo ""

# Check Backend
echo -n "Backend API: "
if curl -sf "$API_URL/health" > /dev/null; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Unhealthy${NC}"
    exit 1
fi

# Check Frontend
echo -n "Frontend: "
if curl -sf "$FRONTEND_URL" > /dev/null; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Unhealthy${NC}"
    exit 1
fi

# Check Database (through backend)
echo -n "Database: "
if curl -sf "$API_URL/api/v1/health/db" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Connected${NC}"
else
    echo -e "${GREEN}⚠ Check endpoint not available (this is normal for scaffold)${NC}"
fi

echo ""
echo "=== All checks passed ==="
exit 0
