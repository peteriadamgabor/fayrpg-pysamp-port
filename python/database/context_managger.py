from contextlib import contextmanager
from sqlalchemy.orm import Session

@contextmanager
def transactional_session(session_factory):
    """
    A context manager that provides a SQLAlchemy session with a transaction.
    Commits the transaction if no exceptions occur, otherwise rolls back.
    """
    session: Session = session_factory()
    try:
        with session.begin(): 
            yield session 
    except:
        raise
    finally:
        session.close()
