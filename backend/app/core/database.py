from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create database engine for DuckDB
# DuckDB doesn't support connection pooling in the same way as PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"read_only": False}
)

# Event listener to replace SERIAL with INTEGER for DuckDB compatibility
@event.listens_for(engine, "before_cursor_execute", retval=True)
def replace_serial(conn, cursor, statement, parameters, context, executemany):
    """Replace SERIAL type with INTEGER for DuckDB compatibility."""
    if isinstance(statement, str):
        statement = statement.replace(" SERIAL ", " INTEGER ")
    return statement, parameters

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
