# AI Conversation Assistant

An intelligent conversation enhancement application that analyzes past conversations to provide contextual suggestions, topics, and questions for better communication.

## Features

- Extract valuable information from conversations using Google Gemini AI
- Store and organize conversation history with intelligent indexing
- Semantic search through past conversations
- Generate personalized conversation starters and questions
- Track evolving information about conversation partners
- Vector embeddings for context-aware suggestions

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Primary database with pgvector extension
- **Google Gemini AI** - Conversation analysis and extraction
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migrations

### Frontend
- **React** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Axios** - HTTP client

## Project Structure

```
ai-atl-25/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core configuration
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── main.py       # FastAPI app
│   ├── alembic/          # Database migrations
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── App.tsx
│   └── package.json
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ with pgvector extension
- Google Cloud account with Gemini API access

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
alembic upgrade head
```

6. Run the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
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

The app will be available at `http://localhost:3000`

## Database Schema

### Core Tables
- **users** - User accounts
- **conversation_partners** - People users converse with
- **conversations** - Conversation sessions
- **messages** - Individual messages
- **extracted_facts** - Key information extracted from conversations
- **topics** - Discussion topics
- **conversation_embeddings** - Vector embeddings for semantic search

## API Endpoints

### Conversations
- `POST /api/conversations` - Create new conversation
- `GET /api/conversations` - List conversations
- `GET /api/conversations/{id}` - Get conversation details
- `POST /api/conversations/{id}/analyze` - Analyze conversation with Gemini

### Suggestions
- `GET /api/suggestions/{partner_id}` - Get conversation suggestions
- `GET /api/topics/{partner_id}` - Get relevant topics

### Facts
- `GET /api/facts/{partner_id}` - Get extracted facts about a person

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/conversation_ai

# Google Gemini
GOOGLE_API_KEY=your_gemini_api_key

# Application
SECRET_KEY=your_secret_key
DEBUG=True
```

## License

MIT
