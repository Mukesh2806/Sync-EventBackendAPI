from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./sync_api_a2.db"

# The connect_args bit is a special requirement just for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# This is a "Dependency" we will use in our routes to safely talk to the DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()