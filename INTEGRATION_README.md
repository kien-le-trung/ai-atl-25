# AI Conversation Assistant - Frontend/Backend Integration

This project integrates the FastAPI backend from `ai-atl-25` with the React frontend from `memory-frontend`.

## Architecture Overview

### Backend (FastAPI)
- **Location**: `/Users/harjyot/Desktop/code/roblox/ai-atl-25/backend`
- **Port**: 8000
- **Database**: DuckDB
- **Key Features**:
  - Face recognition with DeepFace (Facenet512)
  - Live conversation transcription with Deepgram
  - AI analysis with Google Gemini
  - Voice calls with Vapi
  - Camera management (supports OBS Virtual Camera for Meta glasses)
  - Session management with real-time audio processing

### Frontend (React + Vite)
- **Location**: `/tmp/memory-frontend`
- **Port**: 5173 (Vite default)
- **Key Features**:
  - Live conversation sessions with webcam + speech recognition
  - Photo capture and facial recognition
  - Conversation dashboard and analytics
  - Real-time transcription display
  - AI-powered insights and suggestions

## Setup Instructions

### 1. Backend Setup

#### Install Dependencies
```bash
cd /Users/harjyot/Desktop/code/roblox/ai-atl-25/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Environment Configuration
The `.env` file has been created at `/Users/harjyot/Desktop/code/roblox/ai-atl-25/backend/.env` with all necessary API keys:

```env
DATABASE_URL=duckdb:///./conversation_ai.db
GOOGLE_API_KEY=AIzaSyCE6kGyWUvNXBx5nXpQTvjreertoQ6rM4g
GEMINI_API_KEY=AIzaSyCE6kGyWUvNXBx5nXpQTvjreertoQ6rM4g
DEEPGRAM_API_KEY=ccfe77dabe33e62cd034902e2c3a08eb8d397815
VAPI_API_KEY=e41851f4-5ecd-40ae-b02d-f30b7a27a9a0
VAPI_PHONE_NUMBER_ID=e1b0749d-0d3e-48b8-8490-704a27cc5b7d
VAPI_ASSISTANT_ID=5fe73190-7653-47bd-b3fc-e49e1888f3eb
SECRET_KEY=your-secret-key-change-this-in-production
DEBUG=True
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173
```

#### Initialize Database
```bash
# From backend directory
python scripts/init_db.py
```

#### Run Backend Server
```bash
cd /Users/harjyot/Desktop/code/roblox/ai-atl-25/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### 2. Frontend Setup

#### Install Dependencies
```bash
cd /tmp/memory-frontend
npm install
```

#### Environment Configuration
The `.env` file has been created at `/tmp/memory-frontend/client/.env`:

```env
VITE_BACKEND_URL=http://localhost:8000
VITE_DEEPGRAM_API_KEY=ccfe77dabe33e62cd034902e2c3a08eb8d397815
VITE_USER_ID=1
```

#### Run Frontend Development Server
```bash
cd /tmp/memory-frontend
npm run dev
```

The frontend will be available at: http://localhost:5173

## Integration Architecture

### API Service Layer
A comprehensive API service layer was created at `/tmp/memory-frontend/client/src/lib/api.ts` that:
- Handles all backend communication
- Transforms backend responses to match frontend schema
- Provides type-safe methods for all backend endpoints
- Manages authentication and error handling

### Key Integrations

#### 1. Face Recognition Flow
```
Frontend → api.partners.searchByFace(imageFile) → Backend Face Recognition
     ↓
  Match Found?
     ├─ Yes → Use existing partner
     └─ No  → api.partners.createWithImage() → Create new partner
```

#### 2. Live Session Flow
```
User → Start Live Session
  ├─ Start camera (browser getUserMedia)
  ├─ Capture photo → api.sessions.camera.captureFace()
  ├─ Identify person → Backend returns partner_id
  ├─ Start session → api.sessions.start(partnerId, deepgramApiKey)
  ├─ Record audio (Web Speech API - browser-based)
  ├─ Display live transcript
  └─ Stop session → api.sessions.stop(sessionId)
       └─ Backend creates conversation & analyzes with Gemini
```

#### 3. Conversation Analysis Flow
```
Conversation Created → api.conversations.analyze(conversationId)
  ↓
Backend Gemini Analysis
  ├─ Extract facts (interests, work, personal)
  ├─ Identify topics
  ├─ Generate summary
  ├─ Calculate sentiment
  └─ Store in database
```

## Updated Components

### 1. LiveSession Component
**File**: `/tmp/memory-frontend/client/src/components/LiveSession.tsx`

**Backend Integration**:
- Face capture and recognition via `api.partners.searchByFace()`
- Automatic partner creation with `api.partners.createWithImage()`
- Conversation creation with messages via `api.conversations.create()`
- AI analysis via `api.conversations.analyze()`

**Note**: Currently using browser-based speech recognition (Web Speech API) instead of backend Deepgram sessions. To use backend transcription:
1. Start backend session: `api.sessions.start(partnerId, deepgramApiKey)`
2. Poll for transcripts: `api.sessions.getTranscripts(sessionId)`
3. Stop session: `api.sessions.stop(sessionId)`

### 2. Dashboard Component
**File**: `/tmp/memory-frontend/client/src/pages/Dashboard.tsx`

**Backend Integration**:
- Fetch conversations: `api.conversations.list()`
- Fetch stats: `api.stats.get()`
- Photo upload with face recognition
- Demo conversation creation with full message flow

### 3. API Service
**File**: `/tmp/memory-frontend/client/src/lib/api.ts`

**Endpoints Mapped**:
- Partners (Person management)
- Conversations
- Sessions (Camera + Live transcription)
- Profiles (AI analysis & insights)
- Suggestions
- Search (Gemini web search)
- Calls (Vapi voice calls)
- Stats (aggregated)
- Insights (aggregated)

## Database Schema Mapping

### Backend (DuckDB) → Frontend (PostgreSQL expectation)

| Backend Table | Frontend Table | Mapping |
|---|---|---|
| `conversation_partners` | `persons` | Direct mapping with ID transformation |
| `conversations` | `conversations` | Direct mapping with schema transformation |
| `messages` | N/A (embedded in conversations) | Extracted from backend |
| `extracted_facts` | `conversation_details` | Transformed and aggregated |
| `topics` | N/A (stored as array in conversations) | Extracted from conversation_topics |

### Key Transformations
- **IDs**: Backend uses INTEGER, frontend expects VARCHAR (UUID) → Converted with `String(id)`
- **Embeddings**: Backend stores as JSON arrays (4096-dim) → Used for face matching
- **Facts**: Backend normalizes into `extracted_facts` table → Frontend expects in `conversation_details`
- **Topics**: Backend uses many-to-many relation → Frontend expects string array

## API Endpoints Reference

### Partners (Person Management)
- `GET /api/partners?user_id=1` - List all partners
- `POST /api/partners` - Create partner
- `POST /api/partners/{id}/upload-image` - Upload face image
- `POST /api/partners/search-by-face` - Search by face (Form: image, threshold)
- `POST /api/partners/create-with-image` - Create partner with image

### Conversations
- `GET /api/conversations?user_id=1` - List conversations
- `GET /api/conversations/{id}` - Get conversation with details
- `POST /api/conversations` - Create conversation with messages
- `POST /api/conversations/{id}/analyze` - Analyze with Gemini AI
- `DELETE /api/conversations/{id}` - Delete conversation

### Sessions (Camera & Live Recording)
- `GET /api/sessions/camera/list` - List available cameras
- `POST /api/sessions/camera/start` - Start camera
- `POST /api/sessions/camera/stop` - Stop camera
- `GET /api/sessions/camera/status` - Get camera status
- `GET /api/sessions/camera/frame` - Get current frame (JPEG)
- `POST /api/sessions/camera/capture-face` - Capture & identify face
- `POST /api/sessions/start` - Start live session with Deepgram
- `POST /api/sessions/stop/{id}` - Stop session & save
- `GET /api/sessions/list` - List active sessions
- `GET /api/sessions/{id}` - Get session details
- `GET /api/sessions/{id}/transcripts` - Get live transcripts

### Profiles (AI Insights)
- `GET /api/profiles/{partner_id}` - Get partner profile
- `GET /api/profiles/{partner_id}/insights` - Get AI insights
- `POST /api/profiles/{partner_id}/analyze-all` - Batch analyze

### Suggestions
- `GET /api/suggestions/{partner_id}` - Get conversation starters
- `GET /api/suggestions/{partner_id}/facts` - Get extracted facts

### Search (Gemini)
- `POST /api/search/gemini` - Streaming web search with AI
- `GET /api/search/health` - Health check

### Calls (Vapi)
- `POST /api/calls/create` - Create AI voice call
- `POST /api/calls/create-with-context` - Call with conversation context
- `GET /api/calls/{id}` - Get call details
- `GET /api/calls?limit=10` - List recent calls

## Features Available

### ✅ Fully Integrated
- Photo upload and face recognition
- Partner (person) management
- Conversation creation and listing
- AI conversation analysis (Gemini)
- Dashboard statistics
- Demo conversation generation

### ⚠️ Partially Integrated
- Live sessions: Frontend uses browser speech recognition, backend Deepgram sessions available but not connected
- Camera management: Backend supports OBS Virtual Camera, frontend uses browser getUserMedia

### 📝 Pending Integration
- ConversationDetail page → Backend conversation and profile APIs
- Insights page → Backend profile insights and analytics
- Gemini search integration in frontend UI
- Vapi phone call triggering from frontend
- Real-time transcript polling from backend sessions

## Testing the Integration

### 1. Start Backend
```bash
cd /Users/harjyot/Desktop/code/roblox/ai-atl-25/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### 2. Start Frontend
```bash
cd /tmp/memory-frontend
npm run dev
```

### 3. Test Face Recognition
1. Go to http://localhost:5173
2. Click "Upload Photo"
3. Upload a photo of a person
4. Backend will search for matches
5. If no match, creates new partner with face embedding
6. Creates conversation

### 4. Test Live Session
1. Click "Start Live Session"
2. Allow camera and microphone access
3. Start recording → Captures face automatically
4. Speak naturally → Browser transcribes
5. Stop & Complete → Sends to backend for analysis

### 5. Test Demo Conversation
1. Click "Demo" button
2. Backend creates partner "Sarah Johnson"
3. Creates conversation with 8 sample messages
4. Analyzes with Gemini AI
5. Extracts facts, topics, sentiment

## Troubleshooting

### CORS Errors
Ensure backend `.env` includes frontend origin:
```env
ALLOWED_ORIGINS=http://localhost:5173
```

### API Key Issues
Check that all API keys are set in backend `.env`:
- `GOOGLE_API_KEY` - Gemini AI
- `DEEPGRAM_API_KEY` - Live transcription
- `VAPI_API_KEY` - Voice calls

### Database Errors
Initialize database:
```bash
cd /Users/harjyot/Desktop/code/roblox/ai-atl-25/backend
python scripts/init_db.py
```

### Face Recognition Not Working
1. Check image format (JPEG/PNG)
2. Ensure face is clearly visible
3. Check backend logs for DeepFace errors
4. Verify OpenCV and DeepFace are installed

## Next Steps

### High Priority
1. ✅ Complete ConversationDetail page integration
2. ✅ Complete Insights page integration
3. ✅ Add Gemini search UI component
4. ✅ Connect backend Deepgram sessions to frontend
5. ✅ Add real-time transcript polling

### Future Enhancements
- WebSocket for real-time transcripts
- User authentication system
- Multi-user support
- Export conversations to various formats
- Mobile app with React Native

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React + Vite)                 │
│                     http://localhost:5173                    │
├─────────────────────────────────────────────────────────────┤
│  Components:                                                │
│  ├─ Dashboard → api.conversations.list()                    │
│  ├─ LiveSession → api.partners.searchByFace()               │
│  ├─ PhotoCapture → api.partners.createWithImage()           │
│  └─ ConversationDetail → api.conversations.get()            │
│                                                             │
│  API Service Layer (api.ts):                                │
│  ├─ Partners API                                            │
│  ├─ Conversations API                                       │
│  ├─ Sessions API                                            │
│  ├─ Profiles API                                            │
│  └─ Search API                                              │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP/REST
                   │ (CORS enabled)
┌──────────────────▼──────────────────────────────────────────┐
│                  Backend (FastAPI)                          │
│                  http://localhost:8000                       │
├─────────────────────────────────────────────────────────────┤
│  API Routers:                                               │
│  ├─ /api/partners → Partner management                      │
│  ├─ /api/conversations → Conversation CRUD                  │
│  ├─ /api/sessions → Camera + Live sessions                  │
│  ├─ /api/profiles → AI analysis                             │
│  ├─ /api/search → Gemini search                             │
│  └─ /api/calls → Vapi voice calls                           │
│                                                             │
│  Services:                                                  │
│  ├─ FaceRecognitionService (DeepFace)                       │
│  ├─ SessionManager (Deepgram + PyAudio)                     │
│  ├─ GeminiService (AI analysis)                             │
│  ├─ ConversationService (Business logic)                    │
│  └─ CameraManager (OpenCV + OBS)                            │
│                                                             │
│  Database: DuckDB (conversation_ai.db)                      │
│  ├─ conversation_partners                                   │
│  ├─ conversations                                           │
│  ├─ messages                                                │
│  ├─ extracted_facts                                         │
│  └─ topics                                                  │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              External Services                              │
├─────────────────────────────────────────────────────────────┤
│  ├─ Google Gemini → AI analysis & embeddings                │
│  ├─ Deepgram → Live audio transcription                     │
│  ├─ DeepFace → Face recognition (Facenet512)                │
│  └─ Vapi → Voice AI phone calls                             │
└─────────────────────────────────────────────────────────────┘
```

## File Structure

```
ai-atl-25/
├── backend/
│   ├── app/
│   │   ├── api/          # API route handlers
│   │   ├── core/         # Config & database
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── utils/        # Helpers
│   ├── scripts/          # Database init scripts
│   ├── .env             # Environment variables (created)
│   └── requirements.txt  # Python dependencies

memory-frontend/
├── client/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── lib/
│   │   │   ├── api.ts   # Backend API service (NEW)
│   │   │   └── queryClient.ts
│   │   └── hooks/
│   ├── .env             # Frontend environment (created)
│   └── .env.example     # Example config (created)
├── shared/              # Shared types
└── vite.config.ts       # Vite configuration
```

## Support

For issues or questions:
1. Check backend logs: `uvicorn` output
2. Check frontend console: Browser DevTools
3. Verify API endpoints: http://localhost:8000/docs
4. Review this integration guide

## Credits

- Backend: AI-ATL-25 team
- Frontend: Memory project contributors
- Integration: Claude Code
