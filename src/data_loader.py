"""
Data loader module for the Security Incident Analysis application.
Handles loading and processing data from various sources.
"""

import json
import pandas as pd
import streamlit as st
from src.rag_system import create_vector_db, initialize_rag_system, load_vector_db
from src.conversation import setup_conversation_chain

def load_sample_data():
    """Load sample security incident data"""
    
    sample_incidents = [
        """
        Incident ID: INC-2023-001
        Date: 2023-06-12
        Type: Phishing Attack
        Description: Multiple employees received sophisticated phishing emails claiming to be from IT department requesting password resets.
        Impact: Two employees clicked on malicious links and entered credentials. Access to email accounts compromised.
        Mitigation: Performed password resets, enabled MFA for all accounts, and conducted additional security awareness training.
        """,
        
        """
        Incident ID: INC-2023-002
        Date: 2023-07-25
        Type: DDoS Attack
        Description: Company website experienced a distributed denial-of-service attack lasting approximately 4 hours.
        Impact: Website unavailable during attack period, resulting in estimated loss of $25,000 in online sales.
        Mitigation: Implemented rate limiting, enhanced cloud-based DDoS protection, and improved monitoring systems.
        """,
        
        """
        Incident ID: INC-2023-003
        Date: 2023-08-10
        Type: Ransomware
        Description: Accounting department infected with ransomware through a malicious email attachment.
        Impact: Encryption of financial files and temporary disruption of accounting operations.
        Mitigation: Restored from backups, isolated affected systems, updated antivirus definitions, and improved email filtering.
        """,
        
        """
        Incident ID: INC-2023-004
        Date: 2023-09-05
        Type: Data Breach
        Description: Unauthorized access to customer database detected through unusual query patterns.
        Impact: Potential exposure of customer names, email addresses, and hashed passwords.
        Mitigation: Patched vulnerability, reset all user passwords, implemented additional encryption, and notified affected customers.
        """,
        
        """
        Incident ID: INC-2023-005
        Date: 2023-10-18
        Type: Insider Threat
        Description: Employee discovered copying sensitive company data to personal storage.
        Impact: Potential intellectual property theft and violation of data protection policies.
        Mitigation: Terminated employee access, conducted forensic investigation, implemented DLP solution, and enhanced access controls.
        """,
        
        """
        Incident ID: INC-2023-006
        Date: 2023-11-02
        Type: SQL Injection
        Description: Web application vulnerability exploited to inject malicious SQL queries.
        Impact: Unauthorized access to product database and potential data manipulation.
        Mitigation: Implemented parameterized queries, conducted security code review, and deployed WAF with updated rules.
        """
    ]
    
    return sample_incidents

def process_sample_data():
    """Process sample data and initialize the RAG system"""
    try:
        # Initialize RAG components
        embeddings, llm = initialize_rag_system()
        
        # Load sample data
        sample_incidents = load_sample_data()
        
        # Create vector database
        st.session_state.db = create_vector_db(embeddings, sample_incidents)
        
        # Set up conversation chain
        st.session_state.conversation_chain = setup_conversation_chain(llm, st.session_state.db)
        
        st.session_state.document_processed = True
        return True
    except Exception as e:
        st.error(f"Error initializing the system: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return False

def process_uploaded_file(uploaded_file):
    """Process uploaded file (JSON or CSV) and initialize the RAG system"""
    try:
        # Initialize RAG components
        embeddings, llm = initialize_rag_system()
        
        # Process uploaded file
        if uploaded_file.type == "application/json":
            data = json.loads(uploaded_file.read())
            incidents = [json.dumps(incident) for incident in data]
        else:  # CSV
            df = pd.read_csv(uploaded_file)
            incidents = df.apply(lambda row: row.to_json(), axis=1).tolist()
        
        # Create vector database
        st.session_state.db = create_vector_db(embeddings, incidents)
        
        # Set up conversation chain
        st.session_state.conversation_chain = setup_conversation_chain(llm, st.session_state.db)
        
        st.session_state.document_processed = True
        return True
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return False

def load_existing_index():
    """Load existing FAISS index and initialize the RAG system"""
    try:
        # Initialize RAG components
        embeddings, llm = initialize_rag_system()
        
        # Load existing FAISS index
        existing_db = load_vector_db(embeddings)
        
        if existing_db:
            st.session_state.db = existing_db
            
            # Set up conversation chain
            st.session_state.conversation_chain = setup_conversation_chain(llm, st.session_state.db)
            
            st.session_state.document_processed = True
            return True
        else:
            st.error("No existing FAISS index found.")
            return False
    except Exception as e:
        st.error(f"Error loading index: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return False
