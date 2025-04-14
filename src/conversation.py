"""
Conversation module for the Security Incident Analysis application.
Handles conversation chains and query processing.
"""

import streamlit as st
import traceback
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

def setup_conversation_chain(llm, db):
    """Set up the conversational retrieval chain"""
    
    # Create memory
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    # Define the prompt template
    template = """
    You are a Security Incident Analysis Assistant specialized in helping security teams analyze incidents.
    Use the following context and conversation history to provide detailed insights about security incidents.
    
    Context: {context}
    
    Chat History: {chat_history}
    
    Question: {question}
    
    Provide a comprehensive analysis of the security incident, including:
    1. Potential threats involved
    2. Recommended mitigation strategies
    3. Similar incidents from the knowledge base
    4. Severity assessment
    
    Your analysis should be professional, detailed, and actionable.
    """
    
    custom_prompt = PromptTemplate(
        input_variables=["context", "chat_history", "question"],
        template=template
    )
    
    # Create ConversationalRetrievalChain
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=db.as_retriever(search_kwargs={"k": 5}),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": custom_prompt},
        return_source_documents=False  # Disable returning source documents to avoid UUID issues
    )
    
    return conversation_chain

def process_user_query(user_query):
    """Process user query through the conversational chain"""
    
    if st.session_state.conversation_chain:
        try:
            # Convert UUID objects to strings in the chat history
            safe_chat_history = []
            for msg_pair in st.session_state.chat_history:
                # Make sure we're storing tuples of strings
                safe_msg_pair = (str(msg_pair[0]), str(msg_pair[1]))
                safe_chat_history.append(safe_msg_pair)
                
            # Process the query
            response = st.session_state.conversation_chain({"question": user_query})
            
            # Store the response
            response_text = response.get('answer', 'No answer provided')
            st.session_state.chat_history.append((user_query, response_text))
            st.session_state.conversation_history.append({"role": "user", "content": user_query})
            st.session_state.conversation_history.append({"role": "assistant", "content": response_text})
            
            return response_text
        except Exception as e:
            st.error(f"Error in processing query: {str(e)}")
            st.error("Debug info: Chat history length: " + str(len(st.session_state.chat_history)))
            st.error(traceback.format_exc())
            return f"An error occurred: {str(e)}"
    else:
        return "Please upload security incident data first to initialize the system."
