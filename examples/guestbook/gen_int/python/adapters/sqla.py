# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from sqlalchemy.orm import Session


@dataclass
class SqlaAdapter:
    """Adapter providing a SQLAlchemy session."""

    session: Session
