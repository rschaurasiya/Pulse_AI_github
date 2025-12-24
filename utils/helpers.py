import streamlit as st
from datetime import datetime
import re

def load_css(theme="Dark"):
    """Injects custom CSS to style the Streamlit app based on theme."""
    
    # --- DESIGN SYSTEM VARIABLES ---
    if theme == "Dark":
        # Dark Theme Palette
        current_theme = {
            "bg_color": "#0E1117",
            "secondary_bg": "#262730",
            "text_color": "#FAFAFA",
            "secondary_text": "#BDC1C6",
            "card_bg": "#161b22",
            "card_border": "rgba(255, 255, 255, 0.1)",
            "primary": "#FF4B4B",
            "primary_hover": "#FF3333",
            "success": "#00C851",
            "shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.5), 0 2px 4px -1px rgba(0, 0, 0, 0.3)"
        }
    else:
        # Light Theme Palette
        current_theme = {
            "bg_color": "#FFFFFF",
            "secondary_bg": "#F0F2F6",
            "text_color": "#333333", # Darker text for readability
            "secondary_text": "#555555",
            "card_bg": "#FFFFFF",
            "card_border": "rgba(0, 0, 0, 0.1)",
            "primary": "#FF4B4B",
            "primary_hover": "#FF3333",
            "success": "#28A745",
            "shadow": "0 2px 5px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)"
        }

    css = f"""
    <style>
    /* -------------------------------------------------------------------------- */
    /*                                GLOBAL STYLES                               */
    /* -------------------------------------------------------------------------- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    
    .stApp {{
        background-color: {current_theme['bg_color']};
        color: {current_theme['text_color']};
    }}

    /* -------------------------------------------------------------------------- */
    /*                                   SIDEBAR                                  */
    /* -------------------------------------------------------------------------- */
    [data-testid="stSidebar"] {{
        background-color: {current_theme['secondary_bg']};
        border-right: 1px solid {current_theme['card_border']};
    }}

    /* Strictly force text color for all sidebar elements to ensure visibility in Light Mode */
    [data-testid="stSidebar"] *, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label {{
        color: {current_theme['text_color']} !important;
    }}
    
    /* Specific overrides for Headers in Sidebar */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {{
        color: {current_theme['text_color']} !important;
    }}

    /* -------------------------------------------------------------------------- */
    /*                                 NEWS CARDS                                 */
    /* -------------------------------------------------------------------------- */
    .news-card {{
        background-color: {current_theme['card_bg']};
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 24px;
        border: 1px solid {current_theme['card_border']};
        box-shadow: {current_theme['shadow']};
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    
    .news-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }}

    .news-title {{
        font-size: 1.25rem;
        font-weight: 700;
        color: {current_theme['text_color']};
        text-decoration: none;
        margin-bottom: 0.75rem;
        display: block;
        line-height: 1.4;
    }}
    
    .news-title:hover {{
        color: {current_theme['primary']};
    }}

    .news-meta {{
        font-size: 0.85rem;
        color: {current_theme['secondary_text']};
        font-weight: 500;
        margin-bottom: 1.25rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }}

    .summary-section {{
        margin-top: 16px;
        padding: 16px;
        background-color: {current_theme['bg_color']}; /* Contrast for summary */
        border-radius: 8px;
        border-left: 4px solid {current_theme['primary']};
    }}

    .summary-text {{
        font-size: 0.95rem;
        line-height: 1.6;
        color: {current_theme['text_color']};
    }}

    /* -------------------------------------------------------------------------- */
    /*                                   BUTTONS                                  */
    /* -------------------------------------------------------------------------- */
    
    /* Default Primary Button (Save/Listen) */
    .stButton > button {{
        background-color: {current_theme['primary']};
        color: #FFFFFF !important; /* Always White Text on Red Button */
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.25rem;
        font-weight: 600;
        font-size: 0.9rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        transition: all 0.2s;
        width: 100%;
    }}

    .stButton > button:hover {{
        background-color: {current_theme['primary_hover']};
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        color: #FFFFFF !important;
    }}
    
    .stButton > button:active {{
        transform: scale(0.98);
    }}
    
    /* -------------------------------------------------------------------------- */
    /*                                  UTILITIES                                 */
    /* -------------------------------------------------------------------------- */
    /* Hide Default Menu/Footer */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def clean_html(raw_html):
    """Remove HTML tags from a string."""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def format_date(date_str):
    """Try to parse and format date string."""
    try:
        # Common RSS format: Sat, 21 Dec 2024 10:00:00 GMT
        dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z")
        return dt.strftime("%B %d, %Y • %I:%M %p")
    except:
        return date_str
