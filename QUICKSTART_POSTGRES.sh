#!/bin/bash

# Quick Start Script for PostgreSQL Migration
# This automates the entire migration process

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_info() { echo -e "${BLUE}ℹ${NC} $1"; }

echo ""
echo "=========================================="
echo "  PostgreSQL Migration - Quick Start"
echo "=========================================="
echo ""

BACKEND_DIR="/Users/harjyot/Desktop/code/roblox/ai-atl-25/backend"

# Step 1: Check PostgreSQL
print_info "Step 1: Checking PostgreSQL installation..."
if command -v psql &> /dev/null; then
    print_success "PostgreSQL found"
else
    print_error "PostgreSQL not found"
    echo "Install with: brew install postgresql@15"
    exit 1
fi

# Step 2: Start PostgreSQL service
print_info "Step 2: Ensuring PostgreSQL service is running..."
if brew services list | grep postgresql | grep started &> /dev/null; then
    print_success "PostgreSQL service is running"
else
    print_warning "Starting PostgreSQL service..."
    brew services start postgresql@15
    sleep 3
    print_success "PostgreSQL service started"
fi

# Step 3: Create database
print_info "Step 3: Creating database..."
psql postgres -c "CREATE DATABASE conversation_ai;" 2>/dev/null || print_warning "Database may already exist"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE conversation_ai TO postgres;" 2>/dev/null
print_success "Database ready"

# Step 4: Install Python dependencies
print_info "Step 4: Installing Python dependencies..."
cd "$BACKEND_DIR"

# Install dependencies globally
print_warning "Installing Python packages globally (this may take a few minutes)..."
pip3 install --upgrade pip 2>&1 | grep -v "WARNING" || true

# Install core dependencies first to avoid conflicts
pip3 install --upgrade fastapi uvicorn[standard] sqlalchemy psycopg2-binary alembic bcrypt 2>&1 | grep -v "WARNING" || true

# Then install the rest
pip3 install --upgrade pydantic pydantic-settings python-dotenv requests 2>&1 | grep -v "WARNING" || true
pip3 install --upgrade numpy pandas python-multipart python-jose passlib python-dateutil 2>&1 | grep -v "WARNING" || true
pip3 install --upgrade deepface tf-keras tensorflow opencv-python 2>&1 | grep -v "WARNING" || true
pip3 install --upgrade pyaudio websockets deepgram-sdk httpx 2>&1 | grep -v "WARNING" || true

print_success "Dependencies installed"

# Step 5: Initialize database schema
print_info "Step 5: Initializing database schema..."
python3 scripts/init_db_postgres.py
print_success "Database schema created"

# Step 6: Verify setup
print_info "Step 6: Verifying setup..."

# Test connection
psql postgresql://postgres:postgres@localhost:5432/conversation_ai -c "SELECT 'Connection OK' as status;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_success "Database connection verified"
else
    print_error "Database connection failed"
    exit 1
fi

# Count tables
TABLE_COUNT=$(psql postgresql://postgres:postgres@localhost:5432/conversation_ai -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" | tr -d ' ')
if [ "$TABLE_COUNT" -ge "7" ]; then
    print_success "All tables created ($TABLE_COUNT tables)"
else
    print_warning "Expected 7+ tables, found $TABLE_COUNT"
fi

echo ""
echo "=========================================="
echo "  Migration Complete!"
echo "=========================================="
echo ""

print_success "PostgreSQL database is ready to use"
echo ""
echo "Database info:"
echo "  Host:     localhost"
echo "  Port:     5432"
echo "  Database: conversation_ai"
echo "  User:     postgres"
echo "  Password: postgres"
echo ""
echo "Test user created:"
echo "  Email:    test@example.com"
echo "  Password: testpassword"
echo ""
echo "Next steps:"
echo ""
echo "1. Start the backend server:"
echo "   cd $BACKEND_DIR"
echo "   uvicorn app.main:app --reload --port 8000"
echo ""
echo "2. Start the frontend:"
echo "   cd /tmp/memory-frontend"
echo "   npm run dev"
echo ""
echo "3. Open browser:"
echo "   http://localhost:5173"
echo ""
echo "4. Test the integration:"
echo "   - Click 'Demo' to create sample conversation"
echo "   - Data will be saved in PostgreSQL"
echo ""

print_info "View migration guide: POSTGRES_MIGRATION_GUIDE.md"
print_info "API Documentation: http://localhost:8000/docs (when backend is running)"

echo ""
