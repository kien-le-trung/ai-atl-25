# PostgreSQL Migration Guide

This guide walks you through migrating from DuckDB to PostgreSQL for the AI Conversation Assistant backend.

## Why PostgreSQL?

PostgreSQL offers several advantages over DuckDB for this application:

- **Better concurrency**: Multiple clients can read/write simultaneously
- **Robust transactions**: ACID compliance with proper isolation levels
- **Production-ready**: Battle-tested in production environments
- **Advanced features**: Full-text search, JSON operations, vector extensions (pgvector)
- **Better ecosystem**: Wide tool support, monitoring, backups
- **Connection pooling**: Efficient resource management

## Prerequisites

1. **PostgreSQL installed via Homebrew**:
   ```bash
   brew install postgresql@15
   ```

2. **PostgreSQL service running**:
   ```bash
   brew services start postgresql@15
   ```

3. **Python dependencies updated**:
   ```bash
   cd /Users/harjyot/Desktop/code/roblox/ai-atl-25/backend
   source venv/bin/activate
   pip install psycopg2-binary
   ```

## Migration Steps

### Step 1: Create PostgreSQL Database

Run the automated setup script:

```bash
cd /Users/harjyot/Desktop/code/roblox/ai-atl-25/backend
chmod +x scripts/setup_postgres.sh
./scripts/setup_postgres.sh
```

**Or manually create the database**:

```bash
psql postgres -c "CREATE DATABASE conversation_ai;"
```

### Step 2: Verify Database Connection

Test the connection:

```bash
psql postgresql://postgres:postgres@localhost:5432/conversation_ai -c "SELECT version();"
```

You should see the PostgreSQL version information.

### Step 3: Update Environment Variables

The `.env` file has already been updated with:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/conversation_ai
```

**Important**: If your PostgreSQL has a different:
- **Username**: Replace `postgres` (first occurrence)
- **Password**: Replace `postgres` (second occurrence)
- **Host**: Replace `localhost`
- **Port**: Replace `5432`
- **Database name**: Replace `conversation_ai`

Format: `postgresql://[user]:[password]@[host]:[port]/[database]`

### Step 4: Initialize Database Schema

**Option A: Using Python script (Recommended)**:

```bash
cd /Users/harjyot/Desktop/code/roblox/ai-atl-25/backend
source venv/bin/activate
python scripts/init_db_postgres.py
```

This will:
- Create all tables
- Create indexes for performance
- Create a test user (`test@example.com` / `testpassword`)

**Option B: Using Alembic migrations**:

```bash
cd /Users/harjyot/Desktop/code/roblox/ai-atl-25/backend
source venv/bin/activate

# Create initial migration (if needed)
alembic revision --autogenerate -m "initial postgres schema"

# Apply migrations
alembic upgrade head
```

### Step 5: Verify Schema

Check that all tables were created:

```bash
psql postgresql://postgres:postgres@localhost:5432/conversation_ai -c "\dt"
```

You should see:
- `users`
- `conversation_partners`
- `conversations`
- `messages`
- `topics`
- `conversation_topics`
- `extracted_facts`

### Step 6: Start Backend Server

```bash
cd /Users/harjyot/Desktop/code/roblox/ai-atl-25/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 7: Test the Integration

1. **Check health endpoint**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **View API docs**:
   Open http://localhost:8000/docs

3. **Test from frontend**:
   - Start frontend: `cd /tmp/memory-frontend && npm run dev`
   - Open http://localhost:5173
   - Click "Demo" to create a sample conversation
   - Verify it saves to PostgreSQL

## Changes Made

### 1. Dependencies

**Updated** `/Users/harjyot/Desktop/code/roblox/ai-atl-25/backend/requirements.txt`:
- Removed: `duckdb>=1.4.0`, `duckdb-engine>=0.11.2`
- Added: `psycopg2-binary==2.9.9`

### 2. Database Configuration

**Updated** `backend/app/core/database.py`:
- Removed DuckDB-specific connection args
- Added PostgreSQL connection pooling:
  - `pool_size=10` - Number of persistent connections
  - `max_overflow=20` - Additional connections when needed
  - `pool_pre_ping=True` - Test connections before use
  - `pool_recycle=3600` - Recycle connections hourly
- Removed DuckDB SERIAL compatibility hack

### 3. Environment Configuration

**Updated** `backend/.env`:
```env
# Before:
DATABASE_URL=duckdb:///./conversation_ai.db

# After:
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/conversation_ai
```

### 4. Database Helpers

The `app/utils/db_helpers.py` file remains compatible - PostgreSQL natively supports sequences, so the `get_next_id()` function works correctly.

### 5. Models

No changes required! SQLAlchemy models are database-agnostic. The same model definitions work for both DuckDB and PostgreSQL.

## Data Migration (Optional)

If you have existing data in DuckDB that you want to migrate:

### Export from DuckDB

```python
import duckdb
import json

conn = duckdb.connect('conversation_ai.db')

# Export partners
partners = conn.execute("SELECT * FROM conversation_partners").fetchall()
with open('partners.json', 'w') as f:
    json.dump(partners, f)

# Repeat for other tables...
```

### Import to PostgreSQL

```python
import psycopg2
import json

conn = psycopg2.connect(
    "postgresql://postgres:postgres@localhost:5432/conversation_ai"
)
cursor = conn.cursor()

with open('partners.json', 'r') as f:
    partners = json.load(f)
    for partner in partners:
        cursor.execute("""
            INSERT INTO conversation_partners (...)
            VALUES (...)
        """, partner)

conn.commit()
```

Or use a migration tool like `pgloader`.

## Verification Checklist

- [ ] PostgreSQL service is running
- [ ] Database `conversation_ai` exists
- [ ] All 7 tables created successfully
- [ ] Indexes created on foreign keys and common queries
- [ ] Test user created (if using init script)
- [ ] Backend server starts without errors
- [ ] API endpoints respond correctly
- [ ] Frontend can connect to backend
- [ ] Demo conversation creates successfully
- [ ] Data persists across server restarts

## Performance Tuning

### Connection Pooling

Current settings in `database.py`:
```python
pool_size=10           # Base connections
max_overflow=20        # Additional connections
pool_pre_ping=True     # Health check before use
pool_recycle=3600      # Recycle after 1 hour
```

Adjust based on your workload:
- **Low traffic**: `pool_size=5, max_overflow=10`
- **High traffic**: `pool_size=20, max_overflow=40`

### Indexes

Already created by init script:
- `idx_partners_user_id` - Partner lookups by user
- `idx_conversations_user_id` - Conversation lookups by user
- `idx_conversations_partner_id` - Conversations by partner
- `idx_conversations_created_at` - Time-based queries
- `idx_messages_conversation_id` - Message retrieval
- `idx_facts_partner_id` - Fact lookups by partner
- `idx_facts_conversation_id` - Facts by conversation

### PostgreSQL Configuration

For development, default PostgreSQL settings are fine. For production:

```sql
-- Increase shared memory
ALTER SYSTEM SET shared_buffers = '256MB';

-- Increase work memory
ALTER SYSTEM SET work_mem = '10MB';

-- Increase connection limit
ALTER SYSTEM SET max_connections = 100;

-- Reload configuration
SELECT pg_reload_conf();
```

## Advanced Features (Optional)

### 1. Full-Text Search

Enable full-text search on conversation transcripts:

```sql
-- Add tsvector column
ALTER TABLE conversations ADD COLUMN transcript_search tsvector;

-- Create trigger to update search column
CREATE OR REPLACE FUNCTION conversations_search_update() RETURNS trigger AS $$
BEGIN
    NEW.transcript_search := to_tsvector('english', COALESCE(NEW.full_transcript, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER conversations_search_trigger
BEFORE INSERT OR UPDATE ON conversations
FOR EACH ROW EXECUTE FUNCTION conversations_search_update();

-- Create GIN index for fast search
CREATE INDEX idx_conversations_search ON conversations USING GIN(transcript_search);

-- Search usage
SELECT * FROM conversations
WHERE transcript_search @@ to_tsquery('english', 'AI & education');
```

### 2. pgvector for Semantic Search

Install pgvector extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector;

-- Modify embedding columns to use vector type
ALTER TABLE conversation_partners
ALTER COLUMN image_embedding TYPE vector(4096);

ALTER TABLE conversations
ALTER COLUMN embedding TYPE vector(4096);

-- Create vector indexes
CREATE INDEX ON conversation_partners USING ivfflat (image_embedding vector_cosine_ops);
CREATE INDEX ON conversations USING ivfflat (embedding vector_cosine_ops);

-- Similarity search
SELECT * FROM conversation_partners
ORDER BY image_embedding <=> '[...]'::vector
LIMIT 5;
```

### 3. Partitioning for Large Datasets

Partition conversations by date for better performance:

```sql
-- Convert to partitioned table
ALTER TABLE conversations RENAME TO conversations_old;

CREATE TABLE conversations (
    LIKE conversations_old INCLUDING ALL
) PARTITION BY RANGE (created_at);

-- Create partitions
CREATE TABLE conversations_2025 PARTITION OF conversations
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE conversations_2026 PARTITION OF conversations
FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

-- Migrate data
INSERT INTO conversations SELECT * FROM conversations_old;
```

## Troubleshooting

### Connection refused

**Error**: `psycopg2.OperationalError: could not connect to server`

**Solution**:
```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# Start if not running
brew services start postgresql@15

# Check port
lsof -i :5432
```

### Authentication failed

**Error**: `FATAL: password authentication failed for user "postgres"`

**Solution**:
```bash
# Reset password
psql postgres
ALTER USER postgres WITH PASSWORD 'postgres';
\q

# Update .env with correct password
```

### Database does not exist

**Error**: `FATAL: database "conversation_ai" does not exist`

**Solution**:
```bash
createdb conversation_ai
# Or
psql postgres -c "CREATE DATABASE conversation_ai;"
```

### Permission denied

**Error**: `permission denied for table...`

**Solution**:
```sql
-- Grant all privileges
psql conversation_ai
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
```

### Slow queries

**Solution**:
```sql
-- Check slow queries
SELECT query, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Analyze table statistics
ANALYZE conversations;

-- Check if indexes are being used
EXPLAIN ANALYZE SELECT * FROM conversations WHERE user_id = 1;
```

## Rollback to DuckDB

If you need to revert to DuckDB:

1. **Restore original requirements.txt**:
   ```bash
   # Add back DuckDB dependencies
   pip install duckdb duckdb-engine
   ```

2. **Restore .env**:
   ```env
   DATABASE_URL=duckdb:///./conversation_ai.db
   ```

3. **Restore database.py**:
   - Remove connection pooling parameters
   - Add back DuckDB-specific connection args
   - Add back SERIAL compatibility event listener

4. **Restart backend**

## Next Steps

1. **Configure backups**:
   ```bash
   # Create backup
   pg_dump conversation_ai > backup.sql

   # Restore backup
   psql conversation_ai < backup.sql
   ```

2. **Set up monitoring**:
   - Install pgAdmin: https://www.pgadmin.org/
   - Or use CLI: `psql conversation_ai`

3. **Production deployment**:
   - Use managed PostgreSQL (AWS RDS, Google Cloud SQL, etc.)
   - Enable SSL connections
   - Configure firewall rules
   - Set up automated backups

## Support

- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **Alembic Documentation**: https://alembic.sqlalchemy.org/

For issues specific to this migration, check the logs:
```bash
tail -f /usr/local/var/log/postgres.log  # Homebrew PostgreSQL logs
```

## Summary

You've successfully migrated from DuckDB to PostgreSQL! Your application now has:

✅ Production-grade database
✅ Connection pooling for better performance
✅ Better concurrency support
✅ ACID compliance
✅ Advanced indexing
✅ Ready for scaling

The migration required minimal code changes thanks to SQLAlchemy's database abstraction layer.
