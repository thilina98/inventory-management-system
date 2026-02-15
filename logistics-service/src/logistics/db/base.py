from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    This is isolated to prevent circular imports when models import Base,
    and the session manager imports models.
    """
    pass