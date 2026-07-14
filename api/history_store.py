import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


DB_PATH = Path("query_history.db")


def init_history_db() -> None:
    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                intent TEXT,
                validation_status TEXT,
                mlflow_run_id TEXT,
                latency_ms INTEGER,
                full_payload TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        con.commit()


def save_query(payload: Dict[str, Any]) -> int:
    created_at = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(DB_PATH) as con:
        cur = con.execute(
            """
            INSERT INTO query_history (
                question,
                answer,
                intent,
                validation_status,
                mlflow_run_id,
                latency_ms,
                full_payload,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.get("question", ""),
                payload.get("answer", ""),
                payload.get("intent", ""),
                payload.get("validation_status"),
                payload.get("mlflow_run_id"),
                payload.get("total_latency_ms"),
                json.dumps(payload, default=str),
                created_at,
            ),
        )
        con.commit()
        return int(cur.lastrowid)


def list_history(limit: int = 25) -> List[Dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            """
            SELECT id, question, answer, intent, validation_status,
                   mlflow_run_id, latency_ms, created_at
            FROM query_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_history_item(item_id: int) -> Optional[Dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        row = con.execute(
            "SELECT full_payload FROM query_history WHERE id = ?",
            (item_id,),
        ).fetchone()

    if not row:
        return None

    return json.loads(row["full_payload"])