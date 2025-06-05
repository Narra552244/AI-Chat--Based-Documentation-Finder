import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
from utils.document_processor import DocumentProcessor
from utils.vector_store import VectorStore
from utils.llm_handler import LLMHandler
from utils.db_handler import DBHandler

# Load environment variables
load_dotenv()

# Verify OpenAI API key is set
if not os.getenv("OPENAI_API_KEY"):
    st.error("OpenAI API key not found. Please set it in the .env file.")
    st.stop()

# Initialize components
@st.cache_resource
def init_components():
    return {
        'doc_processor': DocumentProcessor(),
        'vector_store': VectorStore(),
        'llm_handler': LLMHandler(),
        'db_handler': DBHandler()
    }

# Page config
st.set_page_config(
    page_title="AI Documentation Assistant",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Initialize components
components = init_components()

# Sidebar
with st.sidebar:
    st.title("📚 Doc Assistant")
    
    # File upload
    st.header("Upload Documents")
    uploaded_file = st.file_uploader(
        "Upload PDF or Text files",
        type=['pdf', 'txt'],
        key="file_uploader"
    )
    
    if uploaded_file:
        try:
            # Save file temporarily
            file_type = uploaded_file.type.split('/')[-1]
            temp_path = f"data/documents/{uploaded_file.name}"
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            # Process document
            doc_data = components['doc_processor'].process_document(temp_path, file_type)
            
            # Add to vector store
            components['vector_store'].add_document(doc_data)
            
            # Log to database
            components['db_handler'].log_document(
                uploaded_file.name,
                file_type,
                doc_data['metadata']
            )
            
            st.success(f"Successfully processed {uploaded_file.name}")
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    
    # Stats
    st.header("Statistics")
    stats = components['db_handler'].get_query_stats()
    st.metric("Total Documents", stats['total_documents'])
    st.metric("Total Queries", stats['total_queries'])
    st.metric("Queries (24h)", stats['queries_last_24h'])

# Main chat interface
st.title("💬 Chat with your Documentation")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about your documentation"):
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    try:
        # Get query embedding
        query_embedding = components['llm_handler'].get_embedding(prompt)
        
        # Search for relevant context
        context = components['vector_store'].search(query_embedding)
        
        # Get LLM response
        response = components['llm_handler'].get_response(prompt, context)
        
        # Log query
        components['db_handler'].log_query(prompt, response, context)
        
        # Add assistant message to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Display assistant message
        with st.chat_message("assistant"):
            st.write(response)
            
    except Exception as e:
        st.error(f"Error processing query: {str(e)}")

# Admin view
if st.sidebar.checkbox("Show Admin View"):
    st.sidebar.header("Admin Tools")
    
    # Document history
    st.sidebar.subheader("Document History")
    docs = components['db_handler'].get_document_history()
    for doc in docs:
        st.sidebar.text(f"{doc['filename']} ({doc['upload_timestamp']})")
    
    # Query analysis
    if st.sidebar.button("Analyze Queries"):
        queries = components['db_handler'].get_query_history()
        analysis = components['llm_handler'].analyze_query_log(queries)
        st.sidebar.text_area("Query Analysis", analysis, height=300) 