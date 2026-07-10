import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.pipeline import DSAPipeline

# Load environment variables
load_dotenv()

# App configuration
st.set_page_config(
    page_title="Automated RAG-Based Document Q&A System",
    page_icon="",
    layout="wide",
)

# Initialize Session State
if "pipeline" not in st.session_state:
    st.session_state.pipeline = DSAPipeline()
    if os.path.exists("data") and os.listdir("data"):
        st.session_state.pipeline.initialize_system()
if "messages" not in st.session_state:
    st.session_state.messages = []

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Main Application
st.title("Document Q&A Assistant")
st.markdown("Ask questions based on your uploaded documents.")

# Sidebar for controls
with st.sidebar:
    st.header("1. Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload PDF or Text files",
        type=["pdf", "txt"],
        accept_multiple_files=True,
    )

    if st.button("Ingest Data"):
        if not uploaded_files:
            st.warning("Please upload files first.")
        else:
            with st.spinner("Processing documents..."):
                for uploaded_file in uploaded_files:
                    file_path = os.path.join("data", uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                # Re-initialize the pipeline forcing ingestion
                success = st.session_state.pipeline.initialize_system(force_reingest=True)
                if success:
                    st.success("Documents successfully ingested!")
                else:
                    st.error("Failed to ingest documents.")

    st.header("2. Check API Key")
    if not os.getenv("OPENROUTER_API_KEY") or "your_openrouter_api_key_here" in os.getenv("OPENROUTER_API_KEY"):
        st.error("Please add a valid OPENROUTER_API_KEY to your .env file or environment.")

    st.header("3. Query Analytics")
    if st.button("Show Logs"):
        logs = st.session_state.pipeline.query_logger.get_all_logs()
        if logs:
            df = pd.DataFrame(logs, columns=["ID", "Timestamp", "Query", "Response", "Context Snippet"])
            st.dataframe(df.drop(columns=["Response"]))
        else:
            st.info("No queries logged yet.")

# Chat Interface
if st.session_state.pipeline.retriever is None:
    st.info("Please upload and ingest documents from the sidebar to start asking questions.")
else:
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Ask a question from your uploaded documents..."):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = st.session_state.pipeline.ask_question(prompt)

            if "error" in result:
                st.error(result["error"])
                response = result["error"]
            else:
                response = result["answer"]
                st.markdown(response)

                # Show source documents used
                with st.expander("Show Sources"):
                    shown = set()
                    source_no = 1
                    for doc in result.get("context", []):
                        source_name = doc.metadata.get("source", "Unknown")
                        snippet = doc.page_content[:200].strip()
                        signature = (source_name, snippet)
                        if signature in shown:
                            continue
                        shown.add(signature)
                        st.markdown(f"**Source {source_no}:** {source_name}")
                        st.caption(f"{snippet}...")
                        source_no += 1
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

