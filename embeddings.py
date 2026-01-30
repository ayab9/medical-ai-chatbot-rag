"""
embeddings_medical.py
ChromaDB – Embeddings RAG médical
Compatible nouveaux chunks JSON (WHO / NCI)
"""

import json
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# =========================
# CONFIG
# =========================
class Config:
    CHUNKS_JSON_PATH = "chunks.json"

    PERSIST_DIRECTORY = "chroma_db_free"
    COLLECTION_NAME = "breast_cancer_docs"

    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    DEVICE = "cpu"
    BATCH_SIZE = 64

    VERSION = "3.0-medical-json"
    CREATED_DATE = datetime.now().isoformat()

    EXCLUDED_SECTIONS = [
        "DOCUMENT TITLE",
        "DOCUMENT SCOPE"
    ]

# =========================
# LOAD CHUNKS FROM JSON
# =========================
def load_chunks_from_json(path: str) -> List[Document]:
    with open(path, "r", encoding="utf-8") as f:
        raw_chunks = json.load(f)

    documents = []

    for item in raw_chunks:
        section = item["metadata"].get("section", "").upper()

        # filtrage des sections non informatives
        if any(x in section for x in Config.EXCLUDED_SECTIONS):
            continue

        documents.append(
            Document(
                page_content=item["content"],
                metadata={
                    "chunk_id": item["chunk_id"],
                    "document_id": item["metadata"].get("document_id"),
                    "source": item["metadata"].get("source"),
                    "section": item["metadata"].get("section"),
                    "domain": item["metadata"].get("domain"),
                    "language": item["metadata"].get("language"),
                }
            )
        )

    return documents

# =========================
# EMBEDDINGS
# =========================
def create_embeddings_model():
    return HuggingFaceEmbeddings(
        model_name=Config.EMBEDDING_MODEL,
        model_kwargs={"device": Config.DEVICE},
        encode_kwargs={
            "normalize_embeddings": True,
            "batch_size": Config.BATCH_SIZE
        }
    )

# =========================
# VECTOR STORE
# =========================
def create_vector_store(chunks: List[Document]) -> Optional[Chroma]:
    if not chunks:
        print("❌ Aucun chunk à indexer")
        return None

    persist_path = Path(Config.PERSIST_DIRECTORY)
    if persist_path.exists():
        shutil.rmtree(persist_path)

    embeddings = create_embeddings_model()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=Config.PERSIST_DIRECTORY,
        collection_name=Config.COLLECTION_NAME,
        collection_metadata={
            "hnsw:space": "cosine",
            "version": Config.VERSION,
            "created_at": Config.CREATED_DATE
        }
    )

    print(f"✅ {vectorstore._collection.count()} chunks indexés")
    return vectorstore

# =========================
# MAIN
# =========================
def main():
    print("📥 Chargement des chunks JSON...")
    chunks = load_chunks_from_json(Config.CHUNKS_JSON_PATH)
    print(f"📊 Chunks valides: {len(chunks)}")

    print("🧠 Création de la base vectorielle Chroma...")
    vectorstore = create_vector_store(chunks)

    if not vectorstore:
        print("❌ Échec création base")
        return

    print("🚀 Base ChromaDB prête pour RAG + Groq")

if __name__ == "__main__":
    main()
