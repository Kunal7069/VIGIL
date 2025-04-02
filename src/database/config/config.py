import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from settings.database_management import database_management

# Create SQLAlchemy engine
engine = create_engine(database_management.DATABASE_URL, pool_pre_ping=True)

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

# Function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
