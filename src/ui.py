"""
UI module for the Security Incident Analysis application.
Handles Streamlit UI components and interactions.
"""

import os
import datetime
import streamlit as st
import traceback
from src.config import get_api_key, set_api_key
from src.data_loader import process_sample_data, process_uploaded_file, load_existing_index
from src.incident_manager import add_new_incident
from src.conversation import process_user_query

def render_sidebar():
    """Render the sidebar UI components"""
    with st.sidebar:
        st.header("Configuration")
        
        # Display LangChain version
        try:
            import langchain
            st.info(f"LangChain version: {langchain.__version__}")
        except Exception:
            st.warning("Could not detect LangChain version")
        
        # Option to manually input API key
        manual_api_key = st.text_input("Google API Key (optional)", type="password")
        if manual_api_key:
            set_api_key(manual_api_key)
            st.success("API key set!")
        
        # Display current API key status
        if get_api_key():
            st.success("Google API Key is configured")
        else:
            st.warning("Google API Key not found. Please enter it above or check your .env file")
        
        # Data source options
        st.subheader("Data Source")
        data_option = st.radio(
            "Choose data source:",
            ("Sample Data", "Upload Own Data", "Add New Incident", "Load Existing Index")
        )
        
        handle_data_source_selection(data_option)
        
        # Advanced options
        st.subheader("Advanced Options")
        if st.button("Reset Chat History"):
            st.session_state.conversation_history = []
            st.session_state.chat_history = []
            st.success("Chat history cleared")
        
        # Display system status
        st.subheader("System Status")
        status = "Ready" if st.session_state.document_processed else "Not Initialized"
        st.write(f"Status: {status}")
        st.write(f"Chat history entries: {len(st.session_state.chat_history)}")
        
        # Debug section
        if st.checkbox("Show Debug Info"):
            st.subheader("Debug Information")
            st.write(f"Database initialized: {st.session_state.db is not None}")
            st.write(f"Conversation chain initialized: {st.session_state.conversation_chain is not None}")

def handle_data_source_selection(data_option):
    """Handle the data source selection in the sidebar"""
    if data_option == "Sample Data":
        if st.button("Load Sample Data"):
            if not get_api_key():
                st.error("Google API key not found. Please set it manually or check your .env file.")
            else:
                with st.spinner("Loading sample data and initializing the system..."):
                    success = process_sample_data()
                    if success:
                        st.success("Sample data loaded successfully!")
    
    elif data_option == "Upload Own Data":
        uploaded_file = st.file_uploader("Upload security incidents JSON or CSV", type=["json", "csv"])
        
        if uploaded_file is not None:
            if st.button("Process Uploaded Data"):
                if not get_api_key():
                    st.error("Google API key not found. Please set it manually or check your .env file.")
                else:
                    with st.spinner("Processing uploaded data..."):
                        success = process_uploaded_file(uploaded_file)
                        if success:
                            st.success("Data processed successfully!")
    
    elif data_option == "Add New Incident":
        render_add_incident_form()
    
    elif data_option == "Load Existing Index":
        if st.button("Load Existing FAISS Index"):
            if not get_api_key():
                st.error("Google API key not found. Please set it manually or check your .env file.")
            else:
                with st.spinner("Loading existing FAISS index..."):
                    success = load_existing_index()
                    if success:
                        st.success("Existing index loaded successfully!")

def render_add_incident_form():
    """Render the form for adding a new security incident"""
    st.subheader("Add New Security Incident")
    
    incident_date = st.date_input("Incident Date", datetime.datetime.now())
    incident_type = st.selectbox("Incident Type", [
        "Phishing Attack", "Malware", "Ransomware", "DDoS", "Data Breach", 
        "Insider Threat", "SQL Injection", "XSS", "CSRF", "Other"
    ])
    
    incident_description = st.text_area("Description", height=100)
    incident_impact = st.text_area("Impact", height=100)
    incident_mitigation = st.text_area("Mitigation", height=100)
    
    if st.button("Add Incident"):
        if not get_api_key():
            st.error("Google API key not found. Please set it manually or check your .env file.")
        elif incident_description and incident_impact and incident_mitigation:
            # Collect incident data
            incident_data = {
                "date": incident_date.strftime("%Y-%m-%d"),
                "type": incident_type,
                "description": incident_description,
                "impact": incident_impact,
                "mitigation": incident_mitigation
            }
            
            incident_id = add_new_incident(incident_data)
            if incident_id:
                st.success(f"Incident {incident_id} added successfully!")
        else:
            st.error("Please fill in all fields.")

def render_chat_interface():
    """Render the main chat interface"""
    st.header("Security Incident Analysis Chat")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for i, (query, response) in enumerate(st.session_state.chat_history):
            st.info(f"Question: {query}")
            st.success(f"Response: {response}")
            st.divider()
    
    # Input for new queries
    st.subheader("Ask a Question")
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_query = st.text_area("Enter your security incident analysis question:", 
                             height=100, 
                             placeholder="Example: What patterns can we identify in recent phishing attacks?")
    
    with col2:
        st.markdown("##")  # Add spacing
        if st.button("Submit Question", use_container_width=True) and user_query:
            if not get_api_key():
                st.error("Google API key not found. Please set it manually or check your .env file.")
            elif st.session_state.document_processed:
                with st.spinner("Analyzing..."):
                    try:
                        # Process the query and update the UI
                        response = process_user_query(user_query)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error processing query: {str(e)}")
                        st.error(traceback.format_exc())
            else:
                st.error("Please initialize the system with security incident data first.")
