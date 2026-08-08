import sqlite3
import json
import os
from typing import Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), 'session.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    # Enable WAL mode for better concurrency and fewer write-lock issues
    conn.execute('PRAGMA journal_mode=WAL;')
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                state JSON NOT NULL
            )
        ''')

def save_session(session_id: str, state: Dict[str, Any]):
    with get_connection() as conn:
        conn.execute('''
            INSERT INTO sessions (session_id, state) 
            VALUES (?, ?) 
            ON CONFLICT(session_id) DO UPDATE SET state = excluded.state
        ''', (session_id, json.dumps(state)))

def load_session(session_id: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.execute('SELECT state FROM sessions WHERE session_id = ?', (session_id,))
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return None

# Ensure the table is created upon module import
init_db()
