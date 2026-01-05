"""
Main orchestrator that runs the newsletter pipeline
"""
import database
from scraper import NewsScraper
from ai_summarizer import ArticleSummarizer
from email_sender import EmailSender
from sqlalchemy.orm import Session
import time
from datetime import datetime
import uuid  # For generating newsletter IDs


class NewsletterOrchestrator:
    def __init__(self):
        self.scraper = NewsScraper()
        self.summarizer = ArticleSummarizer()
        self.email_sender = EmailSender()
    
    def run_daily_newsletter(self, db: Session):
        """
        Main pipeline: Get users → Get articles → Summarize → Send emails
        """
        print("🚀 Starting daily newsletter pipeline...")
        
        # 1. Get all subscribed users
        users = db.query(database.User).filter(database.User.subscribed == True).all()
        print(f"📋 Found {len(users)} subscribed users")
        
        for user in users:
            print(f"\n👤 Processing user: {user.email}")
            
            # Parse interests
            interests = [interest.strip() for interest in user.interests.split(",") if interest.strip()]
            print(f"   Interests: {interests}")
            
            # Skip if no interests
            if not interests:
                print("   ⚠️  No interests specified, skipping")
                continue
            
            # 2. Get articles for each interest
            all_articles = []
            for interest in interests[:3]:  # Limit to 3 interests max
                print(f"   📰 Fetching articles for '{interest}'...")
                articles = self.scraper.get_articles(interest, max_articles=2)
                
                for article in articles:
                    # 3. Summarize each article
                    print(f"      📝 Summarizing: {article['title'][:50]}...")
                    summary = self.summarizer.summarize_article(
                        article['title'], 
                        article['url']
                    )
                    
                    # 4. Personalize summary
                    personalized_summary = self.summarizer.personalize_summary(
                        summary, 
                        interests
                    )
                    
                    all_articles.append({
                        "title": article['title'],
                        "summary": personalized_summary,
                        "url": article['url'],
                        "source": article.get('source', 'Unknown')
                    })
            
            # Skip if no articles found
            if not all_articles:
                print("   ⚠️  No articles found, skipping email")
                continue
            
            # Limit to 5 articles max per email
            selected_articles = all_articles[:5]
            print(f"   ✨ Selected {len(selected_articles)} articles for newsletter")
            
            # 5. Generate newsletter_id FIRST
            newsletter_id = str(uuid.uuid4())[:8]
            
            # 6. Generate email content WITH newsletter_id
            html_content = self.email_sender.create_newsletter_html(
                selected_articles, 
                interests,
                newsletter_id=newsletter_id
            )
            
            plain_text = f"Your daily newsletter with {len(selected_articles)} articles about {', '.join(interests[:2])}."
            
            # 7. Send email WITH newsletter_id
            subject = f"Your {interests[0].title()} News Digest"
            print(f"   📧 Sending email with subject: {subject}")
            
            # Send email with pre-generated newsletter_id
            success, sent_newsletter_id = self.email_sender.send_newsletter(
                to_email=user.email,
                subject=subject,
                html_content=html_content,
                plain_text=plain_text,
                newsletter_id=newsletter_id
            )
            
            print(f"   📬 Sent to {user.email}, Newsletter ID: {newsletter_id}")
            print(f"   📊 Articles: {[a['title'][:30] + '...' for a in selected_articles]}")
            
            # 8. Create tracking record in database
            try:
                tracking_record = database.EmailTracking(
                    user_email=user.email,
                    newsletter_id=newsletter_id,
                    sent_at=datetime.utcnow()
                )
                db.add(tracking_record)
                db.commit()
                print(f"   📊 Tracking record created: {newsletter_id}")
            except Exception as e:
                print(f"   ⚠️  Failed to create tracking record: {e}")
                db.rollback()
            
            # Small delay to avoid rate limits
            time.sleep(0.5)
        
        print(f"\n✅ Pipeline complete! Processed {len(users)} users.")


# Manual trigger
if __name__ == "__main__":
    # Create database session
    from sqlalchemy.orm import sessionmaker
    engine = database.create_engine(database.os.getenv("DATABASE_URL"))
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # Run orchestrator
    orchestrator = NewsletterOrchestrator()
    orchestrator.run_daily_newsletter(db)
    
    db.close()