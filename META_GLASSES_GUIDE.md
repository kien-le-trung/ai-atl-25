## Meta Glasses Integration Guide

Complete guide for using Meta Ray-Ban glasses with OBS Virtual Camera for conversation tracking, face recognition, and profile building.

## Overview

This system allows you to:
1. **Capture faces** from Meta glasses video feed (via OBS Virtual Camera)
2. **Identify people** using face recognition with DeepFace
3. **Track conversations** with live audio transcription using Deepgram
4. **Build profiles** automatically from conversation analysis using Google Gemini AI
5. **Get insights** and suggestions for future conversations

## Architecture

```
Meta Ray-Ban Glasses
      ↓
OBS Virtual Camera
      ↓
Camera Service (OpenCV) ←→ Face Recognition (DeepFace)
      ↓                           ↓
Session Service ←→ Deepgram API (Transcription)
      ↓                           ↓
   Database (DuckDB) ←→ Profile Builder (Gemini AI)
```

## Prerequisites

### Hardware
- Meta Ray-Ban glasses
- Computer with OBS installed
- Microphone (can be from Meta glasses or separate)

### Software
1. **OBS Studio** - For Meta glasses video feed
2. **Python 3.11+**
3. **Dependencies** - Install with:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

### API Keys Required
1. **Deepgram API Key** - For live transcription ([Get it here](https://deepgram.com))
2. **Google Gemini API Key** - For conversation analysis ([Get it here](https://makersuite.google.com/app/apikey))

## Setup

### 1. Configure Meta Glasses with OBS

1. **Connect Meta Glasses to Computer**
   - Connect via USB or use Meta View app to stream

2. **Set up OBS Virtual Camera**
   - Open OBS Studio
   - Add your Meta glasses as a video source
   - Start Virtual Camera (Tools → Start Virtual Camera)

3. **Verify Camera**
   ```bash
   cd backend
   python3 meta_glasses_cli.py
   # Select option [1] to list cameras
   # Note the OBS Virtual Camera index (usually last one)
   ```

### 2. Configure Environment

1. **Copy environment template**
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Edit .env file**
   ```bash
   # Database (already configured for DuckDB)
   DATABASE_URL=duckdb:///./conversation_ai.db

   # Google Gemini API
   GOOGLE_API_KEY=your_actual_gemini_key_here

   # Deepgram API
   DEEPGRAM_API_KEY=your_actual_deepgram_key_here

   # Other settings (can keep defaults)
   SECRET_KEY=your-secret-key
   DEBUG=True
   ```

### 3. Initialize Database

```bash
cd backend
python3 init_db.py
python3 create_test_user.py
```

This creates:
- All required database tables
- A test user (ID: 1, email: test@example.com, password: test123)

## Usage

### Method 1: Using the CLI Tool (Recommended for Testing)

The CLI tool provides an interactive interface for all features:

```bash
cd backend
python3 meta_glasses_cli.py --user-id 1
```

**Interactive Menu:**
```
[1] List cameras              - Find OBS Virtual Camera index
[2] Start camera preview      - Test camera feed
[3] Capture and identify face - Take photo and identify person
[4] Start conversation session - Begin audio transcription
[5] Analyze conversation      - Extract facts and topics
[6] View partner profile      - See accumulated insights
[q] Quit
```

### Method 2: Using the API

Start the FastAPI server:

```bash
cd backend
uvicorn app.main:app --reload
```

Access API documentation at: http://localhost:8000/docs

## Complete Workflow Example

### Step 1: Capture a Face

**Via CLI:**
```
1. Start CLI: python3 meta_glasses_cli.py
2. Select [3] Capture and identify face
3. Press SPACE when person's face is visible
4. Enter their name if new person
```

**Via API:**
```bash
# Start camera
curl -X POST http://localhost:8000/api/sessions/camera/start \
  -H "Content-Type: application/json" \
  -d '{"camera_index": 2}'

# Capture face
curl -X POST http://localhost:8000/api/sessions/camera/capture-face?user_id=1
```

**Response:**
```json
{
  "success": true,
  "partner_id": 2,
  "partner_name": "John Doe",
  "is_new_partner": true,
  "face_detected": true,
  "similarity_score": null,
  "message": "New partner created: John Doe"
}
```

### Step 2: Start a Conversation Session

**Via CLI:**
```
1. Select [4] Start conversation session
2. Choose the partner from the list
3. Speak into your microphone
4. Press Enter when done
```

**Via API:**
```bash
curl -X POST http://localhost:8000/api/sessions/start \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "partner_id": 2,
    "deepgram_api_key": "your_deepgram_key"
  }'
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 1,
  "partner_id": 2,
  "conversation_id": 5,
  "is_running": true,
  "elapsed_seconds": 0.5,
  "elapsed_formatted": "00:00:00",
  "message_count": 0
}
```

**During the session**, all speech is automatically:
- Transcribed by Deepgram
- Saved as messages in the database
- Associated with the conversation

### Step 3: Stop the Session

**Via API:**
```bash
curl -X POST http://localhost:8000/api/sessions/stop/550e8400-e29b-41d4-a716-446655440000
```

### Step 4: Analyze the Conversation

**Via CLI:**
```
1. Select [5] Analyze conversation
2. Choose the conversation from the list
3. Wait for AI analysis
```

**Via API:**
```bash
curl -X POST http://localhost:8000/api/profiles/analyze-conversation \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": 5,
    "gemini_api_key": "your_gemini_key"
  }'
```

**Response:**
```json
{
  "conversation_id": 5,
  "facts_extracted": 12,
  "topics_identified": 5,
  "summary": "Discussion about work projects, weekend plans, and favorite restaurants. Mentioned interest in hiking and photography."
}
```

**What gets extracted:**
- **Facts**: Personal details, preferences, interests, goals
- **Topics**: Main subjects discussed
- **Summary**: AI-generated conversation summary

### Step 5: View Partner Profile

**Via CLI:**
```
1. Select [6] View partner profile
2. Choose the partner
3. See accumulated facts, topics, and AI suggestions
```

**Via API:**
```bash
# Get full profile
curl http://localhost:8000/api/profiles/2

# Get conversation insights and suggestions
curl http://localhost:8000/api/profiles/2/insights
```

**Profile Response:**
```json
{
  "partner_id": 2,
  "partner_name": "John Doe",
  "statistics": {
    "total_conversations": 3,
    "total_messages": 156,
    "total_facts": 24,
    "topics_count": 12
  },
  "facts": {
    "personal_info": [
      {"key": "occupation", "value": "software engineer", "confidence": 0.95},
      {"key": "location", "value": "San Francisco", "confidence": 0.9}
    ],
    "interests": [
      {"key": "hobby", "value": "photography", "confidence": 0.85},
      {"key": "hobby", "value": "hiking", "confidence": 0.9}
    ],
    "preferences": [
      {"key": "favorite_cuisine", "value": "Italian", "confidence": 0.8}
    ]
  },
  "topics": ["work", "technology", "photography", "hiking", "food", "travel"],
  "last_conversation": {
    "id": 5,
    "date": "2025-11-08T16:30:00",
    "summary": "Discussion about work projects..."
  }
}
```

**Insights Response:**
```json
{
  "partner_id": 2,
  "partner_name": "John Doe",
  "suggestions": [
    "Ask about recent photography projects or favorite locations",
    "Discuss upcoming hiking trips or trail recommendations",
    "Share Italian restaurant recommendations in the area",
    "Talk about new technology trends or software development tools",
    "Ask about work-life balance strategies"
  ],
  "profile_summary": {
    "facts_count": 24,
    "topics_count": 12,
    "conversations_count": 3
  }
}
```

## API Endpoints Reference

### Camera Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sessions/camera/start` | Start OBS camera feed |
| POST | `/api/sessions/camera/stop` | Stop camera feed |
| GET | `/api/sessions/camera/status` | Get camera status |
| GET | `/api/sessions/camera/frame` | Get current frame as JPEG |
| POST | `/api/sessions/camera/capture-face` | Capture and identify face |

### Session Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sessions/start` | Start conversation session |
| POST | `/api/sessions/stop/{session_id}` | Stop session |
| GET | `/api/sessions/list` | List all active sessions |
| GET | `/api/sessions/{session_id}` | Get session details |
| GET | `/api/sessions/{session_id}/transcripts` | Get live transcripts |

### Profile Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/profiles/analyze-conversation` | Analyze conversation |
| GET | `/api/profiles/{partner_id}` | Get partner profile |
| GET | `/api/profiles/{partner_id}/insights` | Get AI suggestions |
| POST | `/api/profiles/{partner_id}/analyze-all` | Batch analyze all conversations |

## How It Works

### 1. Face Recognition

**Technology**: DeepFace with Facenet512 model

**Process**:
1. Capture frame from OBS Virtual Camera
2. Detect largest face using Haar Cascade
3. Extract 512-dimensional embedding
4. Pad to 4096 dimensions for database storage
5. Calculate cosine similarity with existing partners
6. If similarity > 60%, identify as existing partner
7. Otherwise, create new partner entry

**Accuracy**: ~95% for well-lit, frontal faces

### 2. Live Transcription

**Technology**: Deepgram streaming API

**Process**:
1. Capture audio from microphone (16kHz, mono, 16-bit PCM)
2. Stream to Deepgram WebSocket API
3. Receive real-time transcripts with punctuation
4. Save each transcript as a message in database
5. Associate all messages with conversation session

**Latency**: ~300-500ms from speech to text

### 3. Profile Building

**Technology**: Google Gemini Pro AI

**Process**:
1. Retrieve all messages from conversation
2. Send to Gemini with fact extraction prompt
3. Parse JSON response with structured facts
4. Categorize facts (personal_info, interests, preferences, etc.)
5. Extract main topics discussed
6. Generate conversation summary
7. Save all to database with confidence scores

**Capabilities**:
- Extracts 10-30 facts per conversation on average
- Identifies 3-5 main topics
- Generates concise 2-3 sentence summaries
- Provides conversation suggestions based on history

## Troubleshooting

### Camera Issues

**Problem**: OBS Virtual Camera not detected
```bash
# Solution 1: Check OBS is running and Virtual Camera started
# Solution 2: Try different camera index
python3 meta_glasses_cli.py
# Select [1] to list all cameras

# Solution 3: Specify camera index manually
curl -X POST http://localhost:8000/api/sessions/camera/start \
  -H "Content-Type: application/json" \
  -d '{"camera_index": 2}'  # Try 0, 1, 2, etc.
```

**Problem**: "No face detected"
- Ensure good lighting
- Face person directly toward glasses
- Move closer (within 3-6 feet)
- Check camera preview first (option [2] in CLI)

### Audio Issues

**Problem**: No transcription received
```bash
# Check microphone access
# On Mac: System Preferences → Security & Privacy → Microphone
# Grant permission to Terminal/Python

# Test microphone
python3 -c "import pyaudio; p = pyaudio.PyAudio(); print('Microphones:', p.get_device_count())"

# Verify Deepgram API key
curl -H "Authorization: Token YOUR_KEY" \
  https://api.deepgram.com/v1/projects
```

**Problem**: Poor transcription quality
- Use a better microphone
- Reduce background noise
- Speak clearly and at moderate pace
- Check Deepgram API credits

### Database Issues

**Problem**: "Constraint Error: Violates foreign key"
```bash
# Ensure user exists
python3 create_test_user.py

# Or create via database
python3 -c "from app.core.database import SessionLocal; from app.models.user import User; db = SessionLocal(); print([u.id for u in db.query(User).all()])"
```

**Problem**: "Database locked"
```bash
# DuckDB is single-writer
# Close other connections
pkill -f uvicorn
pkill -f python.*meta_glasses

# Restart
python3 init_db.py --fresh  # WARNING: Deletes all data
```

### API Issues

**Problem**: Import errors
```bash
cd backend
pip install -r requirements.txt --upgrade
```

**Problem**: "Module not found"
```bash
# Ensure you're in backend directory
cd backend
python3 -c "from app.main import app; print('OK')"
```

## Performance Tips

### Face Recognition
- **Speed**: ~2-3 seconds per face capture
- **Accuracy**: Best with frontal faces, good lighting
- **Database**: Searches all stored faces (linear time)
- **Optimization**: For >100 partners, consider vector database (e.g., FAISS)

### Transcription
- **Latency**: 300-500ms typical
- **Cost**: ~$0.0125 per minute of audio (Deepgram pay-as-you-go)
- **Quality**: 90-95% accuracy in quiet environments

### Profile Building
- **Speed**: ~5-10 seconds per conversation (depends on length)
- **Cost**: ~$0.001-0.01 per conversation (Gemini free tier: 60 requests/minute)
- **Recommendation**: Batch analyze conversations (use `/analyze-all` endpoint)

## Advanced Usage

### Batch Processing

Analyze all conversations for a partner:
```bash
curl -X POST http://localhost:8000/api/profiles/2/analyze-all
```

### Custom Integration

```python
from app.services.camera_service import CameraService
from app.services.session_service import session_manager
from app.core.database import SessionLocal

# Initialize
camera = CameraService()
db = SessionLocal()

# Capture face
camera.start_camera()
result = camera.capture_and_identify_face()
# ... handle result

# Start session
session = session_manager.create_session(
    session_id="my-session",
    user_id=1,
    partner_id=2,
    deepgram_api_key="your-key",
    db=db
)

# Monitor transcripts
import time
while True:
    transcripts = session.get_recent_transcripts(max_lines=5)
    for t in transcripts:
        print(f"[{t['timestamp']}] {t['text']}")
    time.sleep(2)
```

### Multi-User Setup

The system supports multiple users:
```bash
# Create additional users
python3 -c "
import bcrypt
from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()
user = User(
    email='alice@example.com',
    username='alice',
    hashed_password=bcrypt.hashpw(b'password', bcrypt.gensalt()).decode('utf-8')
)
db.add(user)
db.commit()
print(f'Created user ID: {user.id}')
"

# Use different user ID
python3 meta_glasses_cli.py --user-id 2
```

## Data Privacy & Security

- **Face embeddings**: Stored as 4096-dim vectors, not reversible to original image
- **Images**: Stored locally in `uploads/faces/` directory
- **Transcripts**: Stored in local DuckDB database
- **API keys**: Never logged or stored in database
- **Backup**: Simply copy `conversation_ai.db` file

## Future Enhancements

Potential improvements:
- [ ] Real-time face tracking during conversations
- [ ] Speaker diarization (identify who said what)
- [ ] Emotion detection from facial expressions
- [ ] Multi-language support
- [ ] Cloud sync for database
- [ ] Mobile app companion
- [ ] Voice activity detection (reduce empty transcripts)
- [ ] Conversation threading (group related sessions)

## Support

For issues or questions:
1. Check logs: `tail -f backend/app.log`
2. Test components individually using CLI
3. Verify API keys are valid
4. Check [DeepFace docs](https://github.com/serengil/deepface)
5. Check [Deepgram docs](https://developers.deepgram.com)

---

**Built with**: FastAPI, DeepFace, Deepgram, Google Gemini, OpenCV, DuckDB
