# 🩺 Medical AI Chatbot with RAG

An AI-powered medical chatbot specialized in breast cancer information, built using Retrieval-Augmented Generation (RAG).  
The chatbot answers user questions based strictly on trusted medical documents.

---

## 🚀 Features

- 🎯 Breast cancer–focused medical chatbot
- 🧠 Retrieval-Augmented Generation (RAG)
- 📚 Context-aware answers based on medical PDFs
- ⚡ Groq LLM (Llama 3.3 70B) integration
- 🔍 Clear source attribution
- 💬 Compassionate and structured responses

---

## 🧠 Technologies

- **Backend**: Python, Flask
- **AI/ML**: LangChain, Groq LLM (Llama 3.3 70B)
- **Vector Store**: ChromaDB
- **Embeddings**: HuggingFace Embeddings
- **Frontend**: HTML, CSS, JavaScript

---

## 📂 Project Structure
```bash
.
├── app.py                 # Flask application entry point
├── rag_chatbot.py         # RAG chatbot logic
├── embeddings.py          # Embedding generation
├── chunks.py              # Document chunking utilities
├── chunks.json            # Preprocessed document chunks
├── templates/             # HTML templates
├── static/                # CSS, JS, and static assets
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── .env                   # Environment variables (not tracked)
└── .gitignore             # Git ignore rules
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-username/breast-cancer-rag-chatbot.git
cd breast-cancer-rag-chatbot
```

### 2️⃣ Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure environment variables

Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```

> 💡 **Tip**: Get your Groq API key from [Groq Console](https://console.groq.com/)

### 5️⃣ Run the application
```bash
python app.py
```

Open your browser and navigate to 👉 **http://localhost:5000**

---

## 🎯 Usage

1. Open the web interface
2. Type your breast cancer–related medical question
3. The chatbot retrieves relevant information from medical documents
4. Receive accurate, context-aware answers with source citations

---

## 📋 Requirements
```txt
flask
langchain
chromadb
sentence-transformers
groq
python-dotenv
```

---

## ⚠️ Medical Disclaimer

**Important**: This chatbot is for **educational and informational purposes only**.  
It does **not** provide medical diagnosis or replace professional medical advice.  
Always consult a qualified healthcare professional for medical concerns.




---

## 👩‍💻 Author

**Aya Belhadji**  
Master's in Data Science  

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/aya-belhadji-6b2550295)

---

## 🙏 Acknowledgments

- Groq for providing fast LLM inference
- LangChain for RAG framework
- Medical documents and resources used for training

---

<div align="center">
  Made with ❤️ for better healthcare information access
</div>