from sqlalchemy import func
from sqlalchemy.orm import Session


def get_next_id(db: Session, model) -> int:
    """
    Generate the next integer identifier for a model by looking at the current max(id).

    DuckDB doesn't auto-increment integer primary keys by default, so we emulate it in code.
    """
    max_id = db.query(func.max(model.id)).scalar()
    return (max_id or 0) + 1

