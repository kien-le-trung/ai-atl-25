"""
Manual database initialization for DuckDB - creates tables one by one.
"""
import duckdb
import os

# Get the database path
db_path = "conversation_ai.db"

print(f"Creating database at: {os.path.abspath(db_path)}")

# Connect to DuckDB
conn = duckdb.connect(db_path)

try:
    # Create sequences
    print("Creating sequences...")
    sequences = [
        "CREATE SEQUENCE IF NOT EXISTS users_id_seq START 1",
        "CREATE SEQUENCE IF NOT EXISTS conversation_partners_id_seq START 1",
        "CREATE SEQUENCE IF NOT EXISTS conversations_id_seq START 1",
        "CREATE SEQUENCE IF NOT EXISTS messages_id_seq START 1",
        "CREATE SEQUENCE IF NOT EXISTS extracted_facts_id_seq START 1",
        "CREATE SEQUENCE IF NOT EXISTS topics_id_seq START 1",
    ]
    for seq in sequences:
        conn.execute(seq)
    print("✅ Sequences created")

    # Create tables in correct order (respecting foreign keys)
    print("Creating tables...")

    # 1. Users table (no dependencies)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER DEFAULT nextval('users_id_seq') PRIMARY KEY,
            email VARCHAR NOT NULL UNIQUE,
            username VARCHAR NOT NULL UNIQUE,
            hashed_password VARCHAR NOT NULL,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS ix_users_id ON users(id)")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users(email)")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users(username)")
    print("✅ users table created")

    # 2. Topics table (no dependencies)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER DEFAULT nextval('topics_id_seq') PRIMARY KEY,
            name VARCHAR NOT NULL UNIQUE,
            category VARCHAR,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS ix_topics_id ON topics(id)")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_topics_name ON topics(name)")
    print("✅ topics table created")

    # 3. Conversation partners table (depends on users)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversation_partners (
            id INTEGER DEFAULT nextval('conversation_partners_id_seq') PRIMARY KEY,
            user_id INTEGER NOT NULL,
            name VARCHAR NOT NULL,
            email VARCHAR,
            phone VARCHAR,
            notes TEXT,
            relationship VARCHAR,
            image_url VARCHAR,
            image_path VARCHAR,
            image_embedding JSON,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS ix_conversation_partners_id ON conversation_partners(id)")
    print("✅ conversation_partners table created")

    # 4. Conversations table (depends on users and conversation_partners)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER DEFAULT nextval('conversations_id_seq') PRIMARY KEY,
            user_id INTEGER NOT NULL,
            partner_id INTEGER NOT NULL,
            title VARCHAR,
            summary TEXT,
            is_analyzed BOOLEAN DEFAULT false,
            started_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            ended_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE,
            embedding JSON,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(partner_id) REFERENCES conversation_partners(id)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS ix_conversations_id ON conversations(id)")
    print("✅ conversations table created")

    # 5. Messages table (depends on conversations)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER DEFAULT nextval('messages_id_seq') PRIMARY KEY,
            conversation_id INTEGER NOT NULL,
            sender VARCHAR NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            FOREIGN KEY(conversation_id) REFERENCES conversations(id)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS ix_messages_id ON messages(id)")
    print("✅ messages table created")

    # 6. Conversation topics junction table (depends on conversations and topics)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversation_topics (
            conversation_id INTEGER NOT NULL,
            topic_id INTEGER NOT NULL,
            relevance_score INTEGER DEFAULT 5,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            PRIMARY KEY (conversation_id, topic_id),
            FOREIGN KEY(conversation_id) REFERENCES conversations(id),
            FOREIGN KEY(topic_id) REFERENCES topics(id)
        )
    """)
    print("✅ conversation_topics table created")

    # 7. Extracted facts table (depends on conversation_partners, conversations, and messages)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS extracted_facts (
            id INTEGER DEFAULT nextval('extracted_facts_id_seq') PRIMARY KEY,
            partner_id INTEGER NOT NULL,
            conversation_id INTEGER,
            category VARCHAR NOT NULL,
            fact_key VARCHAR NOT NULL,
            fact_value TEXT NOT NULL,
            confidence FLOAT DEFAULT 1.0,
            source_message_id INTEGER,
            is_current BOOLEAN DEFAULT true,
            extracted_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE,
            FOREIGN KEY(partner_id) REFERENCES conversation_partners(id),
            FOREIGN KEY(conversation_id) REFERENCES conversations(id),
            FOREIGN KEY(source_message_id) REFERENCES messages(id)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS ix_extracted_facts_id ON extracted_facts(id)")
    print("✅ extracted_facts table created")

    # Verify all tables
    tables = conn.execute("SHOW TABLES").fetchall()
    table_names = [t[0] for t in tables]
    print(f"\n✅ Database initialization complete!")
    print(f"📊 Created {len(table_names)} tables: {', '.join(sorted(table_names))}")
    print(f"📁 Database location: {os.path.abspath(db_path)}")

except Exception as e:
    print(f"\n❌ Error during initialization: {e}")
    raise
finally:
    conn.close()
