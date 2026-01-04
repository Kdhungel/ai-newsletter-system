"""
AI-powered article summarizer (with mock mode for development)
"""
import os
import random
from dotenv import load_dotenv

load_dotenv()

MOCK_MODE = True  # Set to False when you have OpenAI credits


class ArticleSummarizer:
    def __init__(self):
        self.mock_mode = MOCK_MODE
    
    def summarize_article(self, title, url, max_length=150):
        """
        Generate a concise summary of an article
        """
        if self.mock_mode:
            # Mock summaries for development
            mock_summaries = [
                f"Big news in {title.split()[0]}: This development could reshape the industry.",
                f"Analysis: {title}. Key insights for professionals following this space.",
                f"Breaking: {title}. What this means for the future of technology.",
                f"Update on {title.split()[0]}: Important implications for stakeholders.",
                f"Expert take: {title}. Why this matters right now."
            ]
            return random.choice(mock_summaries)
        
        # Real OpenAI code would go here
        return f"Interesting development in {title.split()[0]}... Read more at {url}"
    
    def personalize_summary(self, summary, user_interests):
        """
        Add personalization based on user interests
        """
        if self.mock_mode:
            interests_str = " & ".join(user_interests[:2])
            personalizations = [
                f"Hey {interests_str} enthusiast! {summary}",
                f"Given your interest in {interests_str}: {summary}",
                f"Thought you'd like this as a {user_interests[0]} follower: {summary}",
                f"Relevant to your {interests_str} interests: {summary}"
            ]
            return random.choice(personalizations)
        
        return summary


# Test
if __name__ == "__main__":
    summarizer = ArticleSummarizer()
    
    test_title = "Tesla annual sales decline 9% as it’s overtaken by BYD as global EV leader"
    test_url = "https://example.com"
    
    summary = summarizer.summarize_article(test_title, test_url)
    print("Summary:", summary)
    
    personalized = summarizer.personalize_summary(summary, ["tech", "business"])
    print("\nPersonalized:", personalized)