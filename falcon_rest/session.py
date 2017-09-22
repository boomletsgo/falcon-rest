from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker


@contextmanager
def make(db_engine, **kwargs):
    """Scope a db_session for a context, and close it afterwards"""
    db_session = sessionmaker(bind=db_engine, **kwargs)()
    try:
        yield db_session
    finally:
        db_session.close()
