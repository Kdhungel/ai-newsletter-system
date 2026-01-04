"""
Scheduler to run newsletter daily
"""
import schedule
import time
from orchestrator import NewsletterOrchestrator
import database
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()


def run_newsletter_job():
    """Job function to run newsletter pipeline"""
    print(f"\n{'='*60}")
    print(f"🕒 Running scheduled newsletter job at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create database session
    engine = database.create_engine(os.getenv("DATABASE_URL"))
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Run orchestrator
        orchestrator = NewsletterOrchestrator()
        orchestrator.run_daily_newsletter(db)
    except Exception as e:
        print(f"❌ Job failed with error: {e}")
    finally:
        db.close()
    
    print(f"✅ Job completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    print("📅 Newsletter Scheduler Started")
    print("Press Ctrl+C to stop\n")
    
    # Schedule to run daily at 8 AM
    schedule.every().day.at("08:00").do(run_newsletter_job)
    
    # Also run immediately for testing
    print("Running initial test...")
    run_newsletter_job()
    
    # Keep scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute