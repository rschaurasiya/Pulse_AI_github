import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# General Config
APP_NAME = "PulseAI"
APP_ICON = ""
PAGE_LAYOUT = "wide"

# API Keys
# Gemini (COMMENTED OUT - Using Groq instead)
# _keys_str = os.getenv("GEMINI_API_KEY", "")
# GEMINI_API_KEYS = [k.strip() for k in _keys_str.split(",") if k.strip()]

# Groq API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Firebase Web API Key (for Client Auth)
FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY", "")

# News Config
RSS_FEEDS = {
    "Technology": "https://feeds.feedburner.com/TechCrunch/",
    "Business": "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
    "Science": "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml",
    "World": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "Health": "https://rss.nytimes.com/services/xml/rss/nyt/Health.xml",
}

# Theme Colors (for custom CSS)
PRIMARY_COLOR = "#FF4B4B"
BACKGROUND_COLOR = "#0E1117"
TEXT_COLOR = "#FAFAFA"
SECONDARY_BACKGROUND_COLOR = "#262730"
