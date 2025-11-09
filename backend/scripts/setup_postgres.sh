#!/bin/bash

# PostgreSQL Database Setup Script
# This script creates the database and user for the AI Conversation Assistant

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

echo "=========================================="
echo "PostgreSQL Database Setup"
echo "=========================================="
echo ""

# Database configuration
DB_NAME="conversation_ai"
DB_USER="postgres"
DB_PASSWORD="postgres"
DB_HOST="localhost"
DB_PORT="5432"

# Check if PostgreSQL is installed via Homebrew
if command -v psql &> /dev/null; then
    print_success "PostgreSQL is installed"
    psql --version
else
    print_error "PostgreSQL is not installed"
    echo "Install it with: brew install postgresql@15"
    exit 1
fi

# Check if PostgreSQL service is running
if brew services list | grep postgresql | grep started &> /dev/null; then
    print_success "PostgreSQL service is running"
else
    print_warning "PostgreSQL service is not running. Starting it..."
    brew services start postgresql@15
    sleep 3
    print_success "PostgreSQL service started"
fi

echo ""
echo "Creating database and user..."
echo ""

# Create database if it doesn't exist
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres <<EOF
-- Create database if not exists
SELECT 'CREATE DATABASE $DB_NAME'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec

-- Connect to the database
\c $DB_NAME

-- Enable pgvector extension (optional, for vector embeddings)
-- CREATE EXTENSION IF NOT EXISTS vector;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

EOF

if [ $? -eq 0 ]; then
    print_success "Database '$DB_NAME' created successfully"
else
    print_error "Failed to create database"
    exit 1
fi

echo ""
echo "Database connection string:"
echo "postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
echo ""

print_success "PostgreSQL setup complete!"
echo ""
echo "Next steps:"
echo "1. Update backend/.env with the connection string above"
echo "2. Run database migrations: cd backend && alembic upgrade head"
echo "3. Start the backend server: uvicorn app.main:app --reload"
