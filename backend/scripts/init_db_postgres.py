"""
Initialize PostgreSQL database schema and create tables.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine, Base
from app.models import (
    User,
    ConversationPartner,
    Conversation,
    Message,
    ExtractedFact,
    Topic
)
from app.core.config import settings

def init_db():
    """Initialize the database."""
    print("=" * 50)
    print("Initializing PostgreSQL Database")
    print("=" * 50)
    print()
    print(f"Database URL: {settings.DATABASE_URL}")
    print()

    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✓ Connected to PostgreSQL")
            print(f"  Version: {version}")
            print()

        # Drop all tables (for clean slate)
        print("Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
        print("✓ Tables dropped")
        print()

        # Create all tables
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ Tables created:")
        for table in Base.metadata.sorted_tables:
            print(f"  - {table.name}")
        print()

        # Create indexes
        print("Creating indexes...")
        with engine.connect() as conn:
            # Index on user_id for faster lookups
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_partners_user_id
                ON conversation_partners(user_id)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_conversations_user_id
                ON conversations(user_id)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_conversations_partner_id
                ON conversations(partner_id)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
                ON messages(conversation_id)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_facts_partner_id
                ON extracted_facts(partner_id)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_facts_conversation_id
                ON extracted_facts(conversation_id)
            """))

            # Index on created_at for time-based queries
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_conversations_created_at
                ON conversations(created_at DESC)
            """))

            conn.commit()
        print("✓ Indexes created")
        print()

        # Create a default test user
        from sqlalchemy.orm import Session
        from app.models.user import User
        import bcrypt

        with Session(engine) as session:
            # Check if user exists
            existing_user = session.query(User).filter_by(email="test@example.com").first()

            if not existing_user:
                # Use bcrypt directly to avoid passlib compatibility issues
                password = b"testpassword"
                hashed = bcrypt.hashpw(password, bcrypt.gensalt())

                test_user = User(
                    email="test@example.com",
                    username="testuser",
                    hashed_password=hashed.decode('utf-8'),
                    is_active=True
                )
                session.add(test_user)
                session.commit()
                print("✓ Created test user:")
                print(f"  Email: test@example.com")
                print(f"  Password: testpassword")
                print(f"  User ID: {test_user.id}")
            else:
                print("✓ Test user already exists:")
                print(f"  Email: {existing_user.email}")
                print(f"  User ID: {existing_user.id}")

        print()
        print("=" * 50)
        print("Database Initialization Complete!")
        print("=" * 50)
        print()
        print("The database is ready to use.")
        print()
        print("To start the backend server:")
        print("  uvicorn app.main:app --reload --port 8000")
        print()

    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    init_db()
