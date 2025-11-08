"""
Database initialization script for DuckDB.
Creates all tables based on SQLAlchemy models.
"""
import os
from app.core.database import engine, Base
from app.models.user import User
from app.models.conversation_partner import ConversationPartner
from app.models.conversation import Conversation, Message
from app.models.extracted_fact import ExtractedFact
from app.models.topic import Topic, conversation_topics


def init_db(drop_existing=False):
    """Initialize database by creating all tables.

    Args:
        drop_existing: If True, drop all existing tables first (WARNING: destroys all data)
    """
    from sqlalchemy import text

    if drop_existing:
        print("WARNING: Dropping all existing tables and data...")
        try:
            # Drop tables in reverse order of dependencies
            with engine.connect() as conn:
                conn.execute(text("DROP TABLE IF EXISTS extracted_facts CASCADE"))
                conn.execute(text("DROP TABLE IF EXISTS conversation_topics CASCADE"))
                conn.execute(text("DROP TABLE IF EXISTS messages CASCADE"))
                conn.execute(text("DROP TABLE IF EXISTS conversations CASCADE"))
                conn.execute(text("DROP TABLE IF EXISTS topics CASCADE"))
                conn.execute(text("DROP TABLE IF EXISTS conversation_partners CASCADE"))
                conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))

                # Drop sequences
                conn.execute(text("DROP SEQUENCE IF EXISTS users_id_seq"))
                conn.execute(text("DROP SEQUENCE IF EXISTS conversation_partners_id_seq"))
                conn.execute(text("DROP SEQUENCE IF EXISTS conversations_id_seq"))
                conn.execute(text("DROP SEQUENCE IF EXISTS messages_id_seq"))
                conn.execute(text("DROP SEQUENCE IF EXISTS extracted_facts_id_seq"))
                conn.execute(text("DROP SEQUENCE IF EXISTS topics_id_seq"))

                conn.commit()
                print("All existing tables and sequences dropped.")
        except Exception as e:
            print(f"Note: Error during cleanup (this is usually fine): {e}")

    # Create sequences for auto-increment in DuckDB FIRST (before tables)
    print("Creating sequences for auto-increment...")
    with engine.connect() as conn:
        sequences = [
            "CREATE SEQUENCE IF NOT EXISTS users_id_seq START 1",
            "CREATE SEQUENCE IF NOT EXISTS conversation_partners_id_seq START 1",
            "CREATE SEQUENCE IF NOT EXISTS conversations_id_seq START 1",
            "CREATE SEQUENCE IF NOT EXISTS messages_id_seq START 1",
            "CREATE SEQUENCE IF NOT EXISTS extracted_facts_id_seq START 1",
            "CREATE SEQUENCE IF NOT EXISTS topics_id_seq START 1",
        ]
        for seq in sequences:
            conn.execute(text(seq))
        conn.commit()

    print("Creating database tables...")
    try:
        # Use checkfirst=True to avoid issues with existing tables
        Base.metadata.create_all(bind=engine, checkfirst=True)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        print("Attempting to continue with direct table inspection...")
        # Check what was created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Tables in database: {tables}")
        if len(tables) == 7:
            print("✅ All 7 tables exist, migration successful!")
        else:
            raise e

    print(f"📊 Database location: {os.path.abspath('conversation_ai.db')}")


if __name__ == "__main__":
    import sys

    # Check if --drop flag is provided
    drop_flag = "--drop" in sys.argv or "--fresh" in sys.argv

    if drop_flag:
        response = input("⚠️  WARNING: This will delete ALL existing data. Continue? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            sys.exit(0)

    init_db(drop_existing=drop_flag)
