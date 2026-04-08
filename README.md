# Book Graph Browser

A lightweight web-based knowledge graph visualizer for books, powered by Neo4j + vis.js.

## Features

- Select a book to view its character relationship graph
- Interactive force-directed graph with faction-based coloring
- Click any character node to see details and relationships
- Relationship labels displayed on edges
- Support for multi-volume books (e.g. trilogy merged view)

## Quick Start

### Docker Compose (Recommended)

```bash
docker compose up -d
```

This starts both Neo4j and the web app. Access:
- **Web UI**: http://localhost:8090
- **Neo4j Browser**: http://localhost:7474

### Manual Setup

1. Start Neo4j:
```bash
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:5-community
```

2. Build and run the web app:
```bash
docker build -t book-graph-web .
docker run -d --name book-graph-web -p 8090:8090 \
  -e NEO4J_URI=bolt://host.docker.internal:7687 \
  -e NEO4J_USER=neo4j \
  -e NEO4J_PASS=your_password \
  book-graph-web
```

## Import Data

Use the Neo4j Python driver to import character data:

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "your_password"))

with driver.session() as session:
    session.run("""
        CREATE (c:Character {
            name: 'Character Name',
            role: 'protagonist',
            faction: 'Group A',
            book: 'Book Title',
            description: 'Brief description'
        })
    """)
    session.run("""
        MATCH (a:Character {name: 'A'}), (b:Character {name: 'B'})
        CREATE (a)-[:RELATION {type: 'relationship type', detail: 'details'}]->(b)
    """)
```

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j Bolt URI |
| `NEO4J_USER` | `neo4j` | Neo4j username |
| `NEO4J_PASS` | `neo4j` | Neo4j password |

## Tech Stack

- **Backend**: FastAPI + neo4j-driver
- **Frontend**: vis-network.js (single HTML, no build step)
- **Database**: Neo4j 5 Community
