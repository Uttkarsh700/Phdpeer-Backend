
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain

from graph.neo4j_store import get_neo4j_graph


def build_qa_chain() -> GraphCypherQAChain:
    """Assemble the chain once; reuse it for every question."""
    llm   = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    graph = get_neo4j_graph()

    chain = GraphCypherQAChain.from_llm(
        llm=llm,
        graph=graph,
        verbose=True,                    # prints the generated Cypher — great for debugging
        validate_cypher=True,            # second LLM pass to fix bad Cypher before execution
        allow_dangerous_request=True,    # needed because the chain can run arbitrary Cypher
    )
    return chain


def ask(question: str) -> str:
    """One-liner: question  →  answer."""
    chain    = build_qa_chain()
    response = chain.invoke({"query": question})
    return response["result"]


# ─── interactive CLI ────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print(" Frensei Knowledge Graph — Natural Language Query")
    print(" Type 'quit' to exit")
    print("=" * 60)

    chain = build_qa_chain()          # build once, reuse across questions

    while True:
        q = input("\nYou: ").strip()
        if q.lower() in ("quit", "exit", "q"):
            break
        if not q:
            continue

        try:
            result = chain.invoke({"query": q})
            print(f"\nAnswer: {result['result']}")
        except Exception as e:
            print(f"\nError: {e}")
