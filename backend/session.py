import sqlite3
import json
import os
import time
from typing import Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), 'session.db')
SESSION_TTL_SECONDS = 3600  # Sessions expire after 1 hour of inactivity

# Module-level connection (reused across requests, not recreated each time)
_conn: Optional[sqlite3.Connection] = None

def get_connection() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _conn.execute('PRAGMA journal_mode=WAL;')
        _conn.execute('PRAGMA synchronous=NORMAL;')  # Faster writes, still safe with WAL
    return _conn

def init_db():
    conn = get_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            state JSON NOT NULL,
            updated_at REAL NOT NULL DEFAULT 0
        )
    ''')
    # Migration: add updated_at column if it doesn't exist (for existing DBs)
    try:
        conn.execute('ALTER TABLE sessions ADD COLUMN updated_at REAL NOT NULL DEFAULT 0')
    except Exception:
        pass  # Column already exists — this is expected on a fresh run
    conn.commit()

def save_session(session_id: str, state: Dict[str, Any]):
    conn = get_connection()
    conn.execute('''
        INSERT INTO sessions (session_id, state, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            state = excluded.state,
            updated_at = excluded.updated_at
    ''', (session_id, json.dumps(state), time.time()))
    conn.commit()

def load_session(session_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.execute(
        'SELECT state, updated_at FROM sessions WHERE session_id = ?',
        (session_id,)
    )
    row = cursor.fetchone()
    if row:
        state_json, updated_at = row
        # Check if session has expired
        if time.time() - updated_at > SESSION_TTL_SECONDS:
            conn.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
            conn.commit()
            return None
        return json.loads(state_json)
    return None

def delete_session(session_id: str):
    """Explicitly delete a session (useful for cleanup after interview completes)."""
    conn = get_connection()
    conn.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
    conn.commit()

# Ensure the table is created upon module import
init_db()
