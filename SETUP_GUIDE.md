# Quick Setup Guide

## Prerequisites

1. **Python 3.11+** - [Download](https://www.python.org/downloads/)
2. **Node.js 18+** - [Download](https://nodejs.org/)
3. **Google Gemini API Key** - [Get one here](https://makersuite.google.com/app/apikey)

## Important Notes

- The project now includes **DeepFace** for facial recognition with 4096-dimensional vector embeddings
- TensorFlow will be installed automatically (may take some time)
- First run may download face detection models (~100MB)

## Step 1: Database Setup

The project now uses **DuckDB**, a fast in-process SQL database:
- No separate database server installation required
- Database file (`conversation_ai.db`) will be created automatically
- All data stored locally in a single file
- Perfect for development and small to medium deployments

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
DATABASE_URL=duckdb:///./conversation_ai.db
GOOGLE_API_KEY=your_gemini_api_key_here
SECRET_KEY=any-random-secret-key
DEBUG=True
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000
```

6. Initialize the database:
```bash
# Option 1: Use the initialization script (recommended)
# On Mac/Linux:
python3 init_db.py

# On Windows:
python init_db.py

# Option 2: Use Alembic migrations (if you have migration files)
alembic upgrade head
```

Note: The database file will be created in the backend directory as `conversation_ai.db`

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

### 1. Add a Contact (with Face Recognition)
1. Click the "+" button in the sidebar
2. Enter the person's name
3. (Optional) Enter email and relationship
4. **Upload a face photo** by clicking the camera icon
   - Photo will be automatically processed
   - Face embedding will be extracted and stored
   - Supported formats: JPG, PNG, WebP
5. Click "Create Contact"

**Note:** If no face is detected in the uploaded image, the contact will still be created but without facial recognition capabilities.

### 2. Testing Face Recognition

#### Upload a Photo to Existing Contact:
1. Create a contact without a photo first
2. Use the API endpoint: `POST /api/partners/{partner_id}/upload-image`
3. Or add this feature to the UI later

#### Search by Face (API only for now):
```bash
# Using curl to search for a person by their photo:
curl -X POST "http://localhost:8000/api/partners/search-by-face" \
  -F "image=@path/to/photo.jpg" \
  -F "threshold=0.6" \
  -F "top_k=5"
```

This will return:
- List of matching partners
- Similarity scores (0-1, higher is better)
- Number of matches found

#### Test via Swagger UI:
1. Go to `http://localhost:8000/docs`
2. Find `/partners/create-with-image` endpoint
3. Click "Try it out"
4. Fill in the form:
   - name: "John Doe"
   - relationship: "Friend"
   - image: Upload a face photo
5. Execute and check response

### 3. Add a Conversation
- Select a contact from the sidebar
- Click "New Conversation"
- Add messages alternating between you and your partner
- Click "Save & Analyze"

The AI will automatically:
- Extract key facts about the person
- Identify main topics discussed
- Generate a summary
- Create conversation suggestions

### 4. Get Suggestions
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
- `conversation_partners` - People you talk to (with face embeddings)
- `conversations` - Conversation sessions with embeddings
- `messages` - Individual messages
- `extracted_facts` - Categorized facts with confidence scores
- `topics` - Discussion topics (many-to-many with conversations)

**Key Features:**
- **DuckDB database** - Fast in-process database with single-file storage
- **Conversation embeddings** (4096-dimensional) stored as JSON arrays for semantic similarity
- **Face embeddings** (4096-dimensional) using DeepFace Facenet512 model
- **Categorized facts** for easy filtering and retrieval
- **Confidence scores** to prioritize reliable information
- **Temporal tracking** to see how information evolves
- **Topic tagging** for quick context retrieval
- **Face recognition** for identifying people from photos

## API Endpoints

### Partners
- `POST /api/partners` - Create contact (JSON)
- `POST /api/partners/create-with-image` - Create contact with face photo (multipart/form-data)
- `GET /api/partners` - List all contacts
- `GET /api/partners/{id}` - Get specific contact
- `PUT /api/partners/{id}` - Update contact
- `DELETE /api/partners/{id}` - Delete contact
- `POST /api/partners/{id}/upload-image` - Upload face photo to existing contact
- `POST /api/partners/search-by-face` - Search for partners by face photo

### Conversations
- `POST /api/conversations` - Create conversation
- `GET /api/conversations?partner_id={id}` - List conversations
- `POST /api/conversations/{id}/analyze` - Analyze with AI

### Suggestions
- `GET /api/suggestions/{partner_id}` - Get suggestions
- `GET /api/suggestions/{partner_id}/facts` - Get all facts

## Troubleshooting

**Database Connection Error:**
- Make sure the `conversation_ai.db` file has write permissions
- Check DATABASE_URL in `.env` is set to `duckdb:///./conversation_ai.db`
- If database is corrupted, delete `conversation_ai.db` and run `python init_db.py` again

**Gemini API Error:**
- Verify your GOOGLE_API_KEY is correct
- Check you have API quota available
- Ensure you're using the correct model name

**CORS Error:**
- Check ALLOWED_ORIGINS in `.env` includes `http://localhost:3000`
- Restart the backend server after changing `.env`

**Face Recognition Issues:**
- "No face detected": Ensure the photo has a clear, visible face
- Slow first upload: DeepFace downloads models on first use (~100MB)
- TensorFlow warnings: These are normal and can be ignored
- Low similarity scores: Try photos with better lighting and frontal view

**File Upload Errors:**
- Ensure `uploads/faces` directory exists or will be created automatically
- Check file size limits (default is usually 10MB for FastAPI)
- Verify image format is supported (JPG, PNG, WebP)

**Migration Errors:**
- If you get "relationship is not callable" error, ensure you're using the latest code
- Run `alembic downgrade -1` then `alembic upgrade head` to retry
- Check that all model files import `relationship as sa_relationship`

## Testing the Face Recognition Feature

### From the Website (Frontend):

1. **Start both backend and frontend servers**
2. **Open** `http://localhost:3000`
3. **Click the "+" button** in the sidebar to add a new contact
4. **Fill in the form:**
   - Name: "Test Person"
   - Email: (optional)
   - Relationship: "Friend" (optional)
5. **Click the camera icon** to upload a photo
   - Select a clear photo with a visible face
   - You should see a preview of the image
6. **Click "Create Contact"**
7. **Check the browser console** for any errors
8. **Verify in the database** that the embedding was stored:
```bash
# You can use the DuckDB CLI or Python to query:
python -c "import duckdb; conn = duckdb.connect('conversation_ai.db'); print(conn.execute('SELECT id, name, image_path, CASE WHEN image_embedding IS NULL THEN \"No\" ELSE \"Yes\" END as has_embedding FROM conversation_partners').fetchall())"
```

### Using Swagger UI (Recommended for Testing):

1. **Open** `http://localhost:8000/docs`
2. **Find** `/partners/create-with-image` endpoint
3. **Click "Try it out"**
4. **Fill in:**
   - name: "John Doe"
   - relationship: "Colleague"
   - image: Click "Choose File" and select a face photo
5. **Click "Execute"**
6. **Check response:**
   - Should return status 201
   - Response body should include `image_path` and partner details
   - `image_embedding` won't be visible in response (it's in database)

### Testing Face Search:

1. **Create 2-3 partners** with different face photos
2. **Use Swagger UI** at `http://localhost:8000/docs`
3. **Find** `/partners/search-by-face` endpoint
4. **Upload a photo** of one of the people you added
5. **Set parameters:**
   - threshold: 0.6 (adjust between 0-1)
   - top_k: 5
6. **Execute and check results:**
   - Should return matching partners
   - Similarity scores close to 1.0 = very similar
   - Scores < 0.6 = not very similar

## Next Steps

1. **Add Face Search to UI**: Create a search-by-photo button in frontend
2. **Add Authentication**: Implement user login/signup
3. **Real-time Sync**: Add WebSocket for live updates
4. **Mobile App**: Create React Native version with camera integration
5. **Voice Input**: Add speech-to-text for conversations
6. **Reminders**: Set reminders for important facts
7. **Export**: Export conversation history as PDF
8. **Bulk Face Processing**: Upload multiple photos at once

## Support

For issues or questions, refer to:
- FastAPI docs: https://fastapi.tiangolo.com
- Gemini API docs: https://ai.google.dev/docs
- React docs: https://react.dev
