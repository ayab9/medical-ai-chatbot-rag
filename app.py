"""
app.py - Flask Backend pour Breast Cancer AI Assistant
VERSION FINALE - Focus sur RAG Chatbot uniquement
"""
from flask import Flask, render_template, request, jsonify
import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate

# Configuration
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# =========================
# CONFIGURATION RAG
# =========================
class Config:
    PERSIST_DIRECTORY = "chroma_db_free"
    COLLECTION_NAME = "breast_cancer_docs"
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    TEMPERATURE = 0.2
    MAX_TOKENS = 600
    MAX_CHARS_PER_DOC = 1200
    DEFAULT_K = 3

# Variables globales
vectorstore = None
llm = None

# =========================
# INITIALISATION RAG
# =========================
def init_vectorstore():
    """Charge la base vectorielle"""
    global vectorstore
    
    if not Path(Config.PERSIST_DIRECTORY).exists():
        print("❌ Base vectorielle introuvable")
        return False
    
    embeddings = HuggingFaceEmbeddings(
        model_name=Config.EMBEDDING_MODEL,
        encode_kwargs={"normalize_embeddings": True}
    )
    
    vectorstore = Chroma(
        persist_directory=Config.PERSIST_DIRECTORY,
        embedding_function=embeddings,
        collection_name=Config.COLLECTION_NAME
    )
    
    print(f"✅ Vector DB chargée: {vectorstore._collection.count()} chunks")
    return True

def init_groq_llm():
    """Initialise Groq LLM"""
    global llm
    
    try:
        from langchain_groq import ChatGroq
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("⚠️  GROQ_API_KEY manquante - Mode simulation activé")
            return False
        
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS,
            api_key=api_key
        )
        
        print("✅ Groq LLM prêt")
        return True
        
    except Exception as e:
        print(f"⚠️  Erreur Groq: {e}")
        print("⚠️  Mode simulation activé")
        return False

# =========================
# PROMPT MÉDICAL
# =========================
def create_medical_prompt():
    system_prompt = """You are a compassionate medical information assistant specialized in breast cancer.

Your role is to provide accurate, supportive, and clear information to help women understand breast cancer better.

STRICT RULES:
1. Use ONLY information from the provided CONTEXT
2. Be compassionate and supportive in your tone
3. Structure answers clearly with bullet points or sections
4. If information is not available, say: "This information is not available in my current medical database"
5. Always remind that this is informational support, not medical diagnosis
6. Encourage consulting healthcare professionals for personal cases

RESPONSE FORMAT:
- Use clear sections (##)
- Use bullet points (*)
- Be concise but complete
- Maintain professional yet warm tone"""

    human_prompt = """MEDICAL CONTEXT:
{context}

QUESTION:
{question}

Provide a clear, compassionate answer:"""

    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])

# =========================
# PIPELINE RAG
# =========================
def rag_query(question):
    """Exécute une requête RAG"""
    if not vectorstore:
        return {
            "answer": "❌ System not initialized. Please contact the administrator.",
            "sources": []
        }
    
    try:
        k = Config.DEFAULT_K
        
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
        
        docs = retriever.invoke(question)
        
        if not docs:
            return {
                "answer": "I couldn't find relevant information in my medical knowledge base.",
                "sources": []
            }
        
        # Préparer contexte
        context_parts = []
        sources = []
        
        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "Medical document")
            content = doc.page_content[:Config.MAX_CHARS_PER_DOC]
            
            context_parts.append(f"[Source {i+1}: {source}]\n{content}")
            
            if source not in sources:
                sources.append(source)
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Mode simulation si pas de LLM
        if not llm:
            answer = "**[Simulation Mode]**\n\n"
            answer += "I found relevant information:\n\n"
            for doc in docs[:2]:
                preview = doc.page_content[:300].strip()
                answer += f"• {preview}...\n\n"
            answer += "*Note: Simulation mode active. For complete answers, configure a Groq API key.*"
        else:
            # Générer réponse avec LLM
            prompt = create_medical_prompt()
            messages = prompt.format_messages(
                context=context,
                question=question
            )
            
            response = llm.invoke(messages)
            answer = response.content if hasattr(response, "content") else str(response)
        
        return {
            "answer": answer,
            "sources": sources
        }
        
    except Exception as e:
        print(f"❌ Erreur RAG: {str(e)}")
        return {
            "answer": f"❌ Error during search: {str(e)}",
            "sources": []
        }

# =========================
# ROUTES FLASK
# =========================
@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@app.route('/chatbot')
def chatbot():
    """Page chatbot"""
    stats = {
        "total_docs": 10,
        "total_chunks": vectorstore._collection.count() if vectorstore else 0,
        "model": "Llama 3.3 70B (Groq)" if llm else "Simulation Mode"
    }
    return render_template('chatbot.html', stats=stats)

@app.route('/api/ask', methods=['POST'])
def api_ask():
    """API endpoint pour questions RAG"""
    data = request.get_json()
    
    question = data.get('question', '').strip()
    
    if not question:
        return jsonify({
            "success": False,
            "error": "Empty question"
        })
    
    result = rag_query(question)
    
    return jsonify({
        "success": True,
        "answer": result["answer"],
        "sources": result["sources"]
    })

@app.route('/api/stats')
def api_stats():
    """Statistiques système"""
    return jsonify({
        "system_stats": {
            "documents": 10,
            "chunks": vectorstore._collection.count() if vectorstore else 0,
            "model": "Llama 3.3 70B (Groq)" if llm else "Simulation Mode",
            "embedding_model": Config.EMBEDDING_MODEL
        }
    })

# =========================
# INITIALISATION
# =========================
if __name__ == '__main__':
    print("=" * 60)
    print("🎗️  BREAST CANCER AI ASSISTANT - RAG CHATBOT")
    print("=" * 60)
    print("\n🚀 System initialization...")
    
    # Charger la base vectorielle
    if not init_vectorstore():
        print("⚠️  System started in degraded mode (without RAG)")
    
    # Charger le LLM (optionnel)
    if init_groq_llm():
        print("✅ Mode: Groq LLM (Llama 3.3 70B)")
    else:
        print("✅ Mode: Simulation (without API)")
    
    print("\n" + "=" * 60)
    print("✅ System ready!")
    print("🌐 Access: http://localhost:5000")
    print("💖 by AYA BELHADJI")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)