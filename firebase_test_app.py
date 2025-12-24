import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json

# --- Configuration ---
SERVICE_ACCOUNT_FILE = 'serviceAccountKey.json'

# --- Firebase Initialization ---
def init_firebase():
    """
    Initializes Firebase App safely.
    Checks if app is already initialized to avoid errors.
    """
    try:
        # Check if already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
            firebase_admin.initialize_app(cred)
            st.success("Firebase initialized successfully!")
        else:
            # Already initialized
            pass
            
        return firestore.client()
    except Exception as e:
        st.error(f"Failed to initialize Firebase: {e}")
        return None

# --- Database Operations ---

def save_data(db, collection_name, document_id, data):
    """
    Saves data to Firestore.
    """
    try:
        # specific document ID
        doc_ref = db.collection(collection_name).document(document_id)
        doc_ref.set(data)
        st.success(f"Data saved to collection '{collection_name}' with ID '{document_id}'")
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def read_data(db, collection_name, document_id):
    """
    Reads data from Firestore.
    """
    try:
        doc_ref = db.collection(collection_name).document(document_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            st.warning("No such document found!")
            return None
    except Exception as e:
        st.error(f"Error reading data: {e}")
        return None

# --- Main App ---
def main():
    st.title("Firebase Connection Test")
    
    st.info("This is a minimal example to test Firestore connection.")
    
    # Initialize DB
    db = init_firebase()
    
    if db:
        st.subheader("1. Save Data")
        with st.form("save_form"):
            col_name = st.text_input("Collection Name", "test_collection")
            doc_id = st.text_input("Document ID", "test_doc_1")
            name = st.text_input("Name", "John Doe")
            age = st.number_input("Age", 25)
            
            submitted = st.form_submit_button("Save to Firestore")
            if submitted:
                data = {"name": name, "age": age}
                save_data(db, col_name, doc_id, data)
        
        st.subheader("2. Read Data")
        with st.form("read_form"):
            read_col = st.text_input("Collection to Read", "test_collection")
            read_id = st.text_input("Doc ID to Read", "test_doc_1")
            
            read_submitted = st.form_submit_button("Read from Firestore")
            if read_submitted:
                result = read_data(db, read_col, read_id)
                if result:
                    st.json(result)

if __name__ == "__main__":
    main()
