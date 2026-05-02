import logging
from src.ingestion import DataIngestion
from src.retriever import DSARetriever
from src.validator import ResponseValidator
from src.logger import QueryLogger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DSAPipeline:
    def __init__(self):
        # Initialize components
        self.ingestion = DataIngestion()
        self.validator = ResponseValidator()
        self.query_logger = QueryLogger()
        self.retriever = None
        self.vectorstore = None

    def initialize_system(self, force_reingest=False):
        """Initializes the vector store and retriever, optionally forcing re-ingestion."""
        existing_vectorstore = None if force_reingest else self.ingestion.get_vector_store()
        if force_reingest:
            logger.info("Force re-ingest enabled. Resetting persisted vector store.")
            self.ingestion.reset_vector_store()

        if force_reingest or existing_vectorstore is None:
            logger.info("Building vector store from documents...")
            self.vectorstore = self.ingestion.ingest_all()
            # If we still can't build/load, clear persisted state once and retry.
            if self.vectorstore is None:
                logger.warning("Vector store unavailable. Resetting persisted Chroma data and retrying ingestion.")
                self.ingestion.reset_vector_store()
                self.vectorstore = self.ingestion.ingest_all()
        else:
            logger.info("Loading existing vector store...")
            self.vectorstore = existing_vectorstore

        if self.vectorstore:
            self.retriever = DSARetriever(self.vectorstore)
            logger.info("System initialization complete.")
            return True
        else:
            logger.warning("Failed to initialize vector store. Add documents to the 'data' directory.")
            return False

    def ask_question(self, query):
        """Main interface to ask a question and get a formatted, logged answer."""
        if not self.retriever:
            return {"error": "System not initialized or no documents found. Please add documents and initialize."}

        # 1. Get answer from RAG pipeline
        result = self.retriever.get_answer(query)
        answer = result.get("answer", "")
        
        # Format a short snippet of context for logging
        context_docs = result.get("context", [])
        context_snippet = "\n".join([doc.page_content for doc in context_docs[:2]]) if context_docs else ""
        context_snippet = context_snippet[:500] + "..." if len(context_snippet) > 500 else context_snippet
        
        # 2. Validate response code if present
        validation = self.validator.validate_response(answer)
        validation_status = ""
        if validation["has_code"]:
            for res in validation["validation_results"]:
                if res["language"] == "python":
                    validation_status += f"[Python Valid: {res['is_valid']}] "
        
        # 3. Log query and results
        self.query_logger.log_query(
            query=query,
            response=answer,
            context_snippet=context_snippet,
            validation_status=validation_status.strip()
        )
        
        return {
            "query": query,
            "answer": answer,
            "context": result.get("context", []),
            "validation": validation
        }
