from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from neo4j import GraphDatabase
import os

app = FastAPI()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "neo4j")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))


@app.get("/api/books")
def list_books():
    with driver.session() as s:
        result = s.run("MATCH (n:Character) RETURN DISTINCT n.book AS book, count(n) AS count ORDER BY count DESC")
        return [{"book": r["book"], "count": r["count"]} for r in result]


@app.get("/api/graph/{book}")
def get_graph(book: str):
    with driver.session() as s:
        # 如果 book 是 "三体全集"，匹配所有三体开头的
        if book == "三体全集":
            book_filter = "a.book STARTS WITH '三体' OR b.book STARTS WITH '三体'"
        elif book == "全部":
            book_filter = "TRUE"
        else:
            book_filter = "a.book = $book OR b.book = $book"

        query = f"""
            MATCH (a:Character)-[r:RELATION]->(b:Character)
            WHERE {book_filter}
            RETURN a.name AS src, a.role AS src_role, a.faction AS src_faction,
                   a.description AS src_desc, a.book AS src_book,
                   r.type AS rel_type, r.detail AS rel_detail,
                   b.name AS tgt, b.role AS tgt_role, b.faction AS tgt_faction,
                   b.description AS tgt_desc, b.book AS tgt_book
        """
        rows = s.run(query, book=book).data()

    nodes = {}
    edges = []
    for r in rows:
        for prefix in ("src", "tgt"):
            name = r[f"{prefix}"]
            if name not in nodes:
                nodes[name] = {
                    "id": name,
                    "label": name,
                    "role": r[f"{prefix}_role"],
                    "faction": r[f"{prefix}_faction"],
                    "description": r[f"{prefix}_desc"],
                    "book": r[f"{prefix}_book"],
                }
        edges.append({
            "from": r["src"],
            "to": r["tgt"],
            "label": r["rel_type"],
            "detail": r["rel_detail"],
        })

    return {"nodes": list(nodes.values()), "edges": edges}


@app.get("/api/character/{name}")
def get_character(name: str):
    with driver.session() as s:
        result = s.run("""
            MATCH (a:Character {name: $name})-[r:RELATION]-(b:Character)
            RETURN a.name AS name, a.role AS role, a.faction AS faction,
                   a.description AS description, a.book AS book,
                   r.type AS rel_type, r.detail AS rel_detail,
                   b.name AS other,
                   CASE WHEN startNode(r) = a THEN 'out' ELSE 'in' END AS direction
        """, name=name).data()
        if not result:
            return {"error": "not found"}
        char = {
            "name": result[0]["name"],
            "role": result[0]["role"],
            "faction": result[0]["faction"],
            "description": result[0]["description"],
            "book": result[0]["book"],
            "relations": [
                {
                    "other": r["other"],
                    "type": r["rel_type"],
                    "detail": r["rel_detail"],
                    "direction": r["direction"],
                }
                for r in result
            ],
        }
        return char


@app.get("/", response_class=HTMLResponse)
def index():
    return open("/app/static/index.html").read()
