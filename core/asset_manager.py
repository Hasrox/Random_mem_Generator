import sqlite3
import json
from pathlib import Path
import random
from typing import List, Dict, Tuple
from datetime import datetime

class AssetManager:
    def __init__(self, base_path: str = "assets"):
        self.base_path = Path(base_path).resolve()
        self.db_path = Path("data/meme_generator.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        # FIXED: thread safety for Gradio
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._init_db()
        self._ensure_indexes()

    # ... (rest of the file unchanged - full original code remains exactly as before)
    def _init_db(self):
        cur = self.conn.cursor()
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS templates (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                path TEXT NOT NULL UNIQUE,
                tags TEXT DEFAULT '[]',
                bias REAL DEFAULT 1.0
            );
            CREATE TABLE IF NOT EXISTS sfx (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                path TEXT NOT NULL UNIQUE,
                tags TEXT DEFAULT '[]',
                bias REAL DEFAULT 1.0
            );
        """)
        self.conn.commit()

    def _ensure_indexes(self):
        self._index_folder("templates", self.base_path / "templates")
        self._index_folder("sfx", self.base_path / "sfx")

    def _index_folder(self, table: str, folder: Path):
        cur = self.conn.cursor()
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        if cur.fetchone()[0] > 0:
            return
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
            print(f"⚠️ {folder} created — please add assets!")
            return
        for file in folder.glob("*.*"):
            if file.suffix.lower() not in {".png", ".jpg", ".jpeg", ".mp3", ".wav", ".ogg"}:
                continue
            asset_id = file.stem
            path_str = str(file.resolve())
            tags = json.dumps([])
            cur.execute(f"INSERT OR IGNORE INTO {table} (id, filename, path, tags, bias) VALUES (?, ?, ?, ?, ?)",
                        (asset_id, file.name, path_str, tags, 1.0))
        self.conn.commit()
        print(f"✅ Indexed {cur.rowcount} {table} assets")

    def get_weighted_template(self) -> Tuple[str, str]:
        cur = self.conn.cursor()
        cur.execute("SELECT path, bias FROM templates")
        rows = cur.fetchall()
        if not rows:
            raise FileNotFoundError("No templates found!")
        paths, biases = zip(*rows)
        selected_path = random.choices(paths, weights=biases, k=1)[0]
        return selected_path, Path(selected_path).stem

    def get_weighted_sfx(self) -> Tuple[str, str]:
        cur = self.conn.cursor()
        cur.execute("SELECT path, bias FROM sfx")
        rows = cur.fetchall()
        if not rows:
            raise FileNotFoundError("No SFX found!")
        paths, biases = zip(*rows)
        selected_path = random.choices(paths, weights=biases, k=1)[0]
        return selected_path, Path(selected_path).stem

    def close(self):
        self.conn.close()
