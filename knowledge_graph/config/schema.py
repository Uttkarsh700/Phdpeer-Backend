"""
HOW TO READ THIS FILE
---------------------
  ALLOWED_NODES        → the node labels the LLM is allowed to create
  NODE_PROPERTIES      → which properties the LLM should pull out of text
  ALLOWED_RELATIONSHIPS → (source_type, rel_type, target_type) tuples
                          Using tuples gives the LLM MUCH tighter control than
                          plain string lists.  It knows that STUDIES only goes
                          from Student → Topic, never the other way around.
  RELATIONSHIP_PROPERTIES → extra fields on edges (e.g. "since" on STUDIES)
  ADDITIONAL_INSTRUCTIONS → free-text prompt snippet appended to the LLM prompt;
                          used to give domain context the LLM wouldn't guess.
"""

# ─── Node Labels ────────────────────────────────────────────────────
ALLOWED_NODES: list[str] = [
    "Student",
    "Supervisor",
    "Researcher",
    "Topic",
    "Keyword",
    "Document",
    "Institution",
    "Department",
    "Conference",
    "Grant",
    "Publication",
    "Milestone",
]

# ─── Node Properties ────────────────────────────────────────────────
NODE_PROPERTIES: list[str] = [
    "name",
    "description",
    "year",
    "field",
    "stage",
    "deadline",
    "amount",
]

# ─── Relationship Types (Tuples) ───────────────────────────────────
ALLOWED_RELATIONSHIPS: list[tuple[str, str, str]] = [
    ("Student",      "STUDIES",            "Topic"),
    ("Student",      "SUPERVISED_BY",      "Supervisor"),
    ("Student",      "ENROLLED_IN",        "Institution"),
    ("Student",      "BELONGS_TO",         "Department"),
    ("Student",      "AUTHORED",           "Document"),
    ("Student",      "AUTHORED",           "Publication"),
    ("Student",      "COLLABORATES_WITH",  "Student"),
    ("Student",      "COLLABORATES_WITH",  "Researcher"),
    ("Document",     "CITES",              "Publication"),
    ("Document",     "CITES",              "Researcher"),
    ("Student",      "CITES",              "Researcher"),
    ("Document",     "REVISED_TO",         "Document"),
    ("Document",     "ABOUT",              "Topic"),
    ("Document",     "CONTAINS",           "Keyword"),
    ("Supervisor",   "SUPERVISES",         "Student"),
    ("Supervisor",   "AFFILIATED_WITH",    "Institution"),
    ("Student",      "APPLIED_TO",         "Grant"),
    ("Student",      "APPLIED_TO",         "Conference"),
    ("Student",      "ATTENDED",           "Conference"),
    ("Grant",        "AWARDED_TO",         "Student"),
    ("Grant",        "OFFERED_BY",         "Institution"),
    ("Conference",   "HOSTED_BY",          "Institution"),
    ("Publication",  "ABOUT",              "Topic"),
    ("Publication",  "BY",                 "Researcher"),
    ("Publication",  "BY",                 "Supervisor"),
    ("Student",      "HAS_MILESTONE",      "Milestone"),
    ("Document",     "ADDRESSES",          "Milestone"),
    ("Department",   "PART_OF",            "Institution"),
    ("Researcher",   "AFFILIATED_WITH",    "Institution"),
]

# ─── Relationship Properties ───────────────────────────────────────
RELATIONSHIP_PROPERTIES: list[str] = [
    "since",
    "description",
]

# ─── Additional Prompt Instructions ────────────────────────────────
ADDITIONAL_INSTRUCTIONS: str = """
You are extracting a knowledge graph from an academic research document
uploaded by a PhD student on the Frensei platform.

Important extraction rules:
- If the document mentions a supervisor by name, create a Supervisor node
  and a SUPERVISED_BY edge from the Student to that Supervisor.
- If the document cites any papers or authors, create Researcher nodes for
  the authors and Publication nodes for the papers, then wire CITES edges.
- If any conferences or grants are mentioned (even in passing), create
  Conference or Grant nodes.  Include deadlines or amounts if stated.
- Normalise person names: always use full name when available.
  "Dr. Smith" and "John Smith" appearing in the same doc are the same person.
- Create Keyword nodes for every significant domain-specific term (max 8).
- If the document is clearly a draft (contains "draft", version numbers,
  or revision marks), note that in the Document node's description property.
- Do NOT create nodes for generic concepts like "research" or "academia".
  Keep nodes concrete and specific.
"""
