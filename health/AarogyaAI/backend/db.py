"""
db.py
Lightweight sqlite3 data-access layer. No ORM, so the schema in
database/schema.sql is the single source of truth for table shape.
"""
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "aarogyaai.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")


def get_connection():
    """Return a new sqlite3 connection with dict-like row access and FKs on."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create the database file and all tables if they don't already exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(SCHEMA_PATH, "r") as f:
        schema = f.read()
    conn = get_connection()
    try:
        conn.executescript(schema)
        conn.commit()
    finally:
        conn.close()


def query_one(sql, params=()):
    conn = get_connection()
    try:
        row = conn.execute(sql, params).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def query_all(sql, params=()):
    conn = get_connection()
    try:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def execute(sql, params=()):
    """Run an INSERT/UPDATE/DELETE. Returns (lastrowid, rowcount)."""
    conn = get_connection()
    try:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid, cur.rowcount
    finally:
        conn.close()
