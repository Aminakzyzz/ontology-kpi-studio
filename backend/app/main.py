from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.auto_ontology import integration

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "studio.db"
ONTOLOGY_PATH = ROOT / "ontology" / "operations.yaml"


def ensure_demo_database() -> None:
    """Create a small, public-safe dataset used by the demo application."""
    DATA_DIR.mkdir(exist_ok=True)
    if DB_PATH.exists():
        return
    with sqlite3.connect(DB_PATH) as connection:
        connection.executescript(
            """
            CREATE TABLE customers (
              customer_id INTEGER PRIMARY KEY,
              segment TEXT NOT NULL,
              region TEXT NOT NULL
            );
            CREATE TABLE deliveries (
              delivery_id INTEGER PRIMARY KEY,
              customer_id INTEGER NOT NULL,
              planned_date TEXT NOT NULL,
              delivered_date TEXT NOT NULL,
              status TEXT NOT NULL,
              revenue_eur REAL NOT NULL,
              FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
            );
            INSERT INTO customers VALUES
              (1, 'Enterprise', 'DACH'), (2, 'Mid-market', 'DACH'),
              (3, 'Enterprise', 'Nordics'), (4, 'SMB', 'Benelux');
            INSERT INTO deliveries VALUES
              (101, 1, '2026-01-10', '2026-01-10', 'on_time', 4200),
              (102, 1, '2026-01-14', '2026-01-16', 'late', 1800),
              (103, 2, '2026-01-18', '2026-01-18', 'on_time', 950),
              (104, 3, '2026-02-03', '2026-02-05', 'late', 3150),
              (105, 4, '2026-02-10', '2026-02-10', 'on_time', 680),
              (106, 2, '2026-02-14', '2026-02-14', 'on_time', 1100),
              (107, 3, '2026-03-01', '2026-03-01', 'on_time', 2200),
              (108, 1, '2026-03-06', '2026-03-08', 'late', 1600);
            """
        )


ensure_demo_database()

app = FastAPI(title="Ontology KPI Studio", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=500)


QUERY_LIBRARY: list[dict[str, Any]] = [
    {
        "terms": ("on time", "delivery", "service"),
        "title": "On-time delivery rate",
        "summary": "Share of deliveries completed on or before their planned date.",
        "sql": "SELECT ROUND(100.0 * SUM(status = 'on_time') / COUNT(*), 1) AS on_time_rate_pct FROM deliveries;",
        "chart": "gauge",
    },
    {
        "terms": ("revenue", "region", "sales"),
        "title": "Revenue by region",
        "summary": "Revenue aggregated by the customer region.",
        "sql": "SELECT c.region, ROUND(SUM(d.revenue_eur), 0) AS revenue_eur FROM deliveries d JOIN customers c USING(customer_id) GROUP BY c.region ORDER BY revenue_eur DESC;",
        "chart": "bar",
    },
    {
        "terms": ("late", "delay", "quality"),
        "title": "Late deliveries by month",
        "summary": "Monthly count of delayed deliveries, useful for service-quality monitoring.",
        "sql": "SELECT substr(planned_date, 1, 7) AS month, COUNT(*) AS late_deliveries FROM deliveries WHERE status = 'late' GROUP BY month ORDER BY month;",
        "chart": "line",
    },
]


def execute(sql: str) -> list[dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        return [dict(row) for row in connection.execute(sql).fetchall()]


def select_query(question: str) -> dict[str, Any]:
    normalized = question.lower()
    ranked = sorted(
        QUERY_LIBRARY,
        key=lambda item: sum(term in normalized for term in item["terms"]),
        reverse=True,
    )
    if not any(term in normalized for term in ranked[0]["terms"]):
        raise HTTPException(
            status_code=422,
            detail="This local demo currently supports delivery rate, revenue by region, and late-delivery questions.",
        )
    return ranked[0]


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "data_source": "local SQLite"}


@app.get("/api/ontology")
def ontology() -> dict[str, Any]:
    return yaml.safe_load(ONTOLOGY_PATH.read_text())


@app.get("/api/integration")
def integration_status() -> dict[str, str | bool | None]:
    """Report the semantic-provider mode without revealing credentials."""
    return integration.status()


@app.post("/api/ask")
def ask(request: AskRequest) -> dict[str, Any]:
    intent = select_query(request.question)
    rows = execute(intent["sql"])
    return {
        "question": request.question,
        "title": intent["title"],
        "summary": intent["summary"],
        "sql": intent["sql"],
        "rows": rows,
        "chart": intent["chart"],
        "grounding": ["delivery", "service quality", "revenue"],
        "mode": "local semantic adapter",
    }

