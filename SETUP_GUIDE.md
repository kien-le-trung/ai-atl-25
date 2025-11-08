# Quick Setup Guide

## Prerequisites

1. **Python 3.11+** - [Download](https://www.python.org/downloads/)
2. **Node.js 18+** - [Download](https://nodejs.org/)
3. **PostgreSQL 15+** - [Download](https://www.postgresql.org/download/)
4. **Google Gemini API Key** - [Get one here](https://makersuite.google.com/app/apikey)

## Step 1: Database Setup

1. Install PostgreSQL and pgvector extension:
```bash
# On Windows with PostgreSQL installed:
# Open pgAdmin or psql and run:
CREATE DATABASE conversation_ai;

# Connect to the database and enable pgvector:
\c conversation_ai
CREATE EXTENSION vector;
```

## Step 2: Backend Setup

1. Open a terminal in the `backend` folder:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
copy .env.example .env
```

5. Edit `.env` file with your settings:
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/conversation_ai
GOOGLE_API_KEY=your_gemini_api_key_here
SECRET_KEY=any-random-secret-key
DEBUG=True
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000
```

6. Run database migrations:
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

7. Start the backend server:
```bash
uvicorn app.main:app --reload
```

The API should now be running at `http://localhost:8000`
API docs available at `http://localhost:8000/docs`

## Step 3: Frontend Setup

1. Open a NEW terminal in the `frontend` folder:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The app should open automatically at `http://localhost:3000`

## How to Use

### 1. Add a Contact
- Click the "+" button in the sidebar
- Enter the person's name and email
- Click "Create Contact"

### 2. Add a Conversation
- Select a contact from the sidebar
- Click "New Conversation"
- Add messages alternating between you and your partner
- Click "Save & Analyze"

The AI will automatically:
- Extract key facts about the person
- Identify main topics discussed
- Generate a summary
- Create conversation suggestions

### 3. Get Suggestions
- Click on the "Suggestions" tab to see:
  - Conversation starters
  - Follow-up questions
  - New topic ideas

- Click on the "Known Facts" tab to see:
  - All extracted information about the person
  - Confidence scores for each fact
  - When each fact was discovered

## Architecture Overview

### How It Answers Your Questions:

**1. Extracting Valuable Information (Question 1)**
- After each conversation, Gemini analyzes the entire exchange
- Extracts structured data: facts, topics, sentiment, insights
- Categories include: interests, preferences, life events, work, personal
- Each fact has a confidence score (0-1)

**2. Integrating New with Existing Information (Question 2)**
- Each conversation is stored separately (never overwritten)
- Facts are appended with timestamps
- Vector embeddings enable semantic search across all conversations
- The system tracks fact evolution (e.g., preference changes)
- Uses `is_current` flag to mark superseded information

**3. Database Design for Easy Extraction (Question 3)**

**Core Tables:**
- `users` - User accounts
- `conversation_partners` - People you talk to
- `conversations` - Conversation sessions with embeddings
- `messages` - Individual messages
- `extracted_facts` - Categorized facts with confidence scores
- `topics` - Discussion topics (many-to-many with conversations)

**Key Features:**
- **Vector embeddings** (768-dimensional) for semantic similarity search
- **Categorized facts** for easy filtering and retrieval
- **Confidence scores** to prioritize reliable information
- **Temporal tracking** to see how information evolves
- **Topic tagging** for quick context retrieval

## API Endpoints

### Partners
- `POST /api/partners` - Create contact
- `GET /api/partners` - List all contacts
- `GET /api/partners/{id}` - Get specific contact

### Conversations
- `POST /api/conversations` - Create conversation
- `GET /api/conversations?partner_id={id}` - List conversations
- `POST /api/conversations/{id}/analyze` - Analyze with AI

### Suggestions
- `GET /api/suggestions/{partner_id}` - Get suggestions
- `GET /api/suggestions/{partner_id}/facts` - Get all facts

## Troubleshooting

**Database Connection Error:**
- Make sure PostgreSQL is running
- Check DATABASE_URL in `.env`
- Verify pgvector extension is installed

**Gemini API Error:**
- Verify your GOOGLE_API_KEY is correct
- Check you have API quota available
- Ensure you're using the correct model name

**CORS Error:**
- Check ALLOWED_ORIGINS in `.env` includes `http://localhost:3000`
- Restart the backend server after changing `.env`

## Next Steps

1. **Add Authentication**: Implement user login/signup
2. **Real-time Sync**: Add WebSocket for live updates
3. **Mobile App**: Create React Native version
4. **Voice Input**: Add speech-to-text for conversations
5. **Reminders**: Set reminders for important facts
6. **Export**: Export conversation history as PDF

## Support

For issues or questions, refer to:
- FastAPI docs: https://fastapi.tiangolo.com
- Gemini API docs: https://ai.google.dev/docs
- React docs: https://react.dev
