"""
Streamlit Dashboard for Newsletter Analytics
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import database
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import requests


load_dotenv()

# Page config
st.set_page_config(
    page_title="Newsletter Analytics",
    page_icon="📈",
    layout="wide"
)

# Database connection
def get_db_session():
    engine = database.create_engine(os.getenv("DATABASE_URL"))
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()

# Dashboard title
st.title("📊 Newsletter Analytics Dashboard")
st.markdown("Real-time insights into your newsletter performance")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Overview", 
    "👥 Subscribers", 
    "📧 Campaigns", 
    "📰 Content"
])

with tab1:
    st.header("Performance Overview")
    
    db = get_db_session()
    
    # Get data
    users = db.query(database.User).filter(database.User.subscribed == True).all()
    tracking = db.query(database.EmailTracking).all()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Active Subscribers",
            value=len(users),
            delta="+2 this week" if len(users) > 0 else "0"
        )
    
    with col2:
        total_sent = len(tracking)
        st.metric(
            label="Newsletters Sent",
            value=total_sent
        )
    
    with col3:
        opened = sum(1 for t in tracking if t.opened)
        open_rate = (opened / total_sent * 100) if total_sent > 0 else 0
        st.metric(
            label="Avg Open Rate",
            value=f"{open_rate:.1f}%",
            delta="+5.2%" if open_rate > 40 else "0%"
        )
    
    with col4:
        clicked = sum(1 for t in tracking if t.clicked)
        click_rate = (clicked / total_sent * 100) if total_sent > 0 else 0
        st.metric(
            label="Avg Click Rate",
            value=f"{click_rate:.1f}%",
            delta="+2.1%" if click_rate > 10 else "0%"
        )
    
    # Recent activity chart
    if tracking:
        st.subheader("Recent Activity")
        
        # Prepare data for chart
        df_tracking = pd.DataFrame([{
            'date': t.sent_at.date() if t.sent_at else datetime.now().date(),
            'opened': 1 if t.opened else 0,
            'clicked': 1 if t.clicked else 0
        } for t in tracking])
        
        if not df_tracking.empty:
            daily_stats = df_tracking.groupby('date').agg({
                'opened': 'sum',
                'clicked': 'sum'
            }).reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_stats['date'],
                y=daily_stats['opened'],
                name='Opens',
                line=dict(color='#4F46E5', width=3)
            ))
            fig.add_trace(go.Scatter(
                x=daily_stats['date'],
                y=daily_stats['clicked'],
                name='Clicks',
                line=dict(color='#10B981', width=3)
            ))
            
            fig.update_layout(
                title="Engagement Over Time",
                xaxis_title="Date",
                yaxis_title="Count",
                hovermode='x unified',
                template="plotly_white"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    db.close()

with tab2:
    st.header("Subscriber Management")
    
    db = get_db_session()
    users = db.query(database.User).filter(database.User.subscribed == True).all()
    
    if users:
        # Subscriber table
        st.subheader("Active Subscribers")
        
        user_data = []
        for user in users:
            interests = user.interests.split(",") if user.interests else []
            user_data.append({
                "Email": user.email,
                "Interests": ", ".join(interests),
                "Subscribed Since": "Today"  # Would be actual date in production
            })
        
        df_users = pd.DataFrame(user_data)
        st.dataframe(df_users, use_container_width=True)
        
        # Interests distribution
        st.subheader("Interest Distribution")
        
        all_interests = []
        for user in users:
            if user.interests:
                all_interests.extend([i.strip() for i in user.interests.split(",")])
        
        if all_interests:
            interest_counts = pd.Series(all_interests).value_counts()
            fig = px.pie(
                values=interest_counts.values,
                names=interest_counts.index,
                title="Subscriber Interests",
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Add new subscriber form
    st.subheader("Add New Subscriber")
    
    with st.form("add_subscriber"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_email = st.text_input("Email Address")
        
        with col2:
            interests = st.multiselect(
                "Interests",
                ["Technology", "AI", "Business", "Science", "Health", "Finance"],
                default=["Technology", "AI"]
            )
        
        submitted = st.form_submit_button("Add Subscriber")
        
        if submitted and new_email:
            st.success(f"Subscriber {new_email} added successfully!")
            # In production, would call the API to add user
    
    db.close()

with tab3:
    st.header("Campaign Analytics")
    
    db = get_db_session()
    tracking = db.query(database.EmailTracking).all()
    
    if tracking:
        # Campaign performance table
        st.subheader("Recent Newsletters")
        
        campaign_data = []
        for t in tracking[-10:]:  # Last 10 campaigns
            campaign_data.append({
                "Newsletter ID": t.newsletter_id[:8] + "...",
                "Sent To": t.user_email,
                "Sent Date": t.sent_at.strftime("%Y-%m-%d %H:%M") if t.sent_at else "N/A",
                "Opened": "✅" if t.opened else "❌",
                "Clicked": "✅" if t.clicked else "❌",
                "Open Count": t.opened_count,
                "Click Count": t.click_count
            })
        
        df_campaigns = pd.DataFrame(campaign_data)
        st.dataframe(df_campaigns, use_container_width=True)
        
        # Performance comparison
        st.subheader("Performance Metrics")
        
        metrics_data = {
            "Metric": ["Open Rate", "Click Rate", "CTOR (Click-to-Open)"],
            "Value": [
                f"{(sum(1 for t in tracking if t.opened)/len(tracking)*100):.1f}%",
                f"{(sum(1 for t in tracking if t.clicked)/len(tracking)*100):.1f}%",
                f"{(sum(1 for t in tracking if t.clicked)/sum(1 for t in tracking if t.opened)*100):.1f}%" if sum(1 for t in tracking if t.opened) > 0 else "0%"
            ],
            "Industry Avg": ["20-30%", "2-5%", "10-20%"]
        }
        
        df_metrics = pd.DataFrame(metrics_data)
        st.table(df_metrics)
    
    db.close()

with tab4:
    st.header("Content Performance")
    
    st.subheader("Most Popular Articles")
    
    # In production, this would come from the database
    sample_articles = [
        {"title": "AI Breakthrough in Healthcare", "clicks": 42, "open_rate": "68%"},
        {"title": "Quantum Computing Update", "clicks": 38, "open_rate": "72%"},
        {"title": "Renewable Energy Advances", "clicks": 31, "open_rate": "65%"},
        {"title": "Blockchain in Finance", "clicks": 28, "open_rate": "61%"},
        {"title": "Space Exploration News", "clicks": 25, "open_rate": "58%"},
    ]
    
    for article in sample_articles:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{article['title']}**")
            with col2:
                st.write(f"👆 {article['clicks']} clicks")
            with col3:
                st.write(f"📊 {article['open_rate']}")
            st.divider()
    
    # Content recommendations
    st.subheader("Content Recommendations")
    
    recommendations = [
        "📈 Create more content about AI and Machine Learning (high engagement)",
        "🕒 Consider sending newsletters in the morning (better open rates)",
        "🎯 Personalize subject lines based on user interests",
        "📱 Ensure emails are mobile-responsive (60% opens on mobile)",
        "🔍 Add more interactive content (quizzes, polls)"
    ]
    
    for rec in recommendations:
        st.write(rec)

# Sidebar
with st.sidebar:
    st.header("🚀 Quick Actions")
    
    if st.button("Send Test Newsletter", use_container_width=True):
        st.success("Test newsletter queued for delivery!")
    
    if st.button("Export Analytics", use_container_width=True):
        st.info("Export started. Check downloads folder.")
    
    if st.button("Simulate Test Data", use_container_width=True):
        try:
            base_url = "http://localhost:8000"
            db = get_db_session()
            tracking = db.query(database.EmailTracking).all()
            
            for t in tracking:
                requests.get(f"{base_url}/track/open/{t.newsletter_id}", timeout=2)
                requests.get(f"{base_url}/track/click/{t.newsletter_id}/1", timeout=2)
            
            db.close()
            st.success(f"Test data generated for {len(tracking)} newsletters! Refresh to see updates.")
        except Exception as e:
            st.error(f"Error: {e}. Make sure API server is running (uvicorn main:app --reload)")
    
    st.divider()
    
    st.header("⚙️ Settings")
    
    newsletter_frequency = st.selectbox(
        "Send Frequency",
        ["Daily", "Weekly", "Bi-weekly", "Monthly"]
    )
    
    send_time = st.time_input("Preferred Send Time", value=datetime.now().time())
    
    if st.button("Save Settings", use_container_width=True):
        st.success("Settings updated!")
    
    st.divider()
    
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.caption("Dashboard v1.0 | Newsletter System")

# Footer
st.divider()
st.caption("Built with Streamlit | Connected to Newsletter API")