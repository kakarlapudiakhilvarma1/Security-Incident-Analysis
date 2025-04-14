"""
RAG (Retrieval Augmented Generation) system module.
Handles embeddings, vector database, and language model initialization.
"""

import os
import streamlit as st
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.globals import set_llm_cache, get_llm_cache
from src.config import check_api_key

def initialize_rag_system():
    """Initialize the RAG system with Google Generative AI embeddings and ChatGoogleGenerativeAI"""
    
    # Check if API key is available
    if not check_api_key():
        st.stop()
    
    # Create embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Initialize the language model
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0.2,
        max_output_tokens=2048,
        top_p=0.95,
        top_k=40,
        verbose=True
    )
    
    return embeddings, llm

def create_vector_db(embeddings, security_incidents):
    """Create a vector database from security incidents data using FAISS"""
    
    # Create a vector store using FAISS
    db = FAISS.from_texts(security_incidents, embeddings)
    
    # Save the FAISS index to a file
    db.save_local("faiss_index")
    
    return db

def load_vector_db(embeddings):
    """Load the FAISS vector database from file if it exists"""
    
    try:
        # Try to load existing FAISS index
        if os.path.exists("faiss_index"):
            db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
            return db
    except Exception as e:
        st.warning(f"Could not load existing index: {str(e)}")
    
    return None
