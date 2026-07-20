import sqlite3
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils.config import LOG_DB_PATH


def init_db():
    LOG_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(LOG_DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS query_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_role TEXT,
            query TEXT,
            status TEXT,
            block_reason TEXT,
            sources TEXT,
            answer TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_query(user_role: str, query: str, status: str, block_reason: str = "", sources: str = "", answer: str = ""):
    """
    status: 'allowed', 'blocked_moderation', 'blocked_injection', 'blocked_no_context'
    """
    init_db()
    conn = sqlite3.connect(LOG_DB_PATH)
    conn.execute(
        "INSERT INTO query_logs (timestamp, user_role, query, status, block_reason, sources, answer) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (datetime.now().isoformat(), user_role, query, status, block_reason, sources, answer)
    )
    conn.commit()
    conn.close()


def get_all_logs():
    init_db()
    conn = sqlite3.connect(LOG_DB_PATH)
    cursor = conn.execute("SELECT * FROM query_logs ORDER BY id DESC")
    columns = [desc[0] for desc in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return rows