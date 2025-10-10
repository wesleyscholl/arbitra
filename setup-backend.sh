#!/bin/bash
# Quick setup for Arbitra Paper Trading Backend

echo "🚀 Setting up Arbitra Paper Trading Backend..."
echo ""

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p backend/{api/routes,services,database,trading,tests}
touch backend/__init__.py
touch backend/api/__init__.py
touch backend/api/routes/__init__.py
touch backend/services/__init__.py
touch backend/database/__init__.py
touch backend/trading/__init__.py

# Create requirements.txt
echo "📦 Creating requirements.txt..."
cat > backend/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
sqlalchemy==2.0.23
alembic==1.12.1
websockets==12.0
alpaca-py==0.18.0
pandas==2.1.3
numpy==1.26.2
scikit-learn==1.3.2
python-dotenv==1.0.0
aiosqlite==0.19.0
EOF

# Create .env template
echo "🔐 Creating .env template..."
cat > .env.example << 'EOF'
# Alpaca API Keys (Get from https://alpaca.markets)
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Paper Trading Settings
INITIAL_CAPITAL=100000.0
ENABLE_SLIPPAGE=true
SLIPPAGE_BPS=5.0
ENABLE_COMMISSION=true
COMMISSION_PER_SHARE=0.005

# Database
DATABASE_URL=sqlite+aiosqlite:///./arbitra.db

# AI Engine
MODEL_UPDATE_INTERVAL=3600
SIGNAL_THRESHOLD=0.6

# API
API_HOST=0.0.0.0
API_PORT=8000
EOF

# Check if .env exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file - EDIT THIS with your API keys!"
else
    echo "ℹ️  .env already exists"
fi

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Activate and install dependencies
echo "📥 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Get Alpaca API keys: https://alpaca.markets (FREE)"
echo "   2. Edit .env file with your API keys"
echo "   3. Follow PAPER_TRADING_PLAN.md to implement the backend"
echo ""
echo "💡 Quick start guide:"
echo "   - Backend structure: backend/"
echo "   - Plan: PAPER_TRADING_PLAN.md"
echo "   - Start coding: backend/main.py"
echo ""
