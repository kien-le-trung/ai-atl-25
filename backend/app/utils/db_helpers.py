import logging
from sqlalchemy import func, text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

SEQUENCE_MAP = {
    'users': 'users_id_seq',
    'conversation_partners': 'conversation_partners_id_seq',
    'conversations': 'conversations_id_seq',
    'messages': 'messages_id_seq',
    'extracted_facts': 'extracted_facts_id_seq',
    'topics': 'topics_id_seq'
}


def get_next_id(db: Session, model) -> int:
    """
    Generate the next integer identifier for a model by looking at the current max(id).

    DuckDB doesn't auto-increment integer primary keys by default, so we emulate it in code.
    """
    seq_name = SEQUENCE_MAP.get(getattr(model, '__tablename__', ''))
    max_id = db.query(func.max(model.id)).scalar() or 0

    if seq_name:
        next_id = _safe_next_sequence_value(db, seq_name, max_id + 1)
        if next_id is not None:
            return next_id

    return max_id + 1


def _safe_next_sequence_value(db: Session, seq_name: str, minimum_value: int) -> int:
    """Return the next sequence value, creating or bumping the sequence as needed."""
    try:
        result = db.execute(text(f"SELECT nextval('{seq_name}')")).scalar()
    except Exception as e:
        logger.warning(f"Sequence {seq_name} missing; creating it at {minimum_value}: {e}")
        db.execute(text(f"CREATE SEQUENCE IF NOT EXISTS {seq_name} START {minimum_value}"))
        result = db.execute(text(f"SELECT nextval('{seq_name}')")).scalar()

    if result is None:
        return None

    if result < minimum_value:
        logger.warning(
            "Sequence %s returned %s but minimum needed is %s; recreating sequence",
            seq_name,
            result,
            minimum_value
        )
        # DuckDB doesn't support ALTER SEQUENCE RESTART, so we drop and recreate
        db.execute(text(f"DROP SEQUENCE IF EXISTS {seq_name}"))
        db.execute(text(f"CREATE SEQUENCE {seq_name} START {minimum_value}"))
        result = db.execute(text(f"SELECT nextval('{seq_name}')")).scalar()

    return int(result) if result is not None else None
