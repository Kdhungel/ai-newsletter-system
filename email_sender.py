"""
Email sending module using SMTP (for development) or Resend API
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

USE_RESEND = False  # Set True when you get Resend API key


class EmailSender:
    def __init__(self):
        self.use_resend = USE_RESEND
        
        if self.use_resend:
            # For Resend API (better deliverability)
            self.resend_api_key = os.getenv("RESEND_API_KEY")
            self.from_email = "newsletter@yourdomain.com"
        else:
            # For SMTP (development/testing)
            self.smtp_server = "smtp.gmail.com"
            self.smtp_port = 587
            self.smtp_username = os.getenv("SMTP_USERNAME", "")
            self.smtp_password = os.getenv("SMTP_PASSWORD", "")
            self.from_email = self.smtp_username
    
    def send_newsletter(self, to_email, subject, html_content, plain_text=""):
        """
        Send newsletter email to a subscriber
        Returns True if successful, False otherwise
        """
        if self.use_resend:
            return self._send_via_resend(to_email, subject, html_content)
        else:
            return self._send_via_smtp(to_email, subject, html_content, plain_text)
    
      
    def _send_via_smtp(self, to_email, subject, html_content, plain_text=""):
        """Send email using SMTP (for development)"""
        # Check if we have SMTP credentials
        if not self.smtp_username or not self.smtp_password:
            print(f"📧 [DEV MODE] Would send to {to_email}: {subject[:50]}...")
            print(f"   Set SMTP_USERNAME and SMTP_PASSWORD in .env to actually send")
            return True  # Return True in dev mode
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Add both plain text and HTML versions
            if plain_text:
                msg.attach(MIMEText(plain_text, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            # Connect and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ Email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {e}")
            return False
    
    def _send_via_resend(self, to_email, subject, html_content):
        """Send email using Resend API (production)"""
        # We'll implement this later
        print(f"📧 [Resend] Would send to {to_email}: {subject[:50]}...")
        return True
    
    def create_newsletter_html(self, articles, user_interests):
        """
        Generate HTML email content from articles
        """
        interests_str = ", ".join(user_interests)
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #4F46E5; color: white; padding: 20px; text-align: center; }}
                .article {{ margin: 20px 0; padding: 15px; border-left: 4px solid #4F46E5; background: #f9f9f9; }}
                .title {{ font-size: 18px; font-weight: bold; color: #1F2937; }}
                .summary {{ margin: 10px 0; color: #4B5563; }}
                .read-more {{ color: #4F46E5; text-decoration: none; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #E5E7EB; color: #6B7280; font-size: 12px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📰 Your Personalized Newsletter</h1>
                    <p>Curated based on your interests: {interests_str}</p>
                </div>
        """
        
        for i, article in enumerate(articles, 1):
            html += f"""
                <div class="article">
                    <div class="title">#{i}: {article['title']}</div>
                    <div class="summary">{article['summary']}</div>
                    <a href="{article['url']}" class="read-more">Read full article →</a>
                </div>
            """
        
        html += """
                <div class="footer">
                    <p>You received this email because you subscribed to our newsletter.</p>
                    <p><a href="http://localhost:8000/unsubscribe/{email}">Unsubscribe</a></p>
                    <p>© 2024 Newsletter System. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html


# Test
if __name__ == "__main__":
    sender = EmailSender()
    
    # Test articles
    test_articles = [
        {
            "title": "Tesla sales decline 9% as BYD takes EV lead",
            "summary": "Tesla's annual sales dropped while Chinese automaker BYD became the global EV leader.",
            "url": "https://example.com/tesla-news"
        },
        {
            "title": "New AI chip breaks performance records",
            "summary": "Latest AI processor achieves 2x speed improvement for machine learning tasks.",
            "url": "https://example.com/ai-chip"
        }
    ]
    
    # Generate HTML
    html_content = sender.create_newsletter_html(test_articles, ["tech", "business"])
    
    # Print first 500 chars of HTML to check
    print("Generated HTML (first 500 chars):")
    print(html_content[:500])
    print("...")
    
    # Try to send (will likely fail without SMTP credentials, but that's OK)
    success = sender.send_newsletter(
        to_email="test@example.com",
        subject="Your Daily Tech Briefing",
        html_content=html_content,
        plain_text="Your newsletter is ready. View in browser for full experience."
    )
    
    print(f"\nSend attempted. Success: {success}")
    print("\nNote: To actually send emails, add SMTP credentials to .env file")
    print("Or get Resend API key from resend.com and set USE_RESEND = True")