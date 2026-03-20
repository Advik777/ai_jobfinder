import sqlite3, json, os

DB_PATH = "internship.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS resumes (
                id TEXT PRIMARY KEY,
                text TEXT,
                skills TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id TEXT,
                title TEXT,
                company TEXT,
                location TEXT,
                description TEXT,
                url TEXT,
                match_score REAL,
                matched_skills TEXT,
                missing_skills TEXT
            );
            CREATE TABLE IF NOT EXISTS roadmap (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id TEXT,
                job_title TEXT,
                company TEXT,
                job_description TEXT,
                job_url TEXT,
                roadmap_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

def save_resume(resume_id: str, text: str, skills: list):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO resumes (id, text, skills) VALUES (?,?,?)",
            (resume_id, text, json.dumps(skills))
        )

def get_resume(resume_id: str):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM resumes WHERE id=?", (resume_id,)
        ).fetchone()
        if row:
            return dict(row)
    return None

def save_roadmap(resume_id: str, job_title: str, company: str,
                 job_description: str, job_url: str, roadmap_json: dict):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO roadmap 
               (resume_id, job_title, company, job_description, job_url, roadmap_json)
               VALUES (?,?,?,?,?,?)""",
            (resume_id, job_title, company, job_description,
             job_url, json.dumps(roadmap_json))
        )

def get_roadmaps(resume_id: str) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM roadmap WHERE resume_id=? ORDER BY created_at DESC",
            (resume_id,)
        ).fetchall()
        return [dict(r) for r in rows]

def delete_roadmap(roadmap_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM roadmap WHERE id=?", (roadmap_id,))