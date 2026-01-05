"""
Main FastAPI application for Newsletter System
"""
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import database
from pydantic import BaseModel
from typing import List
from datetime import datetime
from fastapi.responses import Response, RedirectResponse

# Initialize FastAPI app
app = FastAPI(title="Newsletter API", version="2.0.0")


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


@app.get("/track/open/{newsletter_id}")
def track_email_open(newsletter_id: str, db: Session = Depends(get_db)):
    """Track when email is opened (via invisible pixel)"""
    tracking = db.query(database.EmailTracking).filter(
        database.EmailTracking.newsletter_id == newsletter_id
    ).first()
    
    if tracking:
        tracking.opened = True
        tracking.opened_count += 1
        if not tracking.opened_at:
            tracking.opened_at = datetime.utcnow()
        db.commit()
        print(f"📊 Email opened: {newsletter_id}")
    
    # Return 1x1 transparent GIF pixel
    pixel = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
    return Response(content=pixel, media_type="image/gif")


@app.get("/track/click/{newsletter_id}/{article_index}")
def track_link_click(newsletter_id: str, article_index: int, db: Session = Depends(get_db)):
    """Track when links are clicked in newsletter"""
    tracking = db.query(database.EmailTracking).filter(
        database.EmailTracking.newsletter_id == newsletter_id
    ).first()
    
    if tracking:
        tracking.clicked = True
        tracking.click_count += 1
        tracking.last_clicked_at = datetime.utcnow()
        
        # Record which article was clicked
        clicked = tracking.clicked_articles.split(",") if tracking.clicked_articles else []
        clicked.append(str(article_index))
        tracking.clicked_articles = ",".join(set(clicked))  # Remove duplicates
        
        db.commit()
        print(f"📊 Link clicked: {newsletter_id}, Article: {article_index}")
    
    # For now, redirect to example.com
    # In production, you'd store the actual URL in the article data
    return RedirectResponse(url="https://example.com")


@app.get("/analytics/{newsletter_id}")
def get_analytics(newsletter_id: str, db: Session = Depends(get_db)):
    """Get analytics for a specific newsletter"""
    tracking = db.query(database.EmailTracking).filter(
        database.EmailTracking.newsletter_id == newsletter_id
    ).first()
    
    if not tracking:
        raise HTTPException(status_code=404, detail="Newsletter not found")
    
    return {
        "newsletter_id": tracking.newsletter_id,
        "user_email": tracking.user_email,
        "sent_at": tracking.sent_at,
        "opened": tracking.opened,
        "opened_at": tracking.opened_at,
        "opened_count": tracking.opened_count,
        "clicked": tracking.clicked,
        "click_count": tracking.click_count,
        "last_clicked_at": tracking.last_clicked_at,
        "clicked_articles": tracking.clicked_articles.split(",") if tracking.clicked_articles else []
    }


@app.get("/analytics")
def get_all_analytics(db: Session = Depends(get_db)):
    """Get analytics for all newsletters"""
    all_tracking = db.query(database.EmailTracking).all()
    
    # Calculate summary stats
    total_sent = len(all_tracking)
    total_opened = sum(1 for t in all_tracking if t.opened)
    total_clicked = sum(1 for t in all_tracking if t.clicked)
    
    return {
        "summary": {
            "total_newsletters_sent": total_sent,
            "opened_rate": f"{(total_opened/total_sent*100):.1f}%" if total_sent > 0 else "0%",
            "click_rate": f"{(total_clicked/total_sent*100):.1f}%" if total_sent > 0 else "0%"
        },
        "detailed": [
            {
                "newsletter_id": t.newsletter_id,
                "user_email": t.user_email,
                "sent_at": t.sent_at,
                "opened": t.opened,
                "clicked": t.clicked
            }
            for t in all_tracking
        ]
    }