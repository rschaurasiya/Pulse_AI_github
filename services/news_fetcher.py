import os
import requests
import feedparser
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API keys from environment
NEWS_API_KEY = os.getenv('NEWS_API_ORG')
GNEWS_API_KEY = os.getenv('GNEWS_IO')

# RSS Feeds by category
RSS_FEEDS = {
    "Technology": [
        "https://feeds.bbci.co.uk/news/technology/rss.xml",
        "https://techcrunch.com/feed/",
        "https://www.wired.com/feed/rss"
    ],
    "Business": [
        "https://feeds.bbci.co.uk/news/business/rss.xml",
        "https://www.cnbc.com/id/100003114/device/rss/rss.html"
    ],
    "Entertainment": [
        "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
        "https://ew.com/feed/"
    ],
    "Health": [
        "https://feeds.bbci.co.uk/news/health/rss.xml",
        "https://www.medicalnewstoday.com/rss"
    ],
    "Science": [
        "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
        "https://www.sciencedaily.com/rss/all.xml"
    ],
    "Sports": [
        "https://feeds.bbci.co.uk/sport/rss.xml",
        "https://www.espn.com/espn/rss/news"
    ],
    "General": [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://rss.cnn.com/rss/edition.rss"
    ]
}

# Category mappings for both APIs
NEWSAPI_CATEGORIES = {
    "Technology": "technology",
    "Business": "business",
    "Entertainment": "entertainment",
    "Health": "health",
    "Science": "science",
    "Sports": "sports",
    "General": "general"
}

GNEWS_CATEGORIES = {
    "Technology": "technology",
    "Business": "business",
    "Entertainment": "entertainment",
    "Health": "health",
    "Science": "science",
    "Sports": "sports",
    "World": "world",
    "Nation": "nation"
}

def get_available_categories():
    """Returns list of available news categories"""
    return list(NEWSAPI_CATEGORIES.keys())

def fetch_from_newsapi(category="Technology", max_results=5):
    """
    Fetches news from NewsAPI.org
    Returns a list of news items
    """
    if not NEWS_API_KEY:
        print("NewsAPI key not found in .env file")
        return []
    
    try:
        category_param = NEWSAPI_CATEGORIES.get(category, "general")
        url = f"https://newsapi.org/v2/top-headlines"
        params = {
            'category': category_param,
            'country': 'us',
            'apiKey': NEWS_API_KEY,
            'pageSize': max_results
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        news_items = []
        if data.get('status') == 'ok':
            for article in data.get('articles', []):
                item = {
                    "title": article.get('title', 'No Title'),
                    "link": article.get('url', '#'),
                    "published": article.get('publishedAt', datetime.now().isoformat()),
                    "summary": article.get('description', 'No description available'),
                    "image": article.get('urlToImage'),
                    "source": f"NewsAPI - {article.get('source', {}).get('name', 'Unknown')}"
                }
                news_items.append(item)
        
        return news_items
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from NewsAPI: {e}")
        return []

def fetch_from_gnews(category="Technology", max_results=5):
    """
    Fetches news from GNews.io
    Returns a list of news items
    """
    if not GNEWS_API_KEY:
        print("GNews API key not found in .env file")
        return []
    
    try:
        category_param = GNEWS_CATEGORIES.get(category, "general")
        url = f"https://gnews.io/api/v4/top-headlines"
        params = {
            'category': category_param,
            'lang': 'en',
            'country': 'us',
            'apikey': GNEWS_API_KEY,
            'max': max_results
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        news_items = []
        for article in data.get('articles', []):
            item = {
                "title": article.get('title', 'No Title'),
                "link": article.get('url', '#'),
                "published": article.get('publishedAt', datetime.now().isoformat()),
                "summary": article.get('description', 'No description available'),
                "image": article.get('image'),
                "source": f"GNews - {article.get('source', {}).get('name', 'Unknown')}"
            }
            news_items.append(item)
        
        return news_items
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from GNews: {e}")
        return []

def fetch_from_rss(category="Technology", max_results=5):
    """
    Fetches news from RSS feeds
    Returns a list of news items
    """
    rss_urls = RSS_FEEDS.get(category, RSS_FEEDS["General"])
    news_items = []
    
    for rss_url in rss_urls:
        try:
            feed = feedparser.parse(rss_url)
            
            # Get the source name from the feed title
            source_name = feed.feed.get('title', 'RSS Feed')
            
            # Process each entry in the feed
            for entry in feed.entries[:max_results]:
                # Get published date
                published = entry.get('published', entry.get('updated', datetime.now().isoformat()))
                
                # Get summary/description
                summary = entry.get('summary', entry.get('description', 'No description available'))
                
                # Remove HTML tags from summary if present
                from bs4 import BeautifulSoup
                if '<' in summary:
                    soup = BeautifulSoup(summary, 'html.parser')
                    summary = soup.get_text()
                
                item = {
                    "title": entry.get('title', 'No Title'),
                    "link": entry.get('link', '#'),
                    "published": published,
                    "summary": summary[:500],  # Limit summary length
                    "image": entry.get('media_content', [{}])[0].get('url') if entry.get('media_content') else None,
                    "source": f"RSS - {source_name}"
                }
                news_items.append(item)
            
        except Exception as e:
            print(f"Error fetching from RSS feed {rss_url}: {e}")
            continue
    
    return news_items[:max_results]

def fetch_news(category="Technology"):
    """
    Fetches news from NewsAPI.org, GNews.io, and RSS feeds
    Combines and returns a list of dictionaries containing title, link, published, summary, and source.
    """
    all_news = []
    
    # Fetch from all three sources - Increased limits for pagination
    newsapi_items = fetch_from_newsapi(category, max_results=10)
    gnews_items = fetch_from_gnews(category, max_results=10)
    rss_items = fetch_from_rss(category, max_results=20)
    
    # Combine results
    all_news.extend(newsapi_items)
    all_news.extend(gnews_items)
    all_news.extend(rss_items)
    
    # Sort by published date (most recent first)
    try:
        all_news.sort(key=lambda x: x['published'], reverse=True)
    except:
        pass  # If sorting fails, keep original order
    
    return all_news  # Return all fetched articles
