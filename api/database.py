from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine 
from .config.constants import SQLALCHEMY_DATABASE_URL


# Creating the conncetion engine for POSTGRESQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit= False, autoflush= False, bind= engine)

# Declarative base for ORM models
Base = declarative_base()

def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()