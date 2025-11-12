#!/bin/bash

# Startup script for AI Conversation Assistant
# This script starts both the backend and frontend services

set -e

echo "🚀 Starting AI Conversation Assistant..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if backend virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo -e "${RED}❌ Backend virtual environment not found!${NC}"
    echo "Please run setup first:"
    echo "  cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${RED}❌ Node modules not found!${NC}"
    echo "Please run: npm install"
    exit 1
fi

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo -e "${RED}❌ Backend .env file not found!${NC}"
    echo "Please create backend/.env from backend/.env.example"
    exit 1
fi

echo -e "${GREEN}✅ All dependencies found${NC}"
echo ""

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend in background
echo -e "${BLUE}🔧 Starting Backend (FastAPI)...${NC}"
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 3

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backend started on http://localhost:8000${NC}"
echo -e "   API Docs: http://localhost:8000/docs"
echo ""

# Start frontend in background
echo -e "${BLUE}🎨 Starting Frontend (Vite)...${NC}"
npm run dev &
FRONTEND_PID=$!

# Wait a bit for frontend to start
sleep 3

# Check if frontend is running
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Frontend failed to start${NC}"
    kill $BACKEND_PID
    exit 1
fi

echo -e "${GREEN}✅ Frontend started on http://localhost:3000${NC}"
echo ""
echo -e "${GREEN}🎉 Application is ready!${NC}"
echo -e "   Frontend: ${BLUE}http://localhost:3000${NC}"
echo -e "   Backend:  ${BLUE}http://localhost:8000${NC}"
echo -e "   API Docs: ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for both processes
wait
