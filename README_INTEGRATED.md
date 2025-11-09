# AI Conversation Assistant - Integrated Full-Stack Application

An intelligent conversation enhancement application that analyzes past conversations to provide contextual suggestions, topics, and questions for better communication. This project combines a modern React/TypeScript frontend with a FastAPI Python backend.

## Features

### Frontend (Memory UI)
- **Modern Dashboard**: Beautiful, responsive UI with conversation cards
- **Timeline View**: Visual timeline of all conversations
- **Insights Analytics**: Track talk ratios, sentiment, and conversation topics
- **Photo Capture**: Upload photos to create or match conversation partners
- **Live Sessions**: Real-time conversation tracking
- **Settings Management**: Configure your preferences

### Backend (FastAPI)
- Extract valuable information from conversations using Google Gemini AI
- Store and organize conversation history with intelligent indexing
- Semantic search through past conversations
- Generate personalized conversation starters and questions
- Track evolving information about conversation partners
- Vector embeddings for context-aware suggestions

## Tech Stack

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **TanStack Query** - Data fetching and caching
- **Wouter** - Lightweight routing
- **Tailwind CSS** - Utility-first CSS framework
- **Radix UI** - Accessible component primitives
- **Framer Motion** - Animation library
- **Recharts** - Charts and data visualization

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL / DuckDB** - Primary database with pgvector extension
- **Google Gemini AI** - Conversation analysis and extraction
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migrations

## Project Structure

```
ai-atl-25/
├── frontend/           # React TypeScript frontend
│   ├── src/
│   │   ├── components/ # UI components
│   │   ├── pages/      # Page components
│   │   ├── hooks/      # Custom React hooks
│   │   ├── lib/        # Utilities and helpers
│   │   └── main.tsx    # Entry point
│   ├── public/         # Static assets
│   └── index.html      # HTML template
├── backend/            # FastAPI Python backend
│   ├── app/
│   │   ├── api/        # API endpoints
│   │   ├── core/       # Core configuration
│   │   ├── models/     # Database models
│   │   ├── schemas/    # Pydantic schemas
│   │   ├── services/   # Business logic
│   │   └── main.py     # FastAPI app
│   ├── alembic/        # Database migrations
│   └── requirements.txt
├── shared/             # Shared TypeScript types/schemas
├── package.json        # Frontend dependencies
├── vite.config.ts      # Vite configuration
├── tsconfig.json       # TypeScript configuration
└── tailwind.config.ts  # Tailwind CSS configuration
```

## Setup Instructions

### Prerequisites
- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 15+** with pgvector extension (or DuckDB for local development)
- **Google Cloud account** with Gemini API access

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
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. Install dependencies (from project root):
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

The Vite dev server automatically proxies API requests from `/api/*` to `http://localhost:8000/api/*`, so make sure the backend is running.

3. Build for production:
```bash
npm run build
```

4. Preview production build:
```bash
npm run preview
```

## Development Workflow

### Running Both Services

For development, you need both the backend and frontend running:

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

### API Endpoints

The backend provides the following main endpoints:

#### Memory Frontend Endpoints
- `GET /api/stats` - Dashboard statistics
- `GET /api/conversations` - List all conversations with person info
- `GET /api/conversations/{id}` - Get specific conversation
- `POST /api/photo-upload` - Upload photo and create/match person
- `POST /api/persons` - Create new person manually
- `GET /api/insights` - Get analytics insights
- `GET /api/conversation-details/{id}` - Get conversation details
- `GET /api/conversations/{id}/follow-ups` - Get follow-up actions

#### Original Backend Endpoints
- `POST /api/conversations` - Create new conversation
- `GET /api/partners` - List conversation partners
- `POST /api/conversations/{id}/analyze` - Analyze conversation with Gemini
- `GET /api/suggestions/{partner_id}` - Get conversation suggestions
- `GET /api/topics/{partner_id}` - Get relevant topics
- `GET /api/facts/{partner_id}` - Get extracted facts about a person

## Environment Variables

### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost/conversation_ai
# Or for DuckDB (local development)
# DATABASE_URL=duckdb:///./conversation.db

# Google Gemini
GOOGLE_API_KEY=your_gemini_api_key

# Application
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

## Database Schema

### Core Tables
- **users** - User accounts
- **conversation_partners** - People users converse with
- **conversations** - Conversation sessions
- **messages** - Individual messages
- **extracted_facts** - Key information extracted from conversations
- **topics** - Discussion topics
- **conversation_embeddings** - Vector embeddings for semantic search

## Testing

### Frontend Tests
```bash
npm run check  # TypeScript type checking
npm run build  # Build verification
```

### Backend Tests
```bash
cd backend
pytest
```

## Production Deployment

### Frontend
Build the frontend and serve the `dist` folder:
```bash
npm run build
# Serve the dist folder with your preferred static file server
```

### Backend
Use a production ASGI server like Gunicorn with Uvicorn workers:
```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Credits

- **Frontend**: Based on the Memory project by [phelpsj1](https://github.com/phelpsj1/memory)
- **Backend**: FastAPI implementation by kien-le-trung

## License

MIT
