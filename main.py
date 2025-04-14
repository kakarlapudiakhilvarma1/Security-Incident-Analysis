"""
Main module for the Security Incident Analysis application.
Entry point for the Streamlit application.
"""

import streamlit as st
from src.config import load_environment, initialize_session_state, configure_page
from src.ui import render_sidebar, render_chat_interface

def main():
    """Main application entry point"""
    # Load environment variables
    load_environment()
    
    # Configure page settings
    configure_page()
    
    # Initialize session state
    initialize_session_state()
    
    # Display application title
    st.title("🔐 Security Incident Analysis Assistant")
    
    # Render sidebar
    render_sidebar()
    
    # Render main chat interface
    render_chat_interface()

if __name__ == "__main__":
    main()
