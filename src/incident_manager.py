"""
Incident manager module for the Security Incident Analysis application.
Handles creating, storing, and managing security incidents.
"""

import datetime
import uuid
import streamlit as st
from langchain_community.vectorstores import FAISS
from src.rag_system import initialize_rag_system, load_vector_db
from src.conversation import setup_conversation_chain

def save_incident_report(incident_data):
    """
    Save a new incident report to the database
    
    Args:
        incident_data: Dictionary containing incident information
        
    Returns:
        str: The generated incident ID
    """
    # Generate a unique ID for the incident
    incident_id = f"INC-{datetime.datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"

    # Create the incident report text
    incident_report = f"""
    Incident ID: {incident_id}
    Date: {incident_data['date']}
    Type: {incident_data['type']}
    Description: {incident_data['description']}
    Impact: {incident_data['impact']}
    Mitigation: {incident_data['mitigation']}
    """

    # Check if we already have a database
    embeddings, _ = initialize_rag_system()
    existing_db = load_vector_db(embeddings)  # This function now includes allow_dangerous_deserialization=True

    if existing_db:
        # Add the new incident to the existing database
        existing_db.add_texts([incident_report])
        existing_db.save_local("faiss_index")
        st.session_state.db = existing_db
    else:
        # Create a new database with just this incident
        st.session_state.db = FAISS.from_texts([incident_report], embeddings)
        st.session_state.db.save_local("faiss_index")

    return incident_id

def add_new_incident(incident_data):
    """Add a new security incident to the database"""
    try:
        # Save the incident
        incident_id = save_incident_report(incident_data)
        
        # Initialize RAG components if not already done
        if not st.session_state.conversation_chain:
            embeddings, llm = initialize_rag_system()
            st.session_state.conversation_chain = setup_conversation_chain(llm, st.session_state.db)
        
        st.session_state.document_processed = True
        return incident_id
    except Exception as e:
        st.error(f"Error adding incident: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None
