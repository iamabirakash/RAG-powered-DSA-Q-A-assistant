from langchain_openai import ChatOpenAI
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import PromptTemplate
import os
import logging

logger = logging.getLogger(__name__)

class DSARetriever:
    def __init__(self, vectorstore, model_name="google/gemini-2.5-flash", temperature=0.1):
        if not vectorstore:
            raise ValueError("Vectorstore must be provided")
            
        self.vectorstore = vectorstore
        self.retriever = self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 5, "fetch_k": 20, "lambda_mult": 0.5}
        )
        self.llm = ChatOpenAI(
            model=model_name, 
            temperature=temperature,
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            max_tokens=1500
        )
        self.qa_chain = self._setup_chain()

    def _setup_chain(self):
        """Sets up retrieval and answer generation with strict context grounding."""
        template = """You are a document-grounded Q&A assistant.
Answer the user's question using only the retrieved context below.
Do not use outside knowledge.
If the answer is not explicitly present in the context, respond exactly with:
"I could not find this in the provided documents."
When relevant, cite key details from the context clearly and concisely.

Context:
{context}

Question: {input}

Answer:"""
        prompt = PromptTemplate.from_template(template)

        question_answer_chain = create_stuff_documents_chain(self.llm, prompt)
        retrieval_chain = create_retrieval_chain(self.retriever, question_answer_chain)
        return retrieval_chain

    def get_answer(self, query: str):
        """Runs the query through the retrieval chain and returns the result."""
        try:
            response = self.qa_chain.invoke({"input": query})
            return {
                "answer": response["answer"],
                "context": response["context"]
            }
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {"answer": f"Error generating answer: {e}", "context": []}
