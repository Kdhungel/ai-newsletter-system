"""
Main FastAPI application for Newsletter System
"""
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import database
from fastapi import HTTPException
from pydantic import BaseModel
from typing import List

# Initialize FastAPI app
app = FastAPI(title="Newsletter API", version="1.0.0")


def get_db():
    """
    Dependency function to get database session.
    Yields a session and ensures it's closed after use.
    """
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserCreate(BaseModel):
    """Request model for creating a user"""
    email: str
    interests: List[str]

@app.get("/")
def read_root():
    """Root endpoint - welcome message"""
    return {"message": "Newsletter API is running"}


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}


@app.post("/subscribe")
def subscribe_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Subscribe a new user to newsletter
    """
    # Convert interests list to comma-separated string
    interests_str = ",".join(user.interests)
    
    # Check if user already exists
    existing_user = db.query(database.User).filter(database.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already subscribed")
    
    # Create new user
    db_user = database.User(
        email=user.email,
        interests=interests_str,
        subscribed=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "Subscribed successfully", "user_id": db_user.id}

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    """Get all subscribed users"""
    users = db.query(database.User).filter(database.User.subscribed == True).all()
    return users

@app.post("/unsubscribe/{email}")
def unsubscribe_user(email: str, db: Session = Depends(get_db)):
    """Unsubscribe a user by email"""
    user = db.query(database.User).filter(database.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.subscribed = False
    db.commit()
    
    return {"message": "Unsubscribed successfully"}