import os
import shutil
from glob import glob
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

import logging
logger = logging.getLogger(__name__)

class DataIngestion:
    def __init__(self, data_dir="data", persist_dir="chroma_db"):
        self.data_dir = data_dir
        self.persist_dir = persist_dir
        # Using a fast, free local sentence-transformer model
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
    def load_documents(self):
        """Loads PDF and Text documents from the data directory."""
        documents = []
        
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        pdf_files = glob(os.path.join(self.data_dir, "*.pdf"))
        txt_files = glob(os.path.join(self.data_dir, "*.txt"))
        
        for file in pdf_files:
            try:
                loader = PyPDFLoader(file)
                documents.extend(loader.load())
            except Exception as e:
                logger.error(f"Error loading {file}: {e}")
                
        for file in txt_files:
            try:
                loader = TextLoader(file, encoding="utf-8")
                documents.extend(loader.load())
            except Exception as e:
                logger.error(f"Error loading {file}: {e}")
                
        return documents

    def split_documents(self, documents):
        """Splits documents into smaller chunks for vectorization."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )
        return text_splitter.split_documents(documents)

    def create_vector_store(self, chunks):
        """Creates or updates ChromaDB with document chunks."""
        if not chunks:
            return None
            
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_dir
        )
        return vectorstore

    def ingest_all(self):
        """Runs the whole pipeline and returns the vector store."""
        logger.info("Loading documents...")
        docs = self.load_documents()
        if not docs:
            logger.warning("No documents found in data directory.")
            return None
            
        logger.info(f"Loaded {len(docs)} documents. Splitting text...")
        chunks = self.split_documents(docs)
        
        logger.info(f"Created {len(chunks)} chunks. Building vector store...")
        vectorstore = self.create_vector_store(chunks)
        
        logger.info("Vector store building complete.")
        return vectorstore

    def reset_vector_store(self):
        """Deletes persisted vector store files to recover from corruption/version mismatches."""
        if os.path.exists(self.persist_dir):
            shutil.rmtree(self.persist_dir, ignore_errors=True)
        os.makedirs(self.persist_dir, exist_ok=True)

    def get_vector_store(self):
        """Returns the vector store if it already exists, otherwise None."""
        if os.path.exists(self.persist_dir) and os.listdir(self.persist_dir):
            try:
                return Chroma(
                    persist_directory=self.persist_dir,
                    embedding_function=self.embeddings
                )
            except Exception as e:
                logger.warning(f"Failed to load existing vector store: {e}")
                return None
        return None
