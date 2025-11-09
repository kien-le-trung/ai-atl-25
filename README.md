# AI Conversation Assistant - Integrated Full-Stack Application

An intelligent conversation enhancement application that analyzes past conversations to provide contextual suggestions, topics, and questions for better communication. This project combines a **modern React/TypeScript frontend** (from [phelpsj1/memory](https://github.com/phelpsj1/memory)) with a **FastAPI Python backend**.

## 🎯 Features

### Frontend (Memory UI)
- 🎨 **Modern Dashboard**: Beautiful, responsive UI with conversation cards
- ⏱️ **Timeline View**: Visual timeline of all conversations  
- 📊 **Insights Analytics**: Track talk ratios, sentiment, and conversation topics
- 📷 **Photo Capture**: Upload photos to create or match conversation partners
- 🎥 **Live Sessions**: Real-time conversation tracking
- ⚙️ **Settings Management**: Configure your preferences

### Backend (FastAPI)
- 🤖 Extract valuable information from conversations using Google Gemini AI
- 💾 Store and organize conversation history with intelligent indexing
- 🔍 Semantic search through past conversations
- 💡 Generate personalized conversation starters and questions
- 📈 Track evolving information about conversation partners
- 🧠 Vector embeddings for context-aware suggestions

## 🛠️ Tech Stack

### Frontend
- **React 18** + **TypeScript** - Modern UI framework
- **Vite** - Fast build tool and dev server
- **TanStack Query** - Data fetching and caching
- **Tailwind CSS** - Utility-first styling
- **Radix UI** - Accessible components
- **Framer Motion** - Smooth animations
- **Recharts** - Data visualization

### Backend
- **FastAPI** - High-performance Python web framework
- **SQLAlchemy** - ORM for database operations
- **DuckDB / PostgreSQL** - Database with vector support
- **Google Gemini AI** - Conversation analysis
- **Alembic** - Database migrations

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- DuckDB (included) or PostgreSQL 15+ with pgvector
- Google Cloud account with Gemini API access

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/kien-le-trung/ai-atl-25.git
cd ai-atl-25

# Install frontend dependencies
npm install

# Install backend dependencies
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### 2. Configure Environment

```bash
# Backend configuration
cd backend
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Initialize database
alembic upgrade head
cd ..
```

### 3. Run the Application

**Option A: Run Both Services (Recommended)**

Open two terminal windows:

**Terminal 1 - Backend (port 8000):**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend (port 3000):**
```bash
npm run dev
```

Then open your browser to `http://localhost:3000`

**Option B: Use the Startup Script**
```bash
# Coming soon: ./start.sh (will start both services)
```

## 📁 Project Structure

```
ai-atl-25/
├── frontend/           # React TypeScript frontend
│   ├── src/
│   │   ├── components/ # UI components
│   │   ├── pages/      # Page components (Dashboard, Timeline, Insights, etc.)
│   │   ├── hooks/      # Custom React hooks
│   │   ├── lib/        # Utilities (queryClient, etc.)
│   │   └── main.tsx    # Entry point
│   ├── public/         # Static assets
│   └── index.html      # HTML template
├── backend/            # FastAPI Python backend
│   ├── app/
│   │   ├── api/        # API endpoints
│   │   │   ├── memory.py      # Frontend integration endpoints
│   │   │   ├── conversations.py
│   │   │   ├── partners.py
│   │   │   └── ...
│   │   ├── core/       # Configuration
│   │   ├── models/     # Database models
│   │   ├── schemas/    # Pydantic schemas
│   │   ├── services/   # Business logic
│   │   └── main.py     # FastAPI app
│   ├── alembic/        # Database migrations
│   └── requirements.txt
├── shared/             # Shared TypeScript types
├── package.json        # Frontend dependencies
├── vite.config.ts      # Vite configuration (includes API proxy)
├── tsconfig.json       # TypeScript configuration
└── README.md           # This file
```

## 🔌 API Endpoints

### Frontend Integration API (`/api/*`)
- `GET /api/stats` - Dashboard statistics
- `GET /api/conversations` - List conversations with person info
- `GET /api/conversations/{id}` - Get specific conversation
- `POST /api/photo-upload` - Upload photo and create/match person
- `POST /api/persons` - Create new person
- `GET /api/insights` - Analytics insights

### Core Backend API  
- `POST /api/conversations` - Create conversation
- `GET /api/partners` - List conversation partners
- `POST /api/conversations/{id}/analyze` - Analyze with Gemini AI
- `GET /api/suggestions/{partner_id}` - Get suggestions
- `GET /api/topics/{partner_id}` - Get relevant topics

Full API documentation available at: `http://localhost:8000/docs`

## 🏗️ Development

### Frontend Development
```bash
npm run dev      # Start dev server
npm run build    # Build for production
npm run preview  # Preview production build
npm run check    # TypeScript type checking
```

### Backend Development
```bash
cd backend
# With virtual environment activated:
uvicorn app.main:app --reload  # Start with auto-reload
pytest                          # Run tests
alembic revision --autogenerate -m "description"  # Create migration
alembic upgrade head           # Run migrations
```

### How It Works
The Vite dev server proxies all `/api/*` requests to the FastAPI backend at `http://localhost:8000`. This is configured in `vite.config.ts`:

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

## 📚 Documentation

- [SETUP_GUIDE.md](./SETUP_GUIDE.md) - Detailed setup instructions
- [WEB_INTERFACE_GUIDE.md](./WEB_INTERFACE_GUIDE.md) - Frontend usage guide  
- [META_GLASSES_GUIDE.md](./META_GLASSES_GUIDE.md) - Meta glasses integration
- [DATABASE_ER_DIAGRAM.md](./DATABASE_ER_DIAGRAM.md) - Database schema
- [QUICK_START.md](./QUICK_START.md) - Quick start guide
- [README_INTEGRATED.md](./README_INTEGRATED.md) - Full integration details

## 🔐 Environment Variables

See `backend/.env.example` for all available configuration options.

Key variables:
```env
DATABASE_URL=duckdb:///./conversation_ai.db
GOOGLE_API_KEY=your_api_key_here
ALLOWED_ORIGINS=http://localhost:3000
DEBUG=True
```

## 🧪 Testing

### Frontend
```bash
npm run check    # TypeScript validation
npm run build    # Build verification
```

### Backend
```bash
cd backend
pytest           # Run all tests
pytest tests/api # Run API tests only
```

## 📦 Production Deployment

### Frontend
```bash
npm run build
# Serve the `dist` folder with your static file server
```

### Backend
```bash
# Use Gunicorn with Uvicorn workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

MIT

## 🙏 Credits

- **Frontend**: Based on [Memory](https://github.com/phelpsj1/memory) by phelpsj1
- **Backend**: FastAPI implementation by kien-le-trung
- **Integration**: Combined full-stack application
