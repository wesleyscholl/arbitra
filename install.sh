#!/bin/bash
# Quick install script for Arbitra

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "================================================"
echo "  Arbitra Quick Install"
echo "================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Error: Must run from arbitra directory${NC}"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
else
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

echo ""
echo "Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo ""
echo "Installing arbitra package in editable mode..."
pip install -e .

echo ""
echo "================================================"
echo -e "${GREEN}✓ Installation complete!${NC}"
echo "================================================"
echo ""
echo "To activate the environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "Then run tests with:"
echo "  ./run_tests.sh"
echo "  or"
echo "  pytest tests/risk/ -v"
echo ""
