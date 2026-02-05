
import asyncio
from typing import List

from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_google_genai import ChatGoogleGenerativeAI

from config.schema import (
    ALLOWED_NODES,
    ALLOWED_RELATIONSHIPS,
    NODE_PROPERTIES,
    RELATIONSHIP_PROPERTIES,
    ADDITIONAL_INSTRUCTIONS,
)


# ─── build the transformer once at import time ─────────────────────
# temperature=0 → deterministic extraction (no creative hallucination)
_llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
)

llm_transformer = LLMGraphTransformer(
    llm=_llm,
    allowed_nodes=ALLOWED_NODES,
    allowed_relationships=ALLOWED_RELATIONSHIPS,     # tuples!
    node_properties=NODE_PROPERTIES,
    relationship_properties=RELATIONSHIP_PROPERTIES,
    strict_mode=True,                                # filter out anything not in schema
    additional_instructions=ADDITIONAL_INSTRUCTIONS,
)


# ─── async batch extraction ─────────────────────────────────────────
async def extract_graph_documents(chunks: List[Document]):
    """
    Run LLM extraction on every chunk IN PARALLEL and return the
    combined list of GraphDocuments.

    aconvert_to_graph_documents is the async version built into
    LLMGraphTransformer — it handles the concurrency for us.
    """
    graph_documents = await llm_transformer.aconvert_to_graph_documents(chunks)
    return graph_documents


# ─── sync convenience wrapper ───────────────────────────────────────
def extract_graph_documents_sync(chunks: List[Document]):
    """
    Drop-in for scripts / notebooks that aren't already in an async loop.
    """
    return asyncio.run(extract_graph_documents(chunks))


# ─── quick debug helper ─────────────────────────────────────────────
def print_graph_summary(graph_documents) -> None:
    """Print a human-readable summary of what was extracted."""
    total_nodes = 0
    total_rels  = 0
    node_counts: dict[str, int] = {}
    rel_counts:  dict[str, int] = {}

    for gd in graph_documents:
        for node in gd.nodes:
            total_nodes += 1
            node_counts[node.type] = node_counts.get(node.type, 0) + 1
        for rel in gd.relationships:
            total_rels  += 1
            key = rel.type
            rel_counts[key] = rel_counts.get(key, 0) + 1

    print("\n── Extraction Summary ──")
    print(f"  GraphDocuments : {len(graph_documents)}")
    print(f"  Total nodes    : {total_nodes}")
    for label, count in sorted(node_counts.items(), key=lambda x: -x[1]):
        print(f"      {label:20s} {count}")
    print(f"  Total rels     : {total_rels}")
    for rtype, count in sorted(rel_counts.items(), key=lambda x: -x[1]):
        print(f"      {rtype:20s} {count}")
    print()
