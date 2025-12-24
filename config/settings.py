import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_secret(key_name, required=True):
    """
    Retrieves API keys/secrets from Streamlit Cloud or local .env file.
    
    Priority:
    1. st.secrets (Streamlit Cloud)
    2. os.getenv (local .env file)
    
    Args:
        key_name: Name of the secret/environment variable
        required: If True, raises error when key is missing
        
    Returns:
        The secret value or None if not required and not found
        
    Raises:
        ValueError: If required=True and key is not found in either source
    """
    value = None
    
    # Try st.secrets first (Streamlit Cloud)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and key_name in st.secrets:
            value = st.secrets[key_name]
    except (ImportError, FileNotFoundError, KeyError):
        # st.secrets not available or key not found
        pass
    
    # Fall back to environment variable (local .env)
    if value is None:
        value = os.getenv(key_name)
    
    # Handle missing required keys
    if required and not value:
        error_msg = (
            f"Missing required API key: '{key_name}'\n\n"
            f"For local development:\n"
            f"  - Add '{key_name}=your_key_here' to your .env file\n\n"
            f"For Streamlit Cloud:\n"
            f"  - Add '{key_name}' to your app's Secrets management\n"
            f"  - Go to: App Settings → Secrets → Edit Secrets\n"
            f"  - Format: {key_name} = \"your_key_here\""
        )
        raise ValueError(error_msg)
    
    return value if value else None

# General Config
APP_NAME = "PulseAI"
APP_ICON = ""
PAGE_LAYOUT = "wide"

# API Keys - Load securely from st.secrets or .env
GROQ_API_KEY = get_secret("GROQ_API_KEY", required=True)
FIREBASE_WEB_API_KEY = get_secret("FIREBASE_WEB_API_KEY", required=True)
NEWS_API_KEY = get_secret("NEWS_API_ORG", required=False)  # Optional
GNEWS_API_KEY = get_secret("GNEWS_IO", required=False)     # Optional

# Gemini (COMMENTED OUT - Using Groq instead)
# GEMINI_API_KEY = get_secret("GEMINI_API_KEY", required=False)

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
