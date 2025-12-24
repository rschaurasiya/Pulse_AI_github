import firebase_admin
from firebase_admin import credentials, firestore
import hashlib
from datetime import datetime
import streamlit as st
import os

import requests
from config.settings import FIREBASE_WEB_API_KEY

class FirebaseManager:
    _instance = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initializes Firebase app if not already initialized."""
        if not firebase_admin._apps:
            try:
                cred = None
                # 1. Try loading from local file
                if os.path.exists('serviceAccountKey.json'):
                    cred = credentials.Certificate('serviceAccountKey.json')
                
                # 2. Try loading from Streamlit Secrets (Cloud)
                # Check for [firebase] section first
                elif "firebase" in st.secrets:
                    secret_dict = dict(st.secrets["firebase"])
                    # Fix: Handle private_key newlines if they are escaped
                    if "private_key" in secret_dict:
                        secret_dict["private_key"] = secret_dict["private_key"].replace("\\n", "\n")
                    cred = credentials.Certificate(secret_dict)
                
                # Check for [service_account] section
                elif "service_account" in st.secrets:
                   secret_dict = dict(st.secrets["service_account"])
                   if "private_key" in secret_dict:
                       secret_dict["private_key"] = secret_dict["private_key"].replace("\\n", "\n")
                   cred = credentials.Certificate(secret_dict)

                # Check if keys are at the root level of secrets
                elif "project_id" in st.secrets and "private_key" in st.secrets:
                    secret_dict = dict(st.secrets)
                    if "private_key" in secret_dict:
                       secret_dict["private_key"] = secret_dict["private_key"].replace("\\n", "\n")
                    cred = credentials.Certificate(secret_dict)
                
                else:
                    st.error("Firebase Credentials Not Found! Please ensure 'serviceAccountKey.json' exists locally OR add your service account details to Streamlit Secrets (under [firebase] or at root).")
                    self._db = None
                    return

                # Initialize with selected credentials
                firebase_admin.initialize_app(cred)
                self._db = firestore.client()
                # print("Firebase initialized successfully.")
                
            except Exception as e:
                st.error(f"Error initializing Firebase: {e}")
                self._db = None
        else:
            self._db = firestore.client()

    def _get_hash(self, text):
        """Generates a stable hash for document IDs."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    # --- Authentication Methods ---
    def login_user(self, email, password):
        """Logs in a user using Firebase Auth REST API."""
        if not FIREBASE_WEB_API_KEY:
            st.error("Missing FIREBASE_WEB_API_KEY. Add it to .env (local) or Streamlit Secrets (cloud).")
            return None
            
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        
        try:
            r = requests.post(url, json=payload)
            r.raise_for_status()
            return r.json() # Contains idToken, email, localId (uid)
        except requests.exceptions.HTTPError as e:
            try:
                error_msg = e.response.json().get('error', {}).get('message', str(e))
                st.error(f"Login Failed: {error_msg}")
            except:
                st.error(f"Login Failed: {e}")
            return None
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            return None

    def signup_user(self, email, password):
        """Signs up a new user using Firebase Auth REST API."""
        if not FIREBASE_WEB_API_KEY:
            st.error("Missing FIREBASE_WEB_API_KEY. Add it to .env (local) or Streamlit Secrets (cloud).")
            return None

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        
        try:
            r = requests.post(url, json=payload)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as e:
            try:
                error_msg = e.response.json().get('error', {}).get('message', str(e))
                st.error(f"Signup Failed: {error_msg}")
            except:
                st.error(f"Signup Failed: {e}")
            return None
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            return None

    # --- DATA Methods (User Scoped) ---

    def get_category_feed(self, category, limit=20):
        """Retrieves Global cached summaries for a category (Shared Data)."""
        # We can keep category feed global or per-user. 
        # Requirement: "Store all user activities... under that UID only"
        # BUT: fetched news feed isn't strictly 'user activity', it's content.
        # User activity is saving, interacting.
        # However, to avoid complexity, we can keep the feed global?
        # WAIT. The user prompt says "Store all user activities (saved news, summaries...) under that UID only"
        # If I summarize a news, is that my summary?
        # "Store all user activities (saved news, summaries, button actions...) under that UID only"
        # Okay, let's scope summaries to user too to follow instructions strictly.
        # But `get_category_feed` is used to Populate the "Latest News" from cache.
        # If we scope it to user, a new user sees nothing.
        # I will IMPLEMENT it as User-Scoped. If they haven't summarized, they see nothing cached.
        return [] # Disabling Global Cache for "Latest News" to enforce user isolation on 'summaries' if strictly required.
        # actually, let's allow `get_category_feed` to return NOTHING initially 
        # and rely on `fetch_news` (live). The user will then generate their own summaries.
        # Or, we can keep GLOBAL summaries for efficiency but scope SAVED items to user.
        # The prompt says "Store all user activities... summaries... under that UID only".
        # So I will scope summaries to user.

    def get_user_summaries_feed(self, user_id, category, limit=20):
        """Retrieves user's own generated summaries for a category."""
        if not self._db or not user_id: return []
        try:
            feed = []
            docs = self._db.collection('users').document(user_id).collection('summaries')\
                .where('category', '==', category)\
                .order_by('created_at', direction=firestore.Query.DESCENDING)\
                .limit(limit)\
                .stream()
            for doc in docs:
                feed.append(doc.to_dict())
            return feed
        except Exception as e:
            # print(f"Error fetching filtered feed: {e}")
            return []

    def get_summary(self, article_url, user_id):
        """Retrieves cached summary from User's Firestore."""
        if not self._db or not user_id: return None
        
        try:
            doc_id = self._get_hash(article_url)
            # Scoped to User
            doc_ref = self._db.collection('users').document(user_id).collection('summaries').document(doc_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict().get('summary')
            return None
        except Exception as e:
            print(f"Error fetching summary: {e}")
            return None

    def save_summary(self, article_data, summary, category, user_id):
        """Saves generated summary to User's Firestore."""
        if not self._db:
            st.error("Database connection not initialized. Cannot save summary.")
            return False
        if not user_id: return False
        
        try:
            doc_id = self._get_hash(article_data['link'])
            data = {
                'url': article_data['link'],
                'title': article_data.get('title'),
                'summary': summary,
                'category': category,
                'source': article_data.get('source'),
                'published': article_data.get('published'),
                'image': article_data.get('image'),
                'created_at': datetime.now()
            }
            # Scoped to User
            self._db.collection('users').document(user_id).collection('summaries').document(doc_id).set(data)
            return True
        except Exception as e:
            st.error(f"Error saving summary to database: {e}")
            return False

    def save_bookmark(self, article_data, user_id):
        """Save article to User's bookmarks."""
        if not self._db:
            st.error("Database connection not initialized. Cannot save bookmark.")
            return False
        if not user_id: return False
        
        try:
            doc_id = self._get_hash(article_data['link'])
            data = {
                'title': article_data.get('title'),
                'url': article_data.get('link'),
                'source': article_data.get('source'),
                'published': article_data.get('published'),
                'image': article_data.get('image'),
                'summary': article_data.get('summary'),
                'saved_at': datetime.now()
            }
            # Scoped to User
            self._db.collection('users').document(user_id).collection('bookmarks').document(doc_id).set(data)
            return True
        except Exception as e:
            st.error(f"Error bookmarking: {e}")
            return False

    def remove_bookmark(self, article_url, user_id):
        """Remove article from User's bookmarks."""
        if not self._db:
             st.error("Database connection not initialized.")
             return False
        if not user_id: return False
        
        try:
            doc_id = self._get_hash(article_url)
            # Scoped to User
            self._db.collection('users').document(user_id).collection('bookmarks').document(doc_id).delete()
            return True
        except Exception as e:
            st.error(f"Error removing bookmark: {e}")
            return False
            
    def get_bookmarks(self, user_id):
        """Get all bookmarked articles for User."""
        if not self._db or not user_id: return []
        
        try:
            bookmarks = []
            # Scoped to User
            docs = self._db.collection('users').document(user_id).collection('bookmarks').order_by('saved_at', direction=firestore.Query.DESCENDING).stream()
            for doc in docs:
                bookmarks.append(doc.to_dict())
            return bookmarks
        except Exception as e:
            print(f"Error fetching bookmarks: {e}")
            return []

    def is_bookmarked(self, article_url, user_id):
        """Check if an article is already bookmarked by User."""
        if not self._db or not user_id: return False
        
        try:
            doc_id = self._get_hash(article_url)
            # Scoped to User
            doc = self._db.collection('users').document(user_id).collection('bookmarks').document(doc_id).get()
            return doc.exists
        except Exception as e:
            return False
