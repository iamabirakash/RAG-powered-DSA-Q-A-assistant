# RAG-Powered Document Q&A Assistant

A Streamlit-based RAG (Retrieval-Augmented Generation) assistant that answers questions from your uploaded documents, shows retrieval sources, validates Python code snippets in responses, and logs query analytics.

## Overview
This project lets you upload `.pdf` and `.txt` files, builds embeddings locally, stores them in a persistent Chroma vector database, and uses an OpenRouter-hosted LLM to generate context-grounded answers.

The app is now document-domain agnostic (not DSA-only). It is designed to answer from the uploaded context and avoid unsupported hallucinated answers.

## Features
- Upload and ingest `.pdf` and `.txt` documents from the Streamlit UI.
- Chunk documents and create embeddings with `sentence-transformers/all-MiniLM-L6-v2`.
- Persist vector index to local ChromaDB (`chroma_db/`).
- Retrieve relevant chunks using MMR for better diversity and fewer duplicate sources.
- Generate answers with OpenRouter via LangChain `ChatOpenAI` client.
- Strict context-grounded response behavior when information is missing.
- Validate Python code blocks in responses using AST parsing.
- Store query analytics in SQLite (`data/analytics.db`).
- Display deduplicated source snippets in the UI.

## Tech Stack
- Python
- Streamlit
- LangChain (`langchain`, `langchain-classic`, `langchain-openai`, `langchain-chroma`, `langchain-huggingface`)
- ChromaDB
- Sentence Transformers (Hugging Face)
- OpenRouter API
- SQLite

## Project Structure
```text
LeetCode Automation/
|-- app.py
|-- src/
|   |-- ingestion.py
|   |-- pipeline.py
|   |-- retriever.py
|   |-- validator.py
|   `-- logger.py
|-- data/
|   |-- .gitkeep
|   `-- analytics.db                (runtime-generated)
|-- chroma_db/                      (runtime-generated vector store)
|-- requirements.txt
|-- .env                            (local secrets, not committed)
`-- .gitignore
```

## End-to-End Pipeline
### 1. App startup
- `app.py` initializes `DSAPipeline` inside Streamlit session state.
- If `data/` already contains files, the app attempts to initialize retrieval automatically.

### 2. Ingestion
Implemented in `src/ingestion.py`:
- `load_documents()` reads `.pdf` and `.txt` files from `data/`.
- `split_documents()` chunks text (`chunk_size=1000`, `chunk_overlap=200`).
- `create_vector_store()` writes embeddings into Chroma persisted at `chroma_db/`.

### 3. Vector store lifecycle
Implemented across `src/ingestion.py` and `src/pipeline.py`:
- `get_vector_store()` attempts to load existing persisted Chroma index.
- `reset_vector_store()` can clear/recreate `chroma_db/`.
- On `force_reingest=True`, pipeline resets and rebuilds to avoid stale vectors.

### 4. Retrieval + answer generation
Implemented in `src/retriever.py`:
- Builds retriever with MMR (`k=5`, `fetch_k=20`, `lambda_mult=0.5`).
- Uses OpenRouter model via `ChatOpenAI` with `base_url=https://openrouter.ai/api/v1`.
- Uses a strict prompt instructing context-only answers.

### 5. Post-processing
Implemented in `src/pipeline.py`, `src/validator.py`, `src/logger.py`:
- `ask_question()` gets answer + context.
- Python fenced code blocks are syntax-checked with `ast.parse`.
- Query, response, context snippet, and validation status are logged to SQLite.

### 6. UI rendering
In `app.py`:
- Shows chat response.
- Shows deduplicated source snippets in **Show Sources**.
- Shows Python syntax validation in **Code Validation Status**.
- Shows query logs in sidebar **Show Logs**.

## Setup
## 1) Clone and open project
```bash
git clone https://github.com/iamabirakash/RAG-powered-DSA-Q-A-assistant.git
cd RAG-powered-DSA-Q-A-assistant
```

## 2) Create virtual environment
### Windows (PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Windows (cmd)
```bat
python -m venv venv
venv\Scripts\activate
```

## 3) Install dependencies
```bash
pip install -r requirements.txt
```

## 4) Configure environment variables
Create `.env` in project root:
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Optional (to reduce Hugging Face unauthenticated warnings/rate limits):
```env
HF_TOKEN=your_huggingface_token_here
```

## 5) Run the app
```bash
streamlit run app.py
```

## Usage
1. Open the Streamlit app URL.
2. Upload one or more `.pdf` / `.txt` files from the sidebar.
3. Click **Ingest Data**.
4. Ask questions in chat.
5. Expand **Show Sources** to inspect retrieved context.
6. Expand **Code Validation Status** when Python code appears.
7. Use **Show Logs** to review analytics.

## Data Persistence
- `chroma_db/`: persistent vector index.
- `data/analytics.db`: query analytics table.
- `data/`: uploaded source documents.

## Offline Behavior
- Works offline for: local UI, document loading/chunking, embeddings, vector retrieval.
- Requires internet for: final LLM answer generation via OpenRouter.

## Troubleshooting
### 1) `Could not connect to tenant default_tenant`
Cause: stale/corrupted Chroma persisted state.
Fix: click **Ingest Data** again (force re-ingest path resets and rebuilds index automatically).

### 2) Answers look unrelated to current files
Cause: old files still present in `data/` or stale vector index.
Fix:
- Keep only desired files in `data/`.
- Click **Ingest Data** to force a clean rebuild.

### 3) Hugging Face warnings about unauthenticated requests
Cause: model download requests without `HF_TOKEN`.
Fix: optional `HF_TOKEN` in `.env`.

### 4) `OPENROUTER_API_KEY` errors
Cause: missing/invalid API key.
Fix: update `.env`, restart app.

## Security and Git Hygiene
Do not commit:
- `.env`
- `venv/`
- `chroma_db/`
- `data/analytics.db`
- large private source documents

Use `.gitignore` to keep runtime/generated files out of Git.

## Suggested Improvements
- Add unit tests for ingestion, retrieval, and validator modules.
- Add source citations with page numbers/chunk scores.
- Add model selector and temperature controls in UI.
- Add document management UI (remove selected docs + reindex).
- Add optional local LLM backend (Ollama) for full offline Q&A.

## License
Add your preferred license (MIT is common for open source projects).
