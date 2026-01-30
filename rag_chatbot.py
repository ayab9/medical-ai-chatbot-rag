"""
rag_chatbot_llm_final.py
CHATBOT RAG MEDICAL – FINAL VERSION (FIXED)
Supports: Simulation | Ollama | Groq
Domain: Breast Cancer
"""

import os
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document


# =========================
# CONFIGURATION
# =========================
class Config:
    PERSIST_DIRECTORY = "chroma_db_free"
    COLLECTION_NAME = "breast_cancer_docs"
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    DEFAULT_K = 3
    MAX_K = 8

    TEMPERATURE = 0.2
    MAX_TOKENS = 600
    MAX_CHARS_PER_DOC = 1200


# =========================
# LOAD VECTOR STORE
# =========================
def load_vector_store() -> Optional[Chroma]:
    if not Path(Config.PERSIST_DIRECTORY).exists():
        print("❌ Vector database not found. Run embeddings.py first.")
        return None

    print("📂 Loading vector database...")

    embeddings = HuggingFaceEmbeddings(
        model_name=Config.EMBEDDING_MODEL,
        encode_kwargs={"normalize_embeddings": True}
    )

    vectorstore = Chroma(
        persist_directory=Config.PERSIST_DIRECTORY,
        embedding_function=embeddings,
        collection_name=Config.COLLECTION_NAME
    )

    print(f"✅ Vector DB loaded ({vectorstore._collection.count()} chunks)")
    return vectorstore


# =========================
# MEDICAL PROMPT (STRICT)
# =========================
def create_medical_prompt() -> ChatPromptTemplate:
    system_prompt = """
You are a medical information assistant specialized in breast cancer.

STRICT RULES:
1. Use ONLY the information provided in the CONTEXT.
2. If the answer is NOT explicitly present, respond exactly:
   "This information is not available in my current medical document base."
3. Do NOT use prior knowledge.
4. Do NOT speculate.
5. Do NOT provide diagnosis or treatment advice.
6. This is an informational decision-support system only.
7. Structure answers clearly (bullet points or sections).
8. Maintain a professional, neutral, medical tone.
"""

    human_prompt = """
MEDICAL CONTEXT (verified sources):
{context}

QUESTION:
{question}

Medical answer:
"""

    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])


# =========================
# LLM INITIALIZATION
# =========================
def init_ollama_llm():
    try:
        from langchain_community.llms import Ollama

        print("🦙 Initializing Ollama LLM...")
        llm = Ollama(
            model="llama3.2:3b",
            temperature=Config.TEMPERATURE,
            num_predict=Config.MAX_TOKENS
        )

        llm.invoke("test")
        print("✅ Ollama ready")
        return llm

    except Exception as e:
        print(f"⚠️ Ollama unavailable: {e}")
        return None


def init_groq_llm():
    try:
        from langchain_groq import ChatGroq

        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            print("❌ GROQ_API_KEY missing")
            return None

        print("🚀 Initializing Groq LLM...")
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS,
            api_key=api_key
        )

        print("✅ Groq ready (Llama-3.3-70B)")
        return llm

    except Exception as e:
        print(f"⚠️ Groq unavailable: {e}")
        return None


# =========================
# RAG PIPELINE (FIXED)
# =========================
def rag_pipeline(
    vectorstore: Chroma,
    llm: Optional[object],
    question: str,
    k: int
) -> Tuple[str, List[str]]:

    # ✅ FIX: similarity instead of MMR
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )

    docs: List[Document] = retriever.invoke(question)

    if not docs:
        return (
            "This information is not available in my current medical document base.",
            []
        )

    context_parts = []
    sources = []

    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "Unknown")
        
        content = doc.page_content[:Config.MAX_CHARS_PER_DOC]

        context_parts.append(
             f"[Source {i+1}: {source}]\n{content}"
        )

        
        if source not in sources:
            sources.append(source)

    context = "\n\n---\n\n".join(context_parts)

    if llm is None:
        answer = "🔹 SIMULATION MODE 🔹\n\n"
        for doc in docs:
            answer += doc.page_content[:300] + "\n\n"
        return answer, sources

    prompt = create_medical_prompt()
    messages = prompt.format_messages(
        context=context,
        question=question
    )

    response = llm.invoke(messages)
    answer = response.content if hasattr(response, "content") else str(response)

    return answer, sources


# =========================
# CHAT INTERFACE
# =========================
def chat_interface(vectorstore: Chroma, llm: Optional[object]):
    print("\n" + "=" * 70)
    print("🤖 MEDICAL RAG CHATBOT – BREAST CANCER")
    print("=" * 70)
    print("Commands: /quit | /k N")
    print("=" * 70)

    k = Config.DEFAULT_K

    while True:
        user_input = input("\n❓ Question: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "/quit":
            print("👋 Session ended.")
            break

        if user_input.lower().startswith("/k"):
            try:
                k = int(user_input.split()[1])
                k = max(1, min(k, Config.MAX_K))
                print(f"🔧 Number of sources set to {k}")
            except:
                print("Usage: /k 3")
            continue

        answer, sources = rag_pipeline(
            vectorstore=vectorstore,
            llm=llm,
            question=user_input,
            k=k
        )

        print("\n" + "-" * 70)
        print("📌 ANSWER")
        print("-" * 70)
        print(answer)

        if sources:
            print("\n📚 SOURCES")
            for s in sources:
                print(f"- {s}")

        print("-" * 70)


# =========================
# MAIN
# =========================
def main():
    vectorstore = load_vector_store()
    if not vectorstore:
        return

    print("\nSelect mode:")
    print("[1] Simulation")
    print("[2] Ollama (local)")
    print("[3] Groq (API)")

    choice = input("Choice (default 1): ").strip()

    llm = None
    if choice == "2":
        llm = init_ollama_llm()
    elif choice == "3":
        llm = init_groq_llm()

    if choice != "1" and llm is None:
        print("⚠️ Falling back to simulation mode")

    chat_interface(vectorstore, llm)


if __name__ == "__main__":
    main()
