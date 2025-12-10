"""
RAG Vector Store Module
=======================
Handles document loading, chunking, embedding, and retrieval.
"""

import hashlib
import json
import platform
from pathlib import Path
from typing import List, Optional

from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

from app.config import (
    UNSTRUCTURED_DOCS,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOP_K_RESULTS,
    CHROMA_PERSIST_DIR,
    OPENAI_API_KEY,
    EMBEDDING_MODEL,
)

IS_WINDOWS = platform.system() == "Windows"


class RAGVectorStore:
    """Manages the vector store for RAG-based retrieval."""

    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            api_key=OPENAI_API_KEY,
            model=EMBEDDING_MODEL,
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
        )
        self.vector_store: Optional[Chroma] = None
        self._docs_hash_file = CHROMA_PERSIST_DIR / "docs_hash.json"

    def _get_loader(self, file_path: Path):
        """Get appropriate loader based on file extension."""
        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            return PyPDFLoader(str(file_path))
        else:
            # Use TextLoader for .md, .txt, and other text files
            # TextLoader handles markdown files perfectly fine for RAG
            return TextLoader(str(file_path), encoding='utf-8')

    def _compute_docs_hash(self) -> str:
        """Compute hash of all document contents to detect changes."""
        hasher = hashlib.md5()
        for doc_path in sorted(UNSTRUCTURED_DOCS):
            if doc_path.exists():
                hasher.update(doc_path.read_bytes())
                hasher.update(str(doc_path.stat().st_mtime).encode())
        return hasher.hexdigest()

    def _should_rebuild_index(self) -> bool:
        """Check if index needs rebuilding based on document changes."""
        if not CHROMA_PERSIST_DIR.exists():
            return True
        if not self._docs_hash_file.exists():
            return True

        current_hash = self._compute_docs_hash()
        try:
            stored_hash = json.loads(self._docs_hash_file.read_text()).get("hash")
            return current_hash != stored_hash
        except (json.JSONDecodeError, KeyError):
            return True

    def _save_docs_hash(self):
        """Save current documents hash."""
        CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
        self._docs_hash_file.write_text(
            json.dumps({"hash": self._compute_docs_hash()})
        )

    def load_documents(self) -> List[Document]:
        """Load all configured documents."""
        all_docs = []

        for doc_path in UNSTRUCTURED_DOCS:
            if not doc_path.exists():
                print(f"Warning: Document not found: {doc_path}")
                continue

            try:
                loader = self._get_loader(doc_path)
                docs = loader.load()

                for doc in docs:
                    doc.metadata["source_file"] = doc_path.name

                all_docs.extend(docs)
                print(f"Loaded: {doc_path.name} ({len(docs)} documents)")

            except Exception as e:
                print(f"Error loading {doc_path}: {e}")

        return all_docs

    def initialize(self, force_rebuild: bool = False) -> None:
        """Initialize or load the vector store."""
        CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
        persist_dir_str = str(CHROMA_PERSIST_DIR.resolve())

        if not force_rebuild and not self._should_rebuild_index():
            print("Loading existing vector store...")
            self.vector_store = Chroma(
                persist_directory=persist_dir_str,
                embedding_function=self.embeddings,
                collection_name="company_docs",
            )
            print(f"Loaded vector store with {self.vector_store._collection.count()} chunks")
            return

        print("Building vector store from documents...")

        documents = self.load_documents()
        if not documents:
            raise ValueError("No documents loaded. Check UNSTRUCTURED_DOCS paths.")

        chunks = self.text_splitter.split_documents(documents)
        print(f"Created {len(chunks)} chunks from {len(documents)} documents")

        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=persist_dir_str,
            collection_name="company_docs",
        )

        self._save_docs_hash()
        print("Vector store built and persisted successfully")

    def search(self, query: str, k: int = TOP_K_RESULTS) -> List[Document]:
        """Search for relevant documents."""
        if not self.vector_store:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        return self.vector_store.similarity_search(query, k=k)

    def search_with_scores(self, query: str, k: int = TOP_K_RESULTS) -> List[tuple]:
        """Search for relevant documents with similarity scores."""
        if not self.vector_store:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        return self.vector_store.similarity_search_with_score(query, k=k)

    def get_retriever(self):
        """Get a retriever interface for the vector store."""
        if not self.vector_store:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        return self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": TOP_K_RESULTS},
        )


# Singleton instance
_vector_store: Optional[RAGVectorStore] = None


def get_vector_store() -> RAGVectorStore:
    """Get or create the vector store singleton."""
    global _vector_store
    if _vector_store is None:
        _vector_store = RAGVectorStore()
        _vector_store.initialize()
    return _vector_store


def search_knowledge_base(query: str) -> str:
    """
    Search the company knowledge base for relevant information.
    This function is designed to be used as a tool by the agent.
    """
    vs = get_vector_store()
    results = vs.search_with_scores(query)

    if not results:
        return "No relevant information found in the knowledge base."

    formatted_results = []
    for doc, score in results:
        source = doc.metadata.get("source_file", "Unknown")
        relevance = "High" if score < 0.5 else "Medium" if score < 1.0 else "Low"
        formatted_results.append(
            f"[Source: {source} | Relevance: {relevance}]\n{doc.page_content}"
        )

    return "\n\n---\n\n".join(formatted_results)
