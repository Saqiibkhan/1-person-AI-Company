"""
The single declarative Base every model inherits from.

Kept in its own tiny module (instead of inside connection.py) so models
can import Base without accidentally importing the engine/session too,
which avoids circular imports.
"""
from sqlalchemy.orm import declarative_base

Base = declarative_base()
