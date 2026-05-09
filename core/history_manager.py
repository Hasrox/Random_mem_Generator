import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict

class HistoryManager:
    def __init__(self):
        self.db_path = Path("data/meme_generator.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure data/ folder exists
        self.conn = sqlite3.connect(str(self.db_path))
        self._init_history_table()

    def _init_history_table(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                template_id TEXT,
                sfx_id TEXT,
                context TEXT,
                top_text TEXT,
                bottom_text TEXT,
                feedback REAL DEFAULT NULL
            )
        """)
        self.conn.commit()

    def record_generation(self, template_id: str, sfx_id: str, context: str, top: str, bottom: str):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO history (timestamp, template_id, sfx_id, context, top_text, bottom_text)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(), template_id, sfx_id, context, top, bottom))
        self.conn.commit()

    def get_recent_history(self, limit: int = 5) -> List[Dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM history ORDER BY timestamp DESC LIMIT ?", (limit,))
        columns = [col[0] for col in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

    def close(self):
        self.conn.close()