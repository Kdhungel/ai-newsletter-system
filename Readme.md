```markdown
# AI-Powered Newsletter System

A complete, production-ready newsletter automation system with AI summarization, email tracking, and analytics. Built from scratch to demonstrate full-stack development skills.

## Features
- **User Management**: REST API for subscription management
- **Content Pipeline**: Scrapes news → AI summarizes → Personalizes content
- **Email Automation**: Professional HTML templates with tracking
- **Analytics Dashboard**: Real-time open/click rates, engagement metrics
- **Scheduling**: Daily automated newsletter delivery
- **Tracking System**: Pixel tracking for opens, redirect tracking for clicks

## Tech Stack
- **Backend**: FastAPI (Python) with SQLAlchemy ORM
- **Database**: SQLite (production-ready for PostgreSQL)
- **AI Integration**: OpenAI GPT for article summarization
- **Web Scraping**: BeautifulSoup + Requests
- **Email**: SMTP/Resend API with HTML templates
- **Scheduling**: Schedule library for cron-like automation
- **Tracking**: Custom analytics endpoints with pixel/redirect tracking

## Project Structure
```
ai-newsletter-system/
├── main.py              # FastAPI application with all endpoints
├── database.py          # Database models and configuration
├── scraper.py           # Web scraper fetching news articles
├── ai_summarizer.py     # AI-powered article summarization
├── email_sender.py      # Email generation and sending with tracking
├── orchestrator.py      # Main newsletter pipeline orchestrator
├── scheduler.py         # Daily automated scheduler
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── README.md            # This file
└── (venv/)              # Virtual environment
```

## Quick Start

### 1. Installation
```
git clone https://github.com/Kdhungel/ai-newsletter-system.git
cd ai-newsletter-system
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
pip install -r requirements.txt
cp .env.example .env
```

### 2. Configuration (.env)
```
OPENAI_API_KEY=your_key_here
DATABASE_URL=sqlite:///./newsletter.db
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
RESEND_API_KEY=your_resend_key
USE_RESEND=False
DEV_MODE=True
```

### 3. Running the System
```
uvicorn main:app --reload
python orchestrator.py
python scheduler.py
```

## API Endpoints
- POST /subscribe - Subscribe new user with interests
- GET /users - List all active subscribers
- POST /unsubscribe/{email} - Unsubscribe user
- GET /track/open/{newsletter_id} - Track email opens (1x1 pixel)
- GET /track/click/{newsletter_id}/{article_index} - Track link clicks
- GET /analytics - Summary of all newsletters sent
- GET /analytics/{newsletter_id} - Detailed stats for specific newsletter
- GET / - Welcome message
- GET /health - Health check endpoint

Interactive API documentation: http://localhost:8000/docs

## How It Works

### 1. Data Flow
User Signup → Database → Daily Scheduler → Web Scraper → AI Summarizer → Email Generator → Send Email → Track Engagement

### 2. Newsletter Pipeline
1. Scraping: Fetches articles from configured news sources
2. AI Summarization: Uses OpenAI GPT to create concise summaries
3. Personalization: Tailors content based on user interests
4. Email Generation: Creates responsive HTML emails
5. Tracking: Adds invisible pixel and tracking URLs
6. Sending: Delivers via SMTP/Resend API
7. Analytics: Logs opens, clicks, engagement metrics

### 3. Tracking System
- Open Tracking: Invisible 1x1 pixel image loads when email is opened
- Click Tracking: Special redirect URLs log which articles are clicked
- Database Storage: All engagement data stored for analytics

## Analytics Dashboard
Access analytics at:
- Individual newsletter: http://localhost:8000/analytics/{id}
- Summary view: http://localhost:8000/analytics

Returns metrics like:
- Open rates and timestamps
- Click-through rates
- Most popular articles
- User engagement patterns

## Deployment Ready

### For Production:
1. Update .env with real API keys
2. Set DEV_MODE=False or remove DEV_MODE
3. Configure real email service (Resend recommended)
4. Deploy to cloud platform:

### Railway (Recommended - Free Tier)
```
echo "web: uvicorn main:app --host=0.0.0.0 --port=$PORT" > Procfile
```

### Render
- Create new Web Service
- Build command: pip install -r requirements.txt
- Start command: uvicorn main:app --host=0.0.0.0 --port=$PORT

## Learning Outcomes
This project demonstrates proficiency in:

### Technical Skills
- Full-Stack Development: API design, database modeling, frontend integration
- External API Integration: Web scraping, AI services, email APIs
- Production Patterns: Error handling, logging, scheduling, configuration management
- Analytics Implementation: Custom tracking system, data visualization

### Business Skills
- Automation Thinking: Converting manual processes to automated systems
- User-Centric Design: Personalization based on user interests
- Data-Driven Decisions: Analytics for continuous improvement
- Scalability Planning: Architecture that supports growth

## Future Enhancements
- Web dashboard with charts and graphs
- User preference management interface
- A/B testing for subject lines and content
- More news sources and categories
- Social media integration
- Payment integration for premium features
- Mobile application
- Advanced machine learning for content recommendations

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License
MIT License - see LICENSE file for details

## Acknowledgments
- Built as a portfolio project to demonstrate full-stack development capabilities
- Inspired by real-world newsletter automation needs
- Designed for production deployment and scalability

## Contact
For questions or feedback:
- GitHub: Kdhungel
- Project Repository: ai-newsletter-system

---

Built with ❤️ to showcase practical AI/automation implementation skills.
```
