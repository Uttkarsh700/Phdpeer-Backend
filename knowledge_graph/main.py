
import argparse
import sys
from dotenv import load_dotenv

# ── load .env FIRST so every downstream import can read env vars ────
load_dotenv()

from utils.pdf_loader    import load_and_chunk
from graph.transformer   import extract_graph_documents_sync, print_graph_summary
from graph.neo4j_store   import store_graph_documents, get_all_node_counts
from graph.dedup         import deduplicate


def run_pipeline(file_path: str) -> None:
    """Full pipeline, top to bottom."""

    # ── 1. Load & chunk ─────────────────────────────────────────────
    print(f"\n[1/5] Loading & chunking: {file_path}")
    chunks = load_and_chunk(file_path)
    print(f"      → {len(chunks)} chunks ready for extraction")

    # ── 2. LLM extraction ───────────────────────────────────────────
    print("\n[2/5] Running LLMGraphTransformer (async, parallel) …")
    graph_documents = extract_graph_documents_sync(chunks)
    print_graph_summary(graph_documents)

    # ── 3. Store in Neo4j ───────────────────────────────────────────
    print("[3/5] Storing GraphDocuments in Neo4j …")
    store_graph_documents(graph_documents)

    # ── 4. Deduplicate ──────────────────────────────────────────────
    print("\n[4/5] Deduplicating entities …")
    deduplicate(graph_documents)

    # ── 5. Final count ──────────────────────────────────────────────
    print("\n[5/5] Final node counts in Neo4j:")
    for row in get_all_node_counts():
        print(f"      {row['label']:20s} {row['count']}")

    print("\n✅ Pipeline complete.  Open Neo4j Browser or run query.py to explore.\n")


# ─── CLI ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Frensei Knowledge Graph Builder")
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="Path to the PDF to ingest (e.g. research_proposal.pdf)",
    )
    args = parser.parse_args()

    if not args.file.lower().endswith(".pdf"):
        print("Error: only PDF files are supported right now.")
        sys.exit(1)

    run_pipeline(args.file)
