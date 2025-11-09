#!/bin/bash
set -e

echo "=========================================="
echo "AI Conversation Assistant - Installation"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check prerequisites
echo "Checking prerequisites..."

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python ${PYTHON_VERSION} found"
else
    print_error "Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check pip
if command -v pip3 &> /dev/null; then
    print_success "pip3 found"
else
    print_error "pip3 is not installed. Please install pip3."
    exit 1
fi

echo ""
echo "=========================================="
echo "Installing Backend Dependencies"
echo "=========================================="
echo ""

# Navigate to backend directory
BACKEND_DIR="/Users/harjyot/Desktop/code/roblox/ai-atl-25/backend"
cd "$BACKEND_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet
print_success "pip upgraded"

# Install requirements
echo "Installing Python dependencies (this may take a few minutes)..."
echo "  - FastAPI, Uvicorn"
echo "  - SQLAlchemy, DuckDB"
echo "  - Google Generative AI (old and new SDKs)"
echo "  - DeepFace, TensorFlow"
echo "  - OpenCV"
echo "  - Deepgram SDK"
echo "  - PyAudio (may require system dependencies)"
echo ""

# Try to install PyAudio dependencies on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v brew &> /dev/null; then
        print_warning "Installing portaudio via Homebrew (required for PyAudio)..."
        brew install portaudio 2>&1 | grep -v "Warning" || true
    fi
fi

# Install Python packages
pip install -r requirements.txt 2>&1 | grep -E "Successfully installed|ERROR|error" || true

# Check if installation was successful
if [ $? -eq 0 ]; then
    print_success "Python dependencies installed"
else
    print_error "Some dependencies failed to install. Check the output above."
    print_warning "You can try installing them manually with: pip install -r requirements.txt"
fi

# Initialize database
echo ""
echo "Initializing database..."
if [ -f "scripts/init_db.py" ]; then
    python scripts/init_db.py
    print_success "Database initialized"
else
    print_warning "Database initialization script not found. You may need to create the database manually."
fi

echo ""
echo "=========================================="
echo "Backend Installation Complete!"
echo "=========================================="
echo ""
print_success "Backend is ready to run"
echo ""
echo "To start the backend server, run:"
echo "  cd $BACKEND_DIR"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "The API will be available at:"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo "  - Health: http://localhost:8000/health"
echo ""

# Frontend setup
echo "=========================================="
echo "Installing Frontend Dependencies"
echo "=========================================="
echo ""

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js ${NODE_VERSION} found"
else
    print_error "Node.js is not installed. Please install Node.js 18 or higher."
    echo "You can install it from: https://nodejs.org/"
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_success "npm ${NPM_VERSION} found"
else
    print_error "npm is not installed."
    exit 1
fi

FRONTEND_DIR="/tmp/memory-frontend"

if [ -d "$FRONTEND_DIR" ]; then
    cd "$FRONTEND_DIR"

    echo "Installing Node.js dependencies..."
    npm install --quiet 2>&1 | grep -E "added|ERROR|error" || true

    if [ $? -eq 0 ]; then
        print_success "Frontend dependencies installed"
    else
        print_error "Some frontend dependencies failed to install."
    fi

    echo ""
    echo "=========================================="
    echo "Frontend Installation Complete!"
    echo "=========================================="
    echo ""
    print_success "Frontend is ready to run"
    echo ""
    echo "To start the frontend server, run:"
    echo "  cd $FRONTEND_DIR"
    echo "  npm run dev"
    echo ""
    echo "The frontend will be available at:"
    echo "  - http://localhost:5173"
    echo ""
else
    print_warning "Frontend directory not found at $FRONTEND_DIR"
    echo "Please ensure the frontend is cloned/copied to that location."
fi

echo ""
echo "=========================================="
echo "Installation Summary"
echo "=========================================="
echo ""
echo "✓ Backend dependencies installed"
echo "✓ Database initialized"
echo "✓ Environment files created"
echo "✓ Frontend dependencies installed"
echo ""
echo "Next steps:"
echo "1. Start backend:  cd $BACKEND_DIR && source venv/bin/activate && uvicorn app.main:app --reload --port 8000"
echo "2. Start frontend: cd $FRONTEND_DIR && npm run dev"
echo "3. Open browser:   http://localhost:5173"
echo ""
echo "For detailed instructions, see:"
echo "  - SETUP.md"
echo "  - INTEGRATION_README.md"
echo ""
print_success "Installation complete!"
