#!/bin/bash
# Test runner for risk module

set -e  # Exit on error

echo "================================================"
echo "  Arbitra Risk Module Test Suite"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo -e "${YELLOW}Warning: Virtual environment not activated${NC}"
    echo "Run: source venv/bin/activate"
    echo ""
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest not found${NC}"
    echo "Install with: pip install -r requirements.txt"
    exit 1
fi

echo "Running tests..."
echo ""

# Run tests with coverage
pytest tests/risk/ \
    -v \
    --cov=src/risk \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-fail-under=90 \
    --tb=short

TEST_EXIT_CODE=$?

echo ""
echo "================================================"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Coverage report generated in: htmlcov/index.html"
    echo ""
    echo "Next steps:"
    echo "1. Review coverage report"
    echo "2. Check for any warnings"
    echo "3. Move to Phase 2 (AI Engine)"
else
    echo -e "${RED}✗ Tests failed${NC}"
    echo ""
    echo "Please fix failing tests before proceeding."
    exit 1
fi

echo "================================================"
