"""
utils/pdf_loader.py
───────────────────
PDF  →  list[Document]

Why chunking matters
--------------------
LLMGraphTransformer sends each Document to the LLM as one prompt.
A 40-page thesis is way too long for a single call — it blows the
context window AND makes extraction noisy.  We slice the PDF into
~500-token chunks with a small overlap so that sentences that land
on a chunk boundary still appear together in at least one chunk.
"""

import fitz                                  # PyMuPDF  (pip install pymupdf)
from langchain_core.documents import Document


def load_pdf(file_path: str) -> list[Document]:
    """
    Read a PDF and return one Document per page.
    Each Document's metadata carries the page number and source path
    so we can trace every extracted node back to its origin later.
    """
    doc   = fitz.open(file_path)
    pages = []
    for page_num in range(len(doc)):
        text = doc[page_num].get_text()
        if text.strip():                     # skip blank pages
            pages.append(
                Document(
                    page_content=text,
                    metadata={
                        "source":   file_path,
                        "page":     page_num + 1,   # 1-indexed for humans
                    },
                )
            )
    doc.close()
    return pages


def chunk_documents(
    documents: list[Document],
    chunk_size:    int = 2000,   # characters  (≈ 500 tokens)
    chunk_overlap: int = 200,    # characters of overlap between chunks
) -> list[Document]:
    """
    Take the per-page Documents and re-slice them into fixed-size chunks.

    Why not just use LangChain's RecursiveCharacterTextSplitter?
    ─────────────────────────────────────────────────────────────
    It works fine too.  We wrote this manually so every line is visible
    and there are no hidden defaults that could surprise you.  Swap in
    RecursiveCharacterTextSplitter if you prefer — the output type is
    identical (list[Document]).
    """
    chunks: list[Document] = []

    for doc in documents:
        text     = doc.page_content
        metadata = doc.metadata          # carries source + page

        start = 0
        chunk_index = 0
        while start < len(text):
            end   = start + chunk_size
            chunk = text[start:end]

            if chunk.strip():            # skip whitespace-only chunks
                chunks.append(
                    Document(
                        page_content=chunk,
                        metadata={
                            **metadata,
                            "chunk_index": chunk_index,
                        },
                    )
                )
                chunk_index += 1

            start += chunk_size - chunk_overlap   # slide forward

    return chunks


# ─── convenience: do both in one call ───────────────────────────────
def load_and_chunk(file_path: str, chunk_size: int = 2000, chunk_overlap: int = 200) -> list[Document]:
    """Single entry-point: PDF path  →  chunked Documents."""
    pages  = load_pdf(file_path)
    chunks = chunk_documents(pages, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    print(f"[pdf_loader] {file_path} → {len(pages)} pages → {len(chunks)} chunks")
    return chunks
