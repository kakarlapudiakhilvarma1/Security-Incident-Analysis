"""
Configuration module for the Security Incident Analysis application.
Handles environment variables and application settings.
"""

import os
import warnings
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    
    # Suppress UserWarning about llm_cache
    warnings.filterwarnings("ignore", message="Importing llm_cache from langchain root module is no longer supported")

def get_api_key():
    """Get the Google API key from environment variables"""
    return os.environ.get("GOOGLE_API_KEY")

def set_api_key(api_key):
    """Set the Google API key in environment variables"""
    os.environ["GOOGLE_API_KEY"] = api_key

def check_api_key():
    """Check if the Google API key is set"""
    api_key = get_api_key()
    if not api_key:
        st.error("Google API key not found. Please set the GOOGLE_API_KEY environment variable.")
        # Add debug info to help troubleshoot
        st.error(f"Available environment variables: {[k for k in os.environ.keys() if not k.startswith('_')]}")
        return False
    return True

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "db" not in st.session_state:
        st.session_state.db = None
    if "conversation_chain" not in st.session_state:
        st.session_state.conversation_chain = None
    if "document_processed" not in st.session_state:
        st.session_state.document_processed = False

def configure_page():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="Security Incident Analysis Assistant",
        page_icon="🔐",
        layout="wide",
    )
