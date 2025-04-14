import streamlit as st
import os
import warnings
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.globals import set_llm_cache, get_llm_cache
import pandas as pd
import datetime
import uuid
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Security Incident Analysis Assistant",
    page_icon="🔐",
    layout="wide",
)

# Initialize session state
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

def initialize_rag_system():
    """Initialize the RAG system with Google Generative AI embeddings and ChatGoogleGenerativeAI"""

    # Use environment variable for API key
    api_key = os.environ.get("GOOGLE_API_KEY")

    if not api_key:
        st.error("Google API key not found. Please set the GOOGLE_API_KEY environment variable.")
        # Add debug info to help troubleshoot
        st.error(f"Available environment variables: {[k for k in os.environ.keys() if not k.startswith('_')]}")
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
            db = FAISS.load_local("faiss_index", embeddings)
            return db
    except Exception as e:
        st.warning(f"Could not load existing index: {str(e)}")

    return None

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
            import traceback
            st.error(traceback.format_exc())
            return f"An error occurred: {str(e)}"
    else:
        return "Please upload security incident data first to initialize the system."

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

def save_incident_report(incident_data):
    """Save a new incident report to the database"""

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
    existing_db = load_vector_db(embeddings)

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

# Main application UI
def main():
    st.title("🔐 Security Incident Analysis Assistant")

    # Add API key input in the sidebar
    with st.sidebar:
        st.header("Configuration")

        # Display LangChain version
        try:
            import langchain
            st.info(f"LangChain version: {langchain.__version__}")
            # Suppress UserWarning about llm_cache
            warnings.filterwarnings("ignore", message="Importing llm_cache from langchain root module is no longer supported")
        except Exception:
            st.warning("Could not detect LangChain version")

        # Option to manually input API key
        manual_api_key = st.text_input("Google API Key (optional)", type="password")
        if manual_api_key:
            os.environ["GOOGLE_API_KEY"] = manual_api_key
            st.success("API key set!")

        # Display current API key status
        if os.environ.get("GOOGLE_API_KEY"):
            st.success("Google API Key is configured")
        else:
            st.warning("Google API Key not found. Please enter it above or check your .env file")

        # Data source options
        st.subheader("Data Source")
        data_option = st.radio(
            "Choose data source:",
            ("Sample Data", "Upload Own Data", "Add New Incident", "Load Existing Index")
        )

        if data_option == "Sample Data":
            if st.button("Load Sample Data"):
                if not os.environ.get("GOOGLE_API_KEY"):
                    st.error("Google API key not found. Please set it manually or check your .env file.")
                else:
                    with st.spinner("Loading sample data and initializing the system..."):
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
                            st.success("Sample data loaded successfully!")
                        except Exception as e:
                            st.error(f"Error initializing the system: {str(e)}")
                            import traceback
                            st.error(traceback.format_exc())

        elif data_option == "Upload Own Data":
            uploaded_file = st.file_uploader("Upload security incidents JSON or CSV", type=["json", "csv"])

            if uploaded_file is not None:
                if st.button("Process Uploaded Data"):
                    if not os.environ.get("GOOGLE_API_KEY"):
                        st.error("Google API key not found. Please set it manually or check your .env file.")
                    else:
                        with st.spinner("Processing uploaded data..."):
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
                                st.success("Data processed successfully!")
                            except Exception as e:
                                st.error(f"Error processing data: {str(e)}")
                                import traceback
                                st.error(traceback.format_exc())

        elif data_option == "Add New Incident":
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
                if not os.environ.get("GOOGLE_API_KEY"):
                    st.error("Google API key not found. Please set it manually or check your .env file.")
                elif incident_description and incident_impact and incident_mitigation:
                    try:
                        # Collect incident data
                        incident_data = {
                            "date": incident_date.strftime("%Y-%m-%d"),
                            "type": incident_type,
                            "description": incident_description,
                            "impact": incident_impact,
                            "mitigation": incident_mitigation
                        }

                        # Save the incident
                        incident_id = save_incident_report(incident_data)

                        # Initialize RAG components if not already done
                        if not st.session_state.conversation_chain:
                            embeddings, llm = initialize_rag_system()
                            st.session_state.conversation_chain = setup_conversation_chain(llm, st.session_state.db)

                        st.session_state.document_processed = True
                        st.success(f"Incident {incident_id} added successfully!")
                    except Exception as e:
                        st.error(f"Error adding incident: {str(e)}")
                        import traceback
                        st.error(traceback.format_exc())
                else:
                    st.error("Please fill in all fields.")

        elif data_option == "Load Existing Index":
            if st.button("Load Existing FAISS Index"):
                if not os.environ.get("GOOGLE_API_KEY"):
                    st.error("Google API key not found. Please set it manually or check your .env file.")
                else:
                    with st.spinner("Loading existing FAISS index..."):
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
                                st.success("Existing index loaded successfully!")
                            else:
                                st.error("No existing FAISS index found.")
                        except Exception as e:
                            st.error(f"Error loading index: {str(e)}")
                            import traceback
                            st.error(traceback.format_exc())

        # Advanced options
        st.subheader("Advanced Options")
        if st.button("Reset Chat History"):
            st.session_state.conversation_history = []
            st.session_state.chat_history = []
            st.success("Chat history cleared")

    # Main chat interface
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
            if not os.environ.get("GOOGLE_API_KEY"):
                st.error("Google API key not found. Please set it manually or check your .env file.")
            elif st.session_state.document_processed:
                with st.spinner("Analyzing..."):
                    try:
                        # Process the query and update the UI
                        response = process_user_query(user_query)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error processing query: {str(e)}")
                        import traceback
                        st.error(traceback.format_exc())
            else:
                st.error("Please initialize the system with security incident data first.")

    # Display system status
    st.sidebar.subheader("System Status")
    status = "Ready" if st.session_state.document_processed else "Not Initialized"
    st.sidebar.write(f"Status: {status}")
    st.sidebar.write(f"Chat history entries: {len(st.session_state.chat_history)}")

    # Debug section
    if st.sidebar.checkbox("Show Debug Info"):
        st.sidebar.subheader("Debug Information")
        st.sidebar.write(f"Database initialized: {st.session_state.db is not None}")
        st.sidebar.write(f"Conversation chain initialized: {st.session_state.conversation_chain is not None}")

if __name__ == "__main__":
    main()
