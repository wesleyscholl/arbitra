#!/bin/bash
# Setup script for Arbitra - supports Podman or local installation

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "================================================"
echo "  Arbitra Setup"
echo "================================================"
echo ""

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
fi

echo "Detected OS: $OS"
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}Error: Python 3.11+ required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"
echo ""

# Ask user about infrastructure preference
echo "Choose infrastructure setup:"
echo "  1) Podman (containers, no root required)"
echo "  2) Local installation (PostgreSQL + Redis native)"
echo "  3) Skip infrastructure (testing only)"
echo ""
read -p "Enter choice (1-3): " INFRA_CHOICE

case $INFRA_CHOICE in
    1)
        echo ""
        echo "Setting up with Podman..."
        
        # Check if podman is installed
        if ! command -v podman &> /dev/null; then
            echo -e "${YELLOW}Podman not found. Installing...${NC}"
            
            if [ "$OS" == "macos" ]; then
                if ! command -v brew &> /dev/null; then
                    echo -e "${RED}Error: Homebrew required for macOS installation${NC}"
                    echo "Install from: https://brew.sh"
                    exit 1
                fi
                brew install podman podman-compose
            elif [ "$OS" == "linux" ]; then
                echo "Please install podman manually for your distribution:"
                echo "https://podman.io/getting-started/installation"
                exit 1
            fi
        fi
        
        # Check if podman-compose is installed
        if ! command -v podman-compose &> /dev/null; then
            echo -e "${YELLOW}Installing podman-compose...${NC}"
            pip3 install podman-compose
        fi
        
        # Initialize podman machine (macOS only)
        if [ "$OS" == "macos" ]; then
            if ! podman machine list | grep -q "Currently running"; then
                echo "Initializing podman machine..."
                podman machine init --cpus 2 --memory 4096 2>/dev/null || true
                podman machine start
            fi
        fi
        
        # Start services
        echo "Starting services with podman-compose..."
        podman-compose up -d
        
        # Wait for services to be healthy
        echo "Waiting for services to be ready..."
        sleep 5
        
        echo -e "${GREEN}✓ Podman services started${NC}"
        echo ""
        echo "Services available at:"
        echo "  - PostgreSQL: localhost:5432"
        echo "  - Redis: localhost:6379"
        ;;
        
    2)
        echo ""
        echo "Setting up local installation..."
        
        if [ "$OS" == "macos" ]; then
            if ! command -v brew &> /dev/null; then
                echo -e "${RED}Error: Homebrew required for macOS installation${NC}"
                exit 1
            fi
            
            # Install PostgreSQL
            if ! command -v psql &> /dev/null; then
                echo "Installing PostgreSQL..."
                brew install postgresql@15
                brew services start postgresql@15
            else
                echo -e "${GREEN}✓ PostgreSQL already installed${NC}"
            fi
            
            # Install Redis
            if ! command -v redis-cli &> /dev/null; then
                echo "Installing Redis..."
                brew install redis
                brew services start redis
            else
                echo -e "${GREEN}✓ Redis already installed${NC}"
            fi
            
            # Create database
            echo "Creating database..."
            createdb arbitra 2>/dev/null || echo "Database already exists"
            
        elif [ "$OS" == "linux" ]; then
            echo "Please install PostgreSQL and Redis manually for your distribution"
            echo ""
            echo "Ubuntu/Debian:"
            echo "  sudo apt-get install postgresql-15 redis-server"
            echo ""
            echo "Fedora/RHEL:"
            echo "  sudo dnf install postgresql15-server redis"
            exit 1
        fi
        
        echo -e "${GREEN}✓ Local services configured${NC}"
        ;;
        
    3)
        echo ""
        echo "Skipping infrastructure setup."
        echo "You can run unit tests without any infrastructure."
        ;;
        
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run tests:"
echo "   ./run_tests.sh"
echo "   or"
echo "   pytest tests/risk/ -v"
echo ""
echo "3. See QUICKSTART.md for more information"
echo ""
