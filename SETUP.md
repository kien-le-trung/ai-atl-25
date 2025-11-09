# Quick Setup Guide

## Prerequisites
- Python 3.9+ (for backend)
- Node.js 18+ (for frontend)
- Git

## Backend Setup

### 1. Navigate to backend directory
```bash
cd /Users/harjyot/Desktop/code/roblox/ai-atl-25/backend
```

### 2. Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows
```

### 3. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note**: If you encounter issues with `pyaudio`, you may need to install system dependencies first:

**macOS**:
```bash
brew install portaudio
pip install pyaudio
```

**Ubuntu/Debian**:
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

**Windows**:
```bash
pip install pipwin
pipwin install pyaudio
```

### 4. Initialize the database
```bash
python scripts/init_db.py
```

### 5. Start the backend server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend is now running at:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## Frontend Setup

### 1. Navigate to frontend directory
```bash
cd /tmp/memory-frontend
```

### 2. Install dependencies
```bash
npm install
```

### 3. Start the frontend development server
```bash
npm run dev
```

**Frontend is now running at:** http://localhost:5173

---

## Quick Test

1. Open http://localhost:5173 in your browser
2. Click "Demo" button to create a sample conversation
3. Backend will:
   - Create partner "Sarah Johnson"
   - Generate 8 sample messages
   - Analyze with Gemini AI
   - Extract facts and topics
   - Calculate sentiment
4. You'll be redirected to the conversation detail page

---

## Troubleshooting

### Backend Issues

#### "ModuleNotFoundError: No module named 'google.generativeai'"
```bash
cd /Users/harjyot/Desktop/code/roblox/ai-atl-25/backend
source venv/bin/activate
pip install google-generativeai
```

#### "No module named 'deepgram'"
```bash
pip install deepgram-sdk
```

#### Database errors
```bash
# Reinitialize database
python scripts/init_db.py
```

#### Port 8000 already in use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn app.main:app --reload --port 8001
# Then update frontend .env: VITE_BACKEND_URL=http://localhost:8001
```

### Frontend Issues

#### CORS errors
Make sure backend `.env` has:
```env
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

#### Module not found errors
```bash
cd /tmp/memory-frontend
rm -rf node_modules package-lock.json
npm install
```

#### Port 5173 already in use
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

---

## Environment Variables

### Backend (.env already created)
Location: `/Users/harjyot/Desktop/code/roblox/ai-atl-25/backend/.env`

All API keys are already configured:
- ✅ GOOGLE_API_KEY (Gemini AI)
- ✅ DEEPGRAM_API_KEY (Transcription)
- ✅ VAPI_API_KEY (Voice calls)
- ✅ DATABASE_URL (DuckDB)
- ✅ ALLOWED_ORIGINS (CORS)

### Frontend (.env already created)
Location: `/tmp/memory-frontend/client/.env`

Configuration:
- ✅ VITE_BACKEND_URL=http://localhost:8000
- ✅ VITE_DEEPGRAM_API_KEY (for browser-based transcription)
- ✅ VITE_USER_ID=1

---

## Verify Setup

### Check Backend
```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy"}
```

### Check Frontend
```bash
# Should see Vite dev server output
# ➜  Local:   http://localhost:5173/
```

### Check Integration
1. Open browser to http://localhost:5173
2. Open browser DevTools (F12) → Console
3. Should see no CORS errors
4. Click "Demo" button
5. Check console for API requests to http://localhost:8000

---

## Next Steps

After setup is complete:

1. **Test Photo Upload**
   - Click "Upload Photo"
   - Upload a face image
   - See face recognition in action

2. **Test Live Session**
   - Click "Start Live Session"
   - Allow camera/microphone
   - Speak and see transcription
   - Complete session to see AI analysis

3. **Explore API Docs**
   - Visit http://localhost:8000/docs
   - Try out different endpoints
   - See all available features

4. **View Integration Guide**
   - Read `/Users/harjyot/Desktop/code/roblox/ai-atl-25/INTEGRATION_README.md`
   - Understand architecture and data flow
   - Learn about advanced features

---

## Running Both Servers

### Option 1: Two Terminal Windows

**Terminal 1 (Backend):**
```bash
cd /Users/harjyot/Desktop/code/roblox/ai-atl-25/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd /tmp/memory-frontend
npm run dev
```

### Option 2: Using tmux (macOS/Linux)

```bash
# Create new tmux session
tmux new -s ai-app

# Split window horizontally
Ctrl+B then "

# Top pane - Backend
cd /Users/harjyot/Desktop/code/roblox/ai-atl-25/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Switch to bottom pane
Ctrl+B then Down Arrow

# Bottom pane - Frontend
cd /tmp/memory-frontend
npm run dev

# Detach from session: Ctrl+B then D
# Reattach: tmux attach -t ai-app
```

---

## Common Commands

### Backend
```bash
# Activate virtual environment
source venv/bin/activate

# Install new package
pip install package-name
pip freeze > requirements.txt

# Run tests (if available)
pytest

# Check code style
black app/
flake8 app/
```

### Frontend
```bash
# Install new package
npm install package-name

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

---

## Development Workflow

1. **Start both servers** (backend + frontend)
2. **Make changes** to frontend code
   - Vite will hot-reload automatically
3. **Make changes** to backend code
   - Uvicorn will reload automatically (with --reload flag)
4. **Test in browser** at http://localhost:5173
5. **Check logs** in terminal windows

---

## Production Deployment

### Backend
```bash
# Remove --reload flag
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Or use gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend
```bash
npm run build
# Output will be in dist/ directory
# Serve with nginx, Apache, or any static file server
```

---

## Support

For detailed integration information, see:
- **Integration Guide**: `/Users/harjyot/Desktop/code/roblox/ai-atl-25/INTEGRATION_README.md`
- **API Documentation**: http://localhost:8000/docs (when backend is running)
- **Backend Repo**: https://github.com/kien-le-trung/ai-atl-25
- **Frontend Repo**: https://github.com/phelpsj1/memory
