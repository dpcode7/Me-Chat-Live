from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import random
import string
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "mechat.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# User Table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    dob = Column(String)
    secret_key = Column(String, unique=True, index=True)
    public_id = Column(String, unique=True, index=True)
    gender = Column(String, default="Male")

# NEW: The Chat Vault (Messages Table)
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(String, index=True)   # Jisne bheja
    receiver_id = Column(String, index=True) # Jisko bheja
    text = Column(String)                    # Message ka text
    timestamp = Column(DateTime, default=datetime.utcnow) # Kis time bheja

def generate_id(prefix):
    digits = ''.join(random.choices(string.digits, k=6))
    return f"{prefix}-{digits}"

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("✅ VIP DATABASE READY! (Chat History Vault Enabled!)")