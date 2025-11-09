# Database Schema Documentation

## Overview

**Database Type**: DuckDB (embedded analytical database)
**Database File**: `conversation_ai.db` (6.0 MB)
**ORM**: SQLAlchemy
**Total Tables**: 7 (5 main tables + 1 association table + sequences)

The database is designed to support an AI-powered conversation assistant that tracks conversations, partners, and extracts valuable insights using face recognition and natural language processing.

---

## Current Data Summary

| Entity | Count |
|--------|-------|
| Users | 1 |
| Conversation Partners | 2 |
| Conversations | 7 |
| Messages | 0 |
| Extracted Facts | 11 |
| Topics | 10 |

---

## Tables Overview

### 1. **users** - System Users
Stores information about users of the conversation assistant system.

**Columns:**
- `id` (INTEGER, PRIMARY KEY) - Auto-incrementing user ID
- `email` (VARCHAR, UNIQUE, NOT NULL) - User's email address
- `username` (VARCHAR, UNIQUE, NOT NULL) - Unique username
- `hashed_password` (VARCHAR, NOT NULL) - Bcrypt hashed password
- `is_active` (BOOLEAN, default: true) - Account status
- `created_at` (TIMESTAMP) - Account creation timestamp
- `updated_at` (TIMESTAMP) - Last update timestamp

**Relationships:**
- One-to-many with `conversation_partners`
- One-to-many with `conversations`

**Indexes:**
- Primary key on `id`
- Unique index on `email`
- Unique index on `username`

---

### 2. **conversation_partners** - People Users Talk To
Stores information about people that users have conversations with, including face recognition data.

**Columns:**
- `id` (INTEGER, PRIMARY KEY) - Auto-incrementing partner ID
- `user_id` (INTEGER, FOREIGN KEY → users.id, NOT NULL) - Owner of this partner record
- `name` (VARCHAR, NOT NULL) - Partner's name
- `email` (VARCHAR, NULL) - Partner's email address
- `phone` (VARCHAR, NULL) - Partner's phone number
- `notes` (TEXT, NULL) - User notes about the partner
- `relationship` (VARCHAR, NULL) - Relationship type (friend, colleague, family, etc.)
- `image_url` (VARCHAR, NULL) - **Legacy** - URL to partner's image
- `image_path` (VARCHAR, NULL) - Local file path to uploaded face image
- `image_embedding` (JSON, NULL) - **4096-dimensional vector** for face recognition (stored as JSON array)
- `created_at` (TIMESTAMP) - Record creation timestamp
- `updated_at` (TIMESTAMP) - Last update timestamp

**Relationships:**
- Many-to-one with `users`
- One-to-many with `conversations`
- One-to-many with `extracted_facts`

**Foreign Keys:**
- `user_id` → `users.id`

**Special Features:**
- **Face Recognition**: Uses `image_embedding` (4096-dim vector) for identifying partners via camera
- **Contact Information**: Stores email and phone for future contact suggestions

---

### 3. **conversations** - Conversation Sessions
Represents individual conversation sessions between a user and a partner.

**Columns:**
- `id` (INTEGER, PRIMARY KEY) - Auto-incrementing conversation ID
- `user_id` (INTEGER, FOREIGN KEY → users.id, NOT NULL) - User who had the conversation
- `partner_id` (INTEGER, FOREIGN KEY → conversation_partners.id, NOT NULL) - Conversation partner
- `title` (VARCHAR, NULL) - Conversation title
- `summary` (TEXT, NULL) - AI-generated summary of the conversation
- `full_transcript` (TEXT, NULL) - Complete transcript of the conversation
- `is_analyzed` (BOOLEAN, default: false) - Whether AI analysis has been completed
- `started_at` (TIMESTAMP, default: now()) - When conversation started
- `ended_at` (TIMESTAMP, NULL) - When conversation ended
- `created_at` (TIMESTAMP) - Record creation timestamp
- `updated_at` (TIMESTAMP) - Last update timestamp
- `embedding` (JSON, NULL) - **4096-dimensional vector** for semantic search (stored as JSON array)

**Relationships:**
- Many-to-one with `users`
- Many-to-one with `conversation_partners`
- One-to-many with `messages` (cascade delete)
- Many-to-many with `topics` (through `conversation_topics`)

**Foreign Keys:**
- `user_id` → `users.id`
- `partner_id` → `conversation_partners.id`

**Special Features:**
- **Semantic Search**: Uses `embedding` vector for finding similar conversations
- **Live Transcription**: Populated via Deepgram live audio transcription
- **AI Analysis**: Gemini analyzes conversations to extract insights

---

### 4. **messages** - Individual Messages
Individual messages within a conversation (currently using full transcripts instead).

**Columns:**
- `id` (INTEGER, PRIMARY KEY) - Auto-incrementing message ID
- `conversation_id` (INTEGER, FOREIGN KEY → conversations.id, NOT NULL) - Parent conversation
- `sender` (VARCHAR, NOT NULL) - Message sender: 'user' or 'partner'
- `content` (TEXT, NOT NULL) - Message content
- `timestamp` (TIMESTAMP, default: now()) - When message was sent
- `created_at` (TIMESTAMP) - Record creation timestamp

**Relationships:**
- Many-to-one with `conversations`

**Foreign Keys:**
- `conversation_id` → `conversations.id` (CASCADE DELETE)

**Note**: Currently the system stores full transcripts in the `conversations` table. Individual messages can be used for more granular analysis.

---

### 5. **extracted_facts** - AI-Extracted Information
Key facts extracted from conversations about partners using AI analysis.

**Columns:**
- `id` (INTEGER, PRIMARY KEY) - Auto-incrementing fact ID
- `partner_id` (INTEGER, FOREIGN KEY → conversation_partners.id, NOT NULL) - Related partner
- `conversation_id` (INTEGER, FOREIGN KEY → conversations.id, NULL) - Source conversation
- `category` (VARCHAR, NOT NULL) - Fact category (see categories below)
- `fact_key` (VARCHAR, NOT NULL) - Brief key name (e.g., "favorite_food")
- `fact_value` (TEXT, NOT NULL) - The actual information
- `confidence` (FLOAT, default: 1.0) - Confidence score (0.0-1.0)
- `source_message_id` (INTEGER, FOREIGN KEY → messages.id, NULL) - Source message
- `is_current` (BOOLEAN, default: true) - False if superseded by newer information
- `extracted_at` (TIMESTAMP, default: now()) - When fact was extracted
- `created_at` (TIMESTAMP) - Record creation timestamp
- `updated_at` (TIMESTAMP) - Last update timestamp

**Fact Categories:**
- `interest` - Hobbies, interests, passions
- `preference` - Likes, dislikes, preferences
- `life_event` - Important events, milestones
- `relationship` - Relationship information
- `work` - Career, job, professional information
- `personal` - Personal details and characteristics

**Relationships:**
- Many-to-one with `conversation_partners`
- Many-to-one with `conversations`
- Many-to-one with `messages`

**Foreign Keys:**
- `partner_id` → `conversation_partners.id`
- `conversation_id` → `conversations.id`
- `source_message_id` → `messages.id`

**Special Features:**
- **Confidence Scoring**: AI assigns confidence to extracted facts
- **Version Control**: `is_current` flag allows tracking updated information
- **Traceability**: Links back to source conversation/message

---

### 6. **topics** - Conversation Topics
Topics that can be discussed in conversations.

**Columns:**
- `id` (INTEGER, PRIMARY KEY) - Auto-incrementing topic ID
- `name` (VARCHAR, UNIQUE, NOT NULL) - Topic name
- `category` (VARCHAR, NULL) - Topic category (work, hobby, family, etc.)
- `created_at` (TIMESTAMP) - Record creation timestamp

**Relationships:**
- Many-to-many with `conversations` (through `conversation_topics`)

**Indexes:**
- Primary key on `id`
- Unique index on `name`

---

### 7. **conversation_topics** - Association Table
Many-to-many relationship between conversations and topics.

**Columns:**
- `conversation_id` (INTEGER, FOREIGN KEY → conversations.id, PRIMARY KEY) - Conversation reference
- `topic_id` (INTEGER, FOREIGN KEY → topics.id, PRIMARY KEY) - Topic reference
- `relevance_score` (INTEGER, default: 5) - Relevance score (1-10 scale)
- `created_at` (TIMESTAMP) - Association timestamp

**Composite Primary Key**: (`conversation_id`, `topic_id`)

**Foreign Keys:**
- `conversation_id` → `conversations.id`
- `topic_id` → `topics.id`

---

## Database Sequences

The database uses DuckDB sequences for auto-incrementing IDs:

- `users_id_seq` - For users table
- `conversation_partners_id_seq` - For conversation_partners table
- `conversations_id_seq` - For conversations table
- `messages_id_seq` - For messages table
- `extracted_facts_id_seq` - For extracted_facts table
- `topics_id_seq` - For topics table

**Note**: DuckDB doesn't support `ALTER SEQUENCE RESTART`, so the helper function in `db_helpers.py` drops and recreates sequences when needed.

---

## Entity Relationship Diagram (Text)

```
┌──────────┐
│  users   │
└────┬─────┘
     │
     ├─────────────────────────────────┐
     │                                 │
     ▼                                 ▼
┌────────────────────┐         ┌──────────────┐
│conversation_partners│◄────────┤conversations │
└─────────┬──────────┘         └──────┬───────┘
          │                           │
          │                           ├──────────┐
          ▼                           ▼          ▼
    ┌──────────────┐            ┌─────────┐  ┌──────────────────┐
    │extracted_facts│            │messages │  │conversation_topics│
    └──────────────┘            └─────────┘  └────────┬─────────┘
                                                      │
                                                      ▼
                                                 ┌────────┐
                                                 │ topics │
                                                 └────────┘
```

---

## Key Features

### 1. **Face Recognition System**
- Stores 4096-dimensional face embeddings in `conversation_partners.image_embedding`
- Used to automatically identify conversation partners via camera
- Embeddings stored as JSON arrays for DuckDB compatibility

### 2. **AI-Powered Analysis**
- Conversations analyzed by Google Gemini AI
- Extracts facts, topics, and insights automatically
- Generates summaries and conversation starters

### 3. **Semantic Search**
- Conversations have embedding vectors for similarity search
- Enables finding similar past conversations
- 4096-dimensional vectors stored as JSON

### 4. **Live Transcription**
- Integrates with Deepgram for live audio transcription
- Transcripts stored in `conversations.full_transcript`
- Real-time conversation capture during sessions

### 5. **Conversation Intelligence**
- Tracks topics discussed with each partner
- Extracts and categorizes facts about partners
- Provides conversation suggestions based on history
- Confidence scoring for extracted information

---

## Database Configuration

**Connection String**:
```python
DATABASE_URL=duckdb:///path/to/conversation_ai.db
```

**SQLAlchemy Settings**:
- Echo mode: Controlled by DEBUG setting
- Read-only: False
- Compatibility: SERIAL → INTEGER conversion for DuckDB

**ID Generation**:
- Uses custom `get_next_id()` helper function (see `db_helpers.py`)
- Manages sequences manually due to DuckDB limitations
- Handles sequence recreation when max ID exceeds sequence value

---

## Database Migrations

The system uses SQLAlchemy's `Base.metadata.create_all()` for table creation.

**Initialization**:
```python
from app.core.database import engine, Base
from app.models import *

# Create all tables
Base.metadata.create_all(bind=engine)
```

---

## Usage Examples

### Create a User
```python
from app.models import User
from app.core.database import SessionLocal

db = SessionLocal()
user = User(
    email="user@example.com",
    username="john_doe",
    hashed_password="<bcrypt_hash>"
)
db.add(user)
db.commit()
```

### Add a Conversation Partner with Face Recognition
```python
from app.models import ConversationPartner

partner = ConversationPartner(
    user_id=1,
    name="Jane Doe",
    email="jane@example.com",
    relationship="friend",
    image_path="/path/to/face.jpg",
    image_embedding=[0.123, 0.456, ...]  # 4096-dim vector
)
db.add(partner)
db.commit()
```

### Record a Conversation
```python
from app.models import Conversation
from datetime import datetime, timezone

conversation = Conversation(
    user_id=1,
    partner_id=1,
    title="Coffee chat",
    started_at=datetime.now(timezone.utc),
    is_analyzed=False
)
db.add(conversation)
db.commit()
```

### Extract Facts from Conversation
```python
from app.models import ExtractedFact

fact = ExtractedFact(
    partner_id=1,
    conversation_id=1,
    category="interest",
    fact_key="favorite_hobby",
    fact_value="Photography",
    confidence=0.95
)
db.add(fact)
db.commit()
```

---

## Indexes and Performance

**Indexed Columns:**
- `users.id` (PRIMARY KEY)
- `users.email` (UNIQUE)
- `users.username` (UNIQUE)
- `conversation_partners.id` (PRIMARY KEY)
- `conversations.id` (PRIMARY KEY)
- `messages.id` (PRIMARY KEY)
- `extracted_facts.id` (PRIMARY KEY)
- `topics.id` (PRIMARY KEY)
- `topics.name` (UNIQUE)

**Query Optimization:**
- Use foreign key relationships for efficient joins
- Index on email/username for user lookups
- Topic names indexed for fast topic lookup

---

## Backup and Maintenance

**Database File**: `conversation_ai.db`
**Current Size**: 6.0 MB

**Backup Strategy**:
```bash
# Simple file copy
cp conversation_ai.db conversation_ai.db.backup

# With timestamp
cp conversation_ai.db conversation_ai.$(date +%Y%m%d_%H%M%S).db
```

**WAL Files**: DuckDB uses Write-Ahead Logging, you may see:
- `conversation_ai.db.wal` - Write-ahead log

---

## Data Privacy and Security

- **Password Storage**: Bcrypt hashed (never store plain text)
- **Face Embeddings**: Mathematical vectors only (not actual images)
- **Transcripts**: Stored locally in DuckDB
- **No External Storage**: All data kept in local database file

---

## Future Enhancements

Potential schema improvements:
- [ ] Add message-level embeddings for fine-grained search
- [ ] Add tags/labels for conversations
- [ ] Add conversation ratings/feedback
- [ ] Add partner groups/categories
- [ ] Add attachment/media storage
- [ ] Add scheduled reminders based on conversations
- [ ] Add conversation templates
- [ ] Full-text search indexes for transcripts
