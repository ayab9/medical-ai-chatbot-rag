"""
chunks_medical_structured.py
Chunking structuré pour documents médicaux (WHO / NCI)
Optimisé RAG + embeddings (Groq-friendly)
"""

import re
import json
from pathlib import Path
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# =========================
# CONFIG
# =========================
DATA_PATH = "data/rag_data"
OUTPUT_JSON = "chunks.json"

MAX_SECTION_TOKENS = 400
CHUNK_OVERLAP = 40

PRIMARY_SEPARATOR = "##"

# =========================
# CLEAN TEXT
# =========================
def clean_text(text: str) -> str:
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"©.*", "", text)
    return text.strip()

# =========================
# LOAD PDF (FULL DOC)
# =========================
def load_pdfs(path: str) -> List[Document]:
    documents = []

    for pdf in Path(path).glob("*.pdf"):
        loader = PyPDFLoader(str(pdf))
        pages = loader.load()

        full_text = "\n".join(p.page_content for p in pages)
        full_text = clean_text(full_text)

        documents.append(
            Document(
                page_content=full_text,
                metadata={
                    "document_id": pdf.stem,
                    "source": pdf.name,
                    "domain": "Oncology",
                    "language": "en",
                    "total_pages": len(pages),
                }
            )
        )

    return documents

# =========================
# SPLIT BY ## SECTIONS
# =========================
def split_by_sections(doc: Document) -> List[Document]:
    raw_sections = doc.page_content.split(PRIMARY_SEPARATOR)
    sections = []

    for raw in raw_sections:
        raw = raw.strip()
        if not raw:
            continue

        lines = raw.split("\n", 1)
        section_title = lines[0].strip()
        section_body = lines[1].strip() if len(lines) > 1 else ""

        sections.append(
            Document(
                page_content=f"## {section_title}\n{section_body}",
                metadata={
                    **doc.metadata,
                    "section": section_title
                }
            )
        )

    return sections

# =========================
# SEMANTIC SPLIT (IF TOO LONG)
# =========================
def semantic_split(section: Document) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=MAX_SECTION_TOKENS,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n- ", "\n• ", "\n", ". "]
    )

    return splitter.split_documents([section])

# =========================
# CHUNKING PIPELINE
# =========================
def chunk_documents(documents: List[Document]) -> List[Document]:
    chunks = []
    chunk_id = 0

    for doc in documents:
        sections = split_by_sections(doc)

        for section in sections:
            # Simple heuristic: long section → semantic split
            if len(section.page_content.split()) > MAX_SECTION_TOKENS:
                sub_chunks = semantic_split(section)
            else:
                sub_chunks = [section]

            for c in sub_chunks:
                c.metadata["chunk_id"] = chunk_id
                chunk_id += 1
                chunks.append(c)

    return chunks

# =========================
# SAVE JSON
# =========================
def save_chunks(chunks: List[Document]):
    output = []

    for c in chunks:
        output.append({
            "chunk_id": c.metadata["chunk_id"],
            "content": c.page_content,
            "metadata": c.metadata
        })

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

# =========================
# MAIN
# =========================
def main():
    print("📥 Loading PDFs...")
    docs = load_pdfs(DATA_PATH)

    print("✂️ Chunking by medical sections...")
    chunks = chunk_documents(docs)

    print(f"✅ {len(chunks)} structured chunks created")
    save_chunks(chunks)

    print("💾 Saved to chunks.json")

if __name__ == "__main__":
    main()
