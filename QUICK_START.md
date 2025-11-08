# Quick Start - Meta Glasses Integration

Get started with conversation tracking using Meta Ray-Ban glasses in 5 minutes.

## Prerequisites

- ✅ Meta Ray-Ban glasses connected to OBS
- ✅ OBS Virtual Camera running
- ✅ Python 3.11+ installed
- ✅ Deepgram API key
- ✅ Google Gemini API key

## Setup (One-time)

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env and add your API keys:
# - GOOGLE_API_KEY=your_gemini_key
# - DEEPGRAM_API_KEY=your_deepgram_key

# 3. Initialize database
python3 init_db.py
python3 create_test_user.py
```

## Quick Test (CLI)

```bash
cd backend
python3 meta_glasses_cli.py

# Try these in order:
[1] List cameras           # Find your OBS camera (usually index 2 or higher)
[2] Start camera preview   # Verify video feed works
[3] Capture face          # Take a photo, identify/create person
[4] Start session         # Record conversation with transcription
[5] Analyze conversation  # Extract facts and topics
[6] View profile          # See accumulated insights
```

## Quick Test (API)

```bash
# Terminal 1: Start API server
cd backend
uvicorn app.main:app --reload

# Terminal 2: Test endpoints
# 1. Start camera
curl -X POST http://localhost:8000/api/sessions/camera/start \
  -H "Content-Type: application/json" \
  -d '{"camera_index": 2}'

# 2. Capture face
curl -X POST "http://localhost:8000/api/sessions/camera/capture-face?user_id=1"

# 3. Start conversation session
curl -X POST http://localhost:8000/api/sessions/start \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "partner_id": 2,
    "deepgram_api_key": "YOUR_DEEPGRAM_KEY"
  }'

# Speak into microphone...

# 4. Stop session (use session_id from step 3)
curl -X POST http://localhost:8000/api/sessions/stop/SESSION_ID

# 5. Analyze conversation (use conversation_id from step 3)
curl -X POST http://localhost:8000/api/profiles/analyze-conversation \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": 1,
    "gemini_api_key": "YOUR_GEMINI_KEY"
  }'

# 6. View profile
curl http://localhost:8000/api/profiles/2
```

## Typical Workflow

```
1. Put on Meta glasses
2. Start OBS Virtual Camera
3. Run CLI: python3 meta_glasses_cli.py
4. Capture person's face [3]
5. Start conversation session [4]
6. Talk normally - everything is transcribed
7. Press Enter to stop
8. Analyze conversation [5]
9. View accumulated profile [6]
```

## What Gets Captured

### During Face Capture
- Face image saved to `uploads/faces/`
- 4096-dim embedding stored in database
- Automatic identification if person seen before
- Creates new partner entry if new person

### During Conversation
- Real-time audio transcription (Deepgram)
- Each transcript saved as message
- All messages linked to conversation
- Session statistics tracked

### During Analysis
- Facts extracted (name, occupation, interests, preferences, etc.)
- Topics identified (work, hobbies, food, etc.)
- Conversation summary generated
- All saved to partner profile

### In Profile
- Aggregated facts from all conversations
- All topics discussed over time
- Conversation history and statistics
- AI-generated suggestions for future talks

## File Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── sessions.py      # Camera & session endpoints
│   │   └── profiles.py      # Profile & analysis endpoints
│   ├── services/
│   │   ├── camera_service.py    # OBS camera & face detection
│   │   ├── session_service.py   # Audio transcription
│   │   └── profile_service.py   # AI analysis
│   └── models/              # Database models
├── meta_glasses_cli.py      # Interactive CLI tool
├── conversation_ai.db       # Your data (DuckDB)
└── uploads/faces/           # Captured face images
```

## Troubleshooting

### "No camera found"
- Check OBS Virtual Camera is started
- Try different index in [1] List cameras
- Restart OBS if needed

### "No face detected"
- Improve lighting
- Face person directly
- Move closer (3-6 feet)
- Check camera preview first [2]

### "No transcription"
- Check microphone permissions
- Verify Deepgram API key in .env
- Test mic: `pyaudio` should see devices

### "Failed to start session"
- Ensure user exists (run create_test_user.py)
- Check partner was created (option [3] first)
- Verify Deepgram API key is valid

## API Documentation

Full interactive API docs: http://localhost:8000/docs

## Complete Guide

See [META_GLASSES_GUIDE.md](META_GLASSES_GUIDE.md) for:
- Detailed architecture
- All API endpoints
- Advanced usage
- Performance tips
- Custom integration examples

## Cost Estimate

| Service | Usage | Cost |
|---------|-------|------|
| Deepgram | 10 min conversation | ~$0.13 |
| Google Gemini | 1 conversation analysis | ~$0.001-0.01 |
| **Total per conversation** | | **~$0.14** |

Free tiers available:
- Deepgram: $200 credit on signup
- Gemini: 60 requests/minute free tier

## Support

1. Test components individually using CLI
2. Check logs for errors
3. Verify API keys are active
4. See [META_GLASSES_GUIDE.md](META_GLASSES_GUIDE.md) for details

---

**Ready to start?** Run `python3 meta_glasses_cli.py` and select option [1] to find your camera!
