import streamlit as st
from config.settings import APP_NAME, APP_ICON, PAGE_LAYOUT
from utils.helpers import load_css, format_date
from services.news_fetcher import fetch_news, get_available_categories
from services.gemini_summarizer import summarize_text
from services.text_to_speech import text_to_audio
from services.translator import translate_to_hindi
from services.firebase_manager import FirebaseManager

# Page Configuration
st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout=PAGE_LAYOUT
)

# Initialize Firebase
fb_manager = FirebaseManager()

# Helper to reset UI state
def reset_ui_state():
    """Clears all ephemeral UI state (expanded summaries, audio)"""
    keys_to_clear = [k for k in st.session_state.keys() if k.startswith((
        "show_summary_", "show_saved_summary_", 
        "audio_", "saved_audio_", 
        "summarizing_", "summarizing_saved_"
    ))]
    for k in keys_to_clear:
        del st.session_state[k]

def update_url_routing(mode, user_email=""):
    """Updates the URL query parameters based on mode: 'login', 'saved', 'latest'."""
    st.query_params.clear()
    
    if mode == 'login':
        st.query_params["login"] = ""
    elif mode == 'saved':
        st.query_params["saved"] = ""
    elif mode == 'latest':
        # Extract username from email (part before @)
        username = user_email.split('@')[0] if user_email else "user"
        st.query_params[username] = ""

def get_view_mode_from_url():
    """Parses URL to determine current view mode."""
    params = st.query_params.keys()
    if "saved" in params:
        return "Saved Articles"
    if "login" in params:
        return "Login"
    # If a username is present (or any other key), default to Latest News if logged in
    return "Latest News"

def login_page():
    # Enforce URL: /?login
    if "login" not in st.query_params:
        update_url_routing('login')
    
    st.title(f"{APP_NAME} - Login")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    with st.spinner("Logging in..."):
                        user_info = fb_manager.login_user(email, password)
                        if user_info:
                            st.session_state.user = user_info
                            st.success("Logged in successfully!")
                            st.rerun()

    with tab2:
        with st.form("signup_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Sign Up")
            
            if submitted:
                if not email or not password:
                    st.error("Please fill in all fields.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    with st.spinner("Creating account..."):
                        user_info = fb_manager.signup_user(email, password)
                        if user_info:
                            st.session_state.user = user_info
                            st.success("Account created successfully!")
                            st.rerun()

def main():
    
    # --- Authentication Check ---
    if "user" not in st.session_state:
        st.session_state.user = None
        
    if not st.session_state.user:
        login_page()
        return

    user_id = st.session_state.user['localId']
    user_email = st.session_state.user.get('email', 'User')

    # --- Navigation Logic with History Support ---
    
    # 1. Determine Desired View from URL or Default
    current_url_view = get_view_mode_from_url()
    if current_url_view == "Login": 
        # If logged in but URL says login, redirect to Latest
        current_url_view = "Latest News"
        
    # 2. Sidebar Navigation
    with st.sidebar:
        st.title(f"{APP_NAME}")
        st.write(f"Logged in as: **{user_email}**")
        
        # --- Theme Toggle ---
        if "theme" not in st.session_state:
            st.session_state.theme = "Dark"
            
        # We use a toggle for Light/Dark
        is_dark = st.session_state.theme == "Dark"
        dark_mode_on = st.toggle("Dark Mode", value=is_dark)
        
        new_theme = "Dark" if dark_mode_on else "Light"
        if new_theme != st.session_state.theme:
            st.session_state.theme = new_theme
            st.rerun()

        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()
            
        st.markdown("---")
        
        # Map options
        options = ["Latest News", "Saved Articles"]
        try:
            default_index = options.index(current_url_view)
        except ValueError:
            default_index = 0
        
        # Track last known URL state to detect browser back/forward
        # We construct a signature like 'saved' or 'latest' to compare
        url_sig = "saved" if "saved" in st.query_params else "latest"
        
        if "last_url_sig" not in st.session_state:
            st.session_state.last_url_sig = url_sig
            
        # Detect Browser Navigation
        if st.session_state.last_url_sig != url_sig:
            st.session_state.last_url_sig = url_sig
            reset_ui_state()
            # Force Rerun to update radio default index
            st.rerun()
            
        view_option = st.radio("Navigation", options, index=default_index, key=f"nav_radio_{url_sig}")
        
        # 3. Handle Navigation Change (User Click)
        if view_option != current_url_view:
            if view_option == "Saved Articles":
                update_url_routing('saved')
                st.session_state.last_url_sig = "saved"
            else:
                update_url_routing('latest', user_email)
                st.session_state.last_url_sig = "latest"
                
            reset_ui_state()
            st.rerun()
            
        # Ensure URL is correct on initial load (e.g. if arriving with no params)
        if not st.query_params and view_option == "Latest News":
             update_url_routing('latest', user_email)

        st.markdown("---")
        
        if view_option == "Latest News":
            st.subheader("News Settings")
            category = st.selectbox(
                "Select Category",
                get_available_categories()
            )
            
            # Check Category Persistence and Reset if changed
            if "last_category" not in st.session_state:
                st.session_state.last_category = category
            
            if category != st.session_state.last_category:
                reset_ui_state()
                st.session_state.last_category = category
        
        st.markdown("---")
        st.info("Powered by Groq (Llama 3.3), NewsAPI, GNews & RSS Feeds")

    # Load Custom CSS with Theme (Called after sidebar logic)
    load_css(st.session_state.theme)

    # Handle View Selection
    if view_option == "Saved Articles":
        st.title("Saved Articles")
        bookmarks = fb_manager.get_bookmarks(user_id)
        
        if not bookmarks:
            st.info("No saved articles yet. Go to 'Latest News' and click 'Save' to bookmark articles.")
            return

        for i, item in enumerate(bookmarks):
             with st.container():
                # Use Hash key for stability
                item_key = fb_manager._get_hash(item.get('url'))
                
                show_summary = st.session_state.get(f"show_saved_summary_{item_key}", False)
                summary_text = item.get('summary', 'No summary available.') if show_summary else ""

                # --- CARD START ---
                st.markdown(f"""
                <div class="news-card">
                    <a href="{item.get('url')}" target="_blank" class="news-title">{item.get('title')}</a>
                    <div class="news-meta">
                        <span>Date: {format_date(item.get('published'))}</span>
                        <span>|</span>
                        <span>Source: {item.get('source', 'Unknown Source')}</span>
                    </div>
                """, unsafe_allow_html=True)

                if show_summary:
                    st.markdown(f"""
                    <div class="summary-section">
                        <div class="summary-text">{summary_text}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True) # Close Card

                # --- ACTIONS ---
                col_s_actions, col_s_audio = st.columns([1.5, 2])
                
                with col_s_actions:
                    # Summarize Button / Badge Logic
                    if show_summary:
                         st.markdown(":white_check_mark: **Summarized**")
                    else:
                        is_summarizing = st.session_state.get(f"summarizing_saved_{item_key}", False)
                        btn_text = "Summarize" if not is_summarizing else "Observing..."
                        if st.button(btn_text, key=f"btn_saved_{item_key}", disabled=is_summarizing, use_container_width=True):
                             # Just toggle visibility since data is presumed saved with summary or fetchable
                             st.session_state[f"show_saved_summary_{item_key}"] = True
                             st.rerun()

                # Audio Controls (In Saved View)
                if show_summary:
                     with col_s_audio:
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("Listen (EN)", key=f"saved_en_{item_key}", use_container_width=True):
                                st.session_state[f"saved_audio_en_{item_key}"] = True
                                st.session_state[f"saved_audio_hi_{item_key}"] = False
                        with c2:
                            if st.button("Listen (HI)", key=f"saved_hi_{item_key}", use_container_width=True):
                                 st.session_state[f"saved_audio_hi_{item_key}"] = True
                                 st.session_state[f"saved_audio_en_{item_key}"] = False

                     # Audio Processing
                     if st.session_state.get(f"saved_audio_en_{item_key}"):
                        with st.spinner("Generating English audio..."):
                            ab = text_to_audio(item.get('summary', ''), lang='en')
                            if ab: st.audio(ab, format='audio/mp3', autoplay=True)
                    
                     if st.session_state.get(f"saved_audio_hi_{item_key}"):
                        with st.spinner("Translating..."):
                            hs = translate_to_hindi(item.get('summary', ''))
                            if hs:
                                ab = text_to_audio(hs, lang='hi')
                                if ab: st.audio(ab, format='audio/mp3', autoplay=True)

                # Remove Action
                with col_s_actions:
                    if st.button("Remove", key=f"del_{item_key}", use_container_width=True):
                        fb_manager.remove_bookmark(item.get('url'), user_id)
                        st.toast("Removed from bookmarks!")
                        st.rerun()
                
                st.markdown("<br>", unsafe_allow_html=True)
        return  # Stop execution here for Saved View

    # Main Content - Latest News
    st.title(f"{category} News")
    
    # Session State Persistence for News Feed
    if "category_cache" not in st.session_state:
        st.session_state.category_cache = {}

    # Determine if we need to fetch new data
    cached_data = st.session_state.category_cache.get(category)
    should_fetch = cached_data is None

    # Force Refresh Button
    col_ref, col_page = st.columns([1, 1])
    with col_ref:
        if st.button("Force Refresh"):
            should_fetch = True
    
    if should_fetch:
        # --- START FETCH LOGIC ---
        
        # 1. Check User Scoped Summaries Cache (optional logic)
        # For Main Feed, we mainly fetch LIVE news. We can implement a smarter merge if needed.
        # fb_manager.get_user_summaries_feed(user_id, category) 
        # But for now, let's keep fetch_news() as is, and check individual items for existing summaries.
        
        news_items = []
        is_refresh_click = (category in st.session_state.category_cache) and should_fetch
        
        # We always fetch live news for main feed to ensure freshness
        fetch_msg_container = st.empty()
        if is_refresh_click:
            fetch_msg_container.info("Fetching live news...")
        else:
            fetch_msg_container.info("Fetching latest news...")
            
        with st.spinner(f"Fetching {category} news..."):
            live_news = fetch_news(category)
        
        fetch_msg_container.empty()
        
        if not live_news:
            st.warning("No news found. Please check your internet connection.")
            return 

        # Merge with User Summaries Logic
        # We want to check if the user already has a summary for these items
        news_items = live_news 
        for item in news_items:
            existing_summary = fb_manager.get_summary(item['link'], user_id)
            if existing_summary:
                item['summary'] = existing_summary
    
        # SAVE TO CATEGORY CACHE
        st.session_state.category_cache[category] = {
            "items": news_items,
            "page": 0
        }
    else:
        # Load from Category Cache
        news_items = st.session_state.category_cache[category]["items"]

    # Display Logic - Next/Previous Pagination
    total_news = len(news_items)
    items_per_page = 10
    num_pages = (total_news + items_per_page - 1) // items_per_page
    
    current_page = st.session_state.category_cache[category]["page"]
    start_idx = current_page * items_per_page
    end_idx = min(start_idx + items_per_page, total_news)
    
    st.markdown(f"<div style='margin-bottom: 20px; font-weight: 500; color: gray;'>Showing {start_idx + 1} - {end_idx} of {total_news} articles</div>", unsafe_allow_html=True)
    
    # News Loop
    for i in range(start_idx, end_idx):
        item = news_items[i]
        item_key = fb_manager._get_hash(item['link'])
        
        show_summary = st.session_state.get(f"show_summary_{item_key}", False)
        summary_to_show = item.get('summary', '') if show_summary else ""
        
        # --- CARD START ---
        with st.container():
            # Card Wrapper
            st.markdown(f"""
            <div class="news-card">
                <a href="{item['link']}" target="_blank" class="news-title">{item['title']}</a>
                <div class="news-meta">
                    <span>Date: {format_date(item['published'])}</span>
                    <span>|</span>
                    <span>Source: {item.get('source', 'Unknown Source')}</span>
                </div>
            """, unsafe_allow_html=True)

            # --- SUMMARY SECTION (Conditionally Rendered) ---
            if show_summary:
                st.markdown(f"""
                <div class="summary-section">
                    <div class="summary-text">{summary_to_show}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True) # Close Card
            
            # --- ACTION BUTTONS ---
            col_actions, col_audio = st.columns([1.5, 2])
            
            # 1. Summarize / Saved Status
            with col_actions:
                if show_summary:
                    st.markdown(":white_check_mark: **Summarized**")
                else:
                    summarizing_key = f"summarizing_{item_key}"
                    is_summarizing = st.session_state.get(summarizing_key, False)
                    btn_text = "Summarize" if not is_summarizing else "Analyzing..."
                    
                    if st.button(btn_text, key=f"btn_{item_key}", disabled=is_summarizing, use_container_width=True):
                        st.session_state[summarizing_key] = True
                        st.rerun()

            # 2. Audio Controls
            if show_summary and item.get('summary'):
                with col_audio:
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Listen (EN)", key=f"en_{item_key}", use_container_width=True):
                            st.session_state[f"audio_en_{item_key}"] = True
                            st.session_state[f"audio_hi_{item_key}"] = False
                    with c2:
                        if st.button("Listen (HI)", key=f"hi_{item_key}", use_container_width=True):
                            st.session_state[f"audio_hi_{item_key}"] = True
                            st.session_state[f"audio_en_{item_key}"] = False

                if st.session_state.get(f"audio_en_{item_key}"):
                    with st.spinner("Generating audio..."):
                        ab = text_to_audio(item['summary'], lang='en')
                        if ab: st.audio(ab, format='audio/mp3', autoplay=True)
                
                if st.session_state.get(f"audio_hi_{item_key}"):
                    with st.spinner("Translating..."):
                        hs = translate_to_hindi(item['summary'])
                        if hs:
                            ab = text_to_audio(hs, lang='hi')
                            if ab: st.audio(ab, format='audio/mp3', autoplay=True)

            # Save Button
            is_saved = fb_manager.is_bookmarked(item['link'], user_id)
            if not is_saved:
                 with col_actions:
                    if st.button("Save", key=f"save_{item_key}"):
                         with st.spinner("Saving..."):
                            existing = fb_manager.get_summary(item['link'], user_id)
                            if existing:
                                s_save = existing
                            else:
                                t = f"{item.get('title')}. {item.get('summary', '')}"
                                s_save = summarize_text(t)
                            
                            # Always save both summary and bookmark
                            success_summary = fb_manager.save_summary(item, s_save, category, user_id)
                            success_bookmark = fb_manager.save_bookmark(item, user_id)
                            
                            if success_summary and success_bookmark:
                                item['summary'] = s_save
                                st.session_state[f"show_summary_{item_key}"] = True
                                st.toast("Article Saved!")
                                st.rerun()
                            else:
                                st.error("Failed to save article. Check your connection or Firebase configuration.")
            else:
                 with col_actions:
                     st.caption("✅ Saved")

            # Handle Summarization
            if st.session_state.get(f"summarizing_{item_key}"):
                with st.spinner("Reading article..."):
                    existing = fb_manager.get_summary(item['link'], user_id)
                    if existing:
                        item['summary'] = existing
                    else:
                        t = f"{item.get('title')}. {item.get('summary', '')}"
                        item['summary'] = summarize_text(t)
                        fb_manager.save_summary(item, item['summary'], category, user_id)
                    
                    st.session_state[f"show_summary_{item_key}"] = True
                    st.session_state[f"summarizing_{item_key}"] = False
                    st.rerun()
             
            st.markdown("<br>", unsafe_allow_html=True) # Spacer

    # Pagination Navigation
    st.markdown("---")
    col_prev, col_center, col_next = st.columns([1, 2, 1])
    
    with col_prev:
        if current_page > 0:
            if st.button("Previous Page"):
                reset_ui_state()
                st.session_state.category_cache[category]["page"] -= 1
                st.rerun()
    
    with col_center:
        st.markdown(f"<p style='text-align: center;'>Page {current_page + 1} of {num_pages}</p>", unsafe_allow_html=True)
                
    with col_next:
        if current_page < num_pages - 1:
            if st.button("Next Page"):
                reset_ui_state()
                st.session_state.category_cache[category]["page"] += 1
                st.rerun()

if __name__ == "__main__":
    main()
