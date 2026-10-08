"""SQLite schema and repository-style operations."""
from __future__ import annotations
import sqlite3
from pathlib import Path
class Database:
    def __init__(self,path:Path|None=None): self.path=path or Path(__file__).resolve().parents[1]/"traffic.db"; self.initialize()
    def connect(self):
        con=sqlite3.connect(self.path); con.row_factory=sqlite3.Row; return con
    def initialize(self):
        with self.connect() as c:
            c.executescript('''CREATE TABLE IF NOT EXISTS cameras (id TEXT PRIMARY KEY,name TEXT,source TEXT,status TEXT);
            CREATE TABLE IF NOT EXISTS vehicles (plate_number TEXT PRIMARY KEY,updated_at TEXT);
            CREATE TABLE IF NOT EXISTS violations (id TEXT PRIMARY KEY,vehicle_track_id INTEGER,plate_number TEXT,violation_type TEXT,camera_id TEXT,timestamp TEXT,duration REAL,vehicle_type TEXT,vehicle_confidence REAL,plate_confidence REAL,evidence_path TEXT,status TEXT,reviewed_by TEXT,reviewed_at TEXT,note TEXT);
            CREATE TABLE IF NOT EXISTS evidence (id INTEGER PRIMARY KEY,violation_id TEXT,path TEXT,metadata TEXT);
            CREATE TABLE IF NOT EXISTS zones (id TEXT PRIMARY KEY,camera_id TEXT,zone_type TEXT,definition TEXT);
            CREATE TABLE IF NOT EXISTS system_events (id INTEGER PRIMARY KEY,timestamp TEXT,level TEXT,message TEXT);''')
    def add_violation(self,item:dict):
        keys=','.join(item); values=','.join('?' for _ in item)
        with self.connect() as c: c.execute(f'INSERT INTO violations ({keys}) VALUES ({values})',tuple(item.values()))
    def list_violations(self):
        with self.connect() as c:return [dict(r) for r in c.execute('SELECT * FROM violations ORDER BY timestamp DESC')]
    def get_violation(self,vid):
        with self.connect() as c:
            r=c.execute('SELECT * FROM violations WHERE id=?',(vid,)).fetchone(); return dict(r) if r else None
    def review(self,vid,status,note=None):
        with self.connect() as c:c.execute('UPDATE violations SET status=?,note=?,reviewed_at=datetime("now") WHERE id=?',(status,note,vid))
    def statistics(self):
        with self.connect() as c:return dict(c.execute("SELECT count(*) total, sum(status='PENDING_REVIEW') pending, sum(status='CONFIRMED') confirmed FROM violations").fetchone())
