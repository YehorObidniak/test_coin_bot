from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import os

# Assuming SQLite for simplicity; replace with your actual database URI
DATABASE_URI = os.getenv("DB_URL")#'postgresql://postgres:password@127.0.0.1:5433/coin'
engine = create_engine(DATABASE_URI, echo=True, future=True)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()