"""
Web scraper for fetching articles
"""
import requests
from bs4 import BeautifulSoup
import random


class NewsScraper:
    def __init__(self):
        self.sources = {
            "tech": [
                "https://techcrunch.com/",
                "https://www.theverge.com/",
                "https://arstechnica.com/"
            ],
            "ai": [
                "https://openai.com/blog",
                "https://www.anthropic.com/index"
            ],
            "business": [
                "https://www.bloomberg.com/",
                "https://www.economist.com/"
            ]
        }
    
    def scrape_techcrunch(self, url):
        """Scrape TechCrunch for article titles"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = []
            # Try different selectors
            for headline in soup.find_all(['h2', 'h3', 'h4'])[:10]:
                title = headline.get_text(strip=True)
                if len(title) > 20:  # Filter out short/navigation items
                    link = headline.find('a')
                    if link and link.get('href'):
                        article_url = link['href']
                        if not article_url.startswith('http'):
                            article_url = 'https://techcrunch.com' + article_url
                        
                        articles.append({
                            "title": title,
                            "url": article_url,
                            "source": "TechCrunch"
                        })
            
            return articles[:5]  # Return top 5
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return []
    
    def get_articles(self, interest, max_articles=3):
        """
        Get articles for a specific interest
        Returns list of articles with title, url, source
        """
        if interest not in self.sources:
            return []
        
        articles = []
        for source_url in self.sources[interest]:
            if "techcrunch" in source_url:
                articles.extend(self.scrape_techcrunch(source_url))
            
            # Add more sources here later
        
        # Return random selection (or all if less than max)
        if len(articles) > max_articles:
            return random.sample(articles, max_articles)
        return articles[:max_articles]


# Quick test
if __name__ == "__main__":
    scraper = NewsScraper()
    print("Testing scraper...")
    tech_articles = scraper.get_articles("tech")
    for article in tech_articles:
        print(f"- {article['title']}")