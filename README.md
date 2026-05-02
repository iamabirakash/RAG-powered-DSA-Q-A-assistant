# RAG-Powered DSA Q&A Assistant

A Streamlit-based RAG (Retrieval-Augmented Generation) assistant that answers Data Structures and Algorithms (DSA) questions from your own notes, validates generated Python code syntax, and logs query analytics.

## Suggested Repository Name
`rag-powered-dsa-qa-assistant`

## Suggested Short Description
`RAG-powered DSA Q&A assistant built with Streamlit, LangChain, ChromaDB, and OpenRouter; supports note ingestion, source-grounded answers, code syntax validation, and query analytics.`

## What This Project Does
- Upload DSA notes in `.pdf` and `.txt` format.
- Ingest and chunk documents for semantic retrieval.
- Build local embeddings (`all-MiniLM-L6-v2`) and persist vectors in ChromaDB.
- Retrieve relevant context and generate answers via OpenRouter LLM.
- Validate Python code blocks in responses for syntax correctness.
- Store query/response analytics in SQLite.

## Tech Stack
- Python
- Streamlit
- LangChain
- ChromaDB
- HuggingFace Embeddings
- OpenRouter (LLM API)
- SQLite

## Project Structure
```text
RAG-Powered DSA Q&A Assistant/
├── app.py                # Streamlit UI and chat interface
├── src/
│   ├── pipeline.py       # End-to-end orchestration
│   ├── ingestion.py      # File loading, chunking, embeddings, vector store
│   ├── retriever.py      # Retrieval + LLM chain
│   ├── validator.py      # Python code block syntax validation
│   └── logger.py         # Query analytics (SQLite)
├── data/                 # Uploaded notes + analytics.db
├── chroma_db/            # Persisted vector database
├── requirements.txt
└── .env
```

## Setup
### 1. Create and activate virtual environment
**Windows (cmd):**
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
Create `.env` in project root:
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

## Run the App
```bash
streamlit run app.py
```

## How to Use
1. Open the app in browser.
2. Upload DSA `.pdf`/`.txt` notes from the sidebar.
3. Click **Ingest Data**.
4. Ask questions in the chat input.
5. Inspect:
   - **Show Sources** (retrieved context)
   - **Code Validation Status** (for Python blocks)
   - **Show Logs** in sidebar (analytics)

## Data Persistence
- Vector store: `chroma_db/`
- Query logs DB: `data/analytics.db`
- Source files: `data/`

## Example Questions
- "Explain merge sort with time and space complexity."
- "Give Python code for BFS in a graph."
- "Difference between stack and queue with examples?"

## Notes
- If no notes are ingested, the assistant cannot answer context-grounded queries.
- Ensure your API key is valid before querying.

## Future Improvements
- Add unit/integration tests.
- Add multi-user chat history.
- Add model selection in UI.
- Add better citation formatting with chunk ranking scores.

## License
Add your preferred license (MIT recommended for open-source use).
