from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(settings.database_url)
Sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = Sessionlocal()

    try:
        yield db     # hand the session to the endpoint
    finally:
        db.close()   # always close it, even if the endpoint raised