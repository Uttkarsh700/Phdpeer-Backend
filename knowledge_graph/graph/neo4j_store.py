
import os
from typing import List

from langchain_neo4j import Neo4jGraph


# ─── connection ─────────────────────────────────────────────────────
def get_neo4j_graph() -> Neo4jGraph:
    """
    Build and return a Neo4jGraph instance.
    Reads NEO4J_URI / USERNAME / PASSWORD from env (set via .env).
    """
    return Neo4jGraph(
        url=os.getenv("NEO4J_URI",      "bolt://localhost:7687"),
        username=os.getenv("NEO4J_USERNAME", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", ""),
        database=os.getenv("NEO4J_DATABASE", "neo4j"),
        refresh_schema=True,             # auto-refresh schema cache after writes
    )


# ─── store ──────────────────────────────────────────────────────────
def store_graph_documents(graph_documents, graph: Neo4jGraph | None = None) -> None:
    """
    Persist a list of GraphDocuments into Neo4j.

    source_node : bool (default True inside add_graph_documents)
        When True, LangChain automatically creates a :Chunk node for
        each source Document and links every extracted entity to it.
        This is how we maintain "where did this node come from?" provenance.
    """
    if graph is None:
        graph = get_neo4j_graph()

    graph.add_graph_documents(
        graph_documents,
        baseEntity="__ENTITY__",          # internal label LangChain adds; leave it
        baseTriplet="__TRIPLET__",        # same
        source_node=True,                 # keep chunk provenance links
    )
    print(f"[neo4j_store] Stored {len(graph_documents)} GraphDocuments.")


# ─── utility queries ────────────────────────────────────────────────
# These are thin wrappers that run Cypher and return dicts.
# Useful for the dashboard / debugging.  Swap in GraphCypherQAChain
# (see query.py) if you want natural-language queries instead.

def get_student_subgraph(student_name: str, graph: Neo4jGraph | None = None) -> list[dict]:
    """Return all nodes and relationships reachable from a Student node."""
    if graph is None:
        graph = get_neo4j_graph()

    cypher = """
    MATCH (s:Student {name: $name})
    OPTIONAL MATCH (s)-[r]->(target)
    RETURN s, r, target
    LIMIT 100
    """
    return graph.query(cypher, params={"name": student_name})


def get_supervision_latency(student_name: str, graph: Neo4jGraph | None = None) -> list[dict]:
    """
    Placeholder: once supervision-meeting nodes are in the graph,
    this query will compute days-between-submission-and-feedback.
    """
    if graph is None:
        graph = get_neo4j_graph()

    cypher = """
    MATCH (s:Student {name: $name})-[:SUPERVISED_BY]->(sup:Supervisor)
    RETURN s.name AS student, sup.name AS supervisor
    """
    return graph.query(cypher, params={"name": student_name})


def get_most_connected_nodes(top_n: int = 10, graph: Neo4jGraph | None = None) -> list[dict]:
    """Return the top-N nodes by total degree (in + out)."""
    if graph is None:
        graph = get_neo4j_graph()

    cypher = """
    MATCH (n)
    WHERE NOT n:Chunk AND NOT n:__ENTITY__ AND NOT n:__TRIPLET__
    WITH n, size([(n)-[]->()]) + size([(n)<-[]-()]) AS degree
    RETURN labels(n)[0] AS label, n.name AS name, degree
    ORDER BY degree DESC
    LIMIT $top_n
    """
    return graph.query(cypher, params={"top_n": top_n})


def get_all_node_counts(graph: Neo4jGraph | None = None) -> list[dict]:
    """Aggregate count of each node label — handy sanity check."""
    if graph is None:
        graph = get_neo4j_graph()

    cypher = """
    MATCH (n)
    WHERE NOT n:Chunk AND NOT n:__ENTITY__ AND NOT n:__TRIPLET__
    RETURN labels(n)[0] AS label, count(n) AS count
    ORDER BY count DESC
    """
    return graph.query(cypher)
