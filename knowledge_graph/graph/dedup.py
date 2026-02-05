
import json
from collections import defaultdict
from typing import List

from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph

from graph.neo4j_store import get_neo4j_graph


# ─── Pass 1: LLM clustering ─────────────────────────────────────────
def cluster_entities(graph_documents) -> dict[str, list[list[str]]]:
    """
    Input : list of GraphDocuments (straight from the transformer)
    Output: { node_type: [ [id_a, id_b], [id_c], … ] }
            Each inner list is a cluster of IDs that are the same entity.

    Only runs clustering for types that have ≥ 2 unique IDs.
    """
    # ── collect all IDs by type ──
    ids_by_type: dict[str, set[str]] = defaultdict(set)
    for gd in graph_documents:
        for node in gd.nodes:
            ids_by_type[node.type].add(node.id)

    llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

    clusters: dict[str, list[list[str]]] = {}

    for node_type, ids in ids_by_type.items():
        if len(ids) < 2:
            # nothing to deduplicate
            clusters[node_type] = [[i] for i in ids]
            continue

        # ── ask the LLM ──
        prompt = (
            f"These are all the {node_type} entity names extracted from "
            f"a research document:\n\n"
            f"{json.dumps(sorted(ids), indent=2)}\n\n"
            f"Some of these may refer to the same real-world entity "
            f"(e.g. 'Dr. Smith' and 'John Smith' and 'Smith').\n"
            f"Group them into clusters.  Each cluster is a list of names "
            f"that refer to the SAME entity.\n"
            f"Names that are definitely unique get their own single-item cluster.\n\n"
            f"Return ONLY a JSON array of arrays.  No explanation.\n"
            f'Example: [["Dr. Smith", "John Smith"], ["Emma Wilson"]]'
        )

        response = llm.invoke(prompt)
        raw = response.content.strip()

        # strip markdown code fences if the LLM wraps in ```json … ```
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        try:
            parsed: list[list[str]] = json.loads(raw)
            clusters[node_type] = parsed
        except json.JSONDecodeError:
            # fallback: treat every ID as its own cluster (no merge)
            print(f"[dedup] JSON parse failed for {node_type} — skipping dedup for this type")
            clusters[node_type] = [[i] for i in ids]

    return clusters


# ─── Pass 2: Neo4j merge ────────────────────────────────────────────
def merge_clusters_in_neo4j(
    clusters: dict[str, list[list[str]]],
    graph: Neo4jGraph | None = None,
) -> None:
    """
    For each cluster with > 1 member, pick the longest name as canonical
    and run APOC mergeNodes to collapse them.

    How APOC mergeNodes works:
        - All relationships from the deleted nodes are moved to the surviving node.
        - Properties are merged (last-write wins for conflicts).
        - The graph stays fully connected.
    """
    if graph is None:
        graph = get_neo4j_graph()

    for node_type, cluster_list in clusters.items():
        for cluster in cluster_list:
            if len(cluster) < 2:
                continue                 # nothing to merge

            # canonical = longest name (most complete)
            canonical = max(cluster, key=len)
            others    = [n for n in cluster if n != canonical]

            print(f"[dedup] {node_type}: merging {others} → '{canonical}'")

            # APOC merge query
            cypher = """
            MATCH (keep:{label} {{name: $canonical}})
            WITH keep
            MATCH (dup:{label})
            WHERE dup.name IN $others
            CALL apoc.refactor.mergeNodes([keep, dup], {{properties: 'combine', mergeRels: true}})
            YIELD node
            RETURN node
            """.format(label=node_type)

            try:
                graph.query(cypher, params={"canonical": canonical, "others": others})
            except Exception as e:
                print(f"[dedup] APOC merge failed for {cluster}: {e}")


# ─── single entry-point ─────────────────────────────────────────────
def deduplicate(graph_documents, graph: Neo4jGraph | None = None) -> None:
    """
    Full pipeline: cluster with LLM, then merge in Neo4j.
    Call this AFTER store_graph_documents().
    """
    print("[dedup] Clustering entities with LLM …")
    clusters = cluster_entities(graph_documents)

    print("[dedup] Merging clusters in Neo4j …")
    merge_clusters_in_neo4j(clusters, graph=graph)

    print("[dedup] Done.")
