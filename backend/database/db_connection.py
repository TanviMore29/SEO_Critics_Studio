"""
database/db_connection.py

Handles the SQLite connection and schema creation for SEO Critics Studio.
Tables: Websites, Pages, Images, Reports, ScanHistory

Also runs small idempotent migrations so existing database files pick up
new columns (e.g. advanced SEO signals, keyword insights, recommendations)
without needing to delete the database file.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "seo_critics.db")

# Columns added after the initial release. Each entry is applied with
# "ALTER TABLE ... ADD COLUMN" only if the column does not already exist.
PAGE_COLUMN_MIGRATIONS = [
    ("has_viewport", "BOOLEAN"),
    ("has_structured_data", "BOOLEAN"),
    ("has_open_graph", "BOOLEAN"),
    ("has_twitter_card", "BOOLEAN"),
    ("html_lang", "TEXT"),
    ("images_missing_dimensions", "INTEGER"),
    ("non_descriptive_images", "INTEGER"),
    ("top_keywords", "TEXT"),
    # --- Crawler / issue-explorer upgrade additions ---
    ("crawl_depth", "INTEGER"),
    ("redirect_count", "INTEGER"),
    ("redirect_chain", "TEXT"),
    ("is_indexable", "BOOLEAN"),
]

REPORT_COLUMN_MIGRATIONS = [
    ("recommendations_json", "TEXT"),
    ("keywords_json", "TEXT"),
    ("advanced_checks_json", "TEXT"),
    # --- Crawler / issue-explorer upgrade additions ---
    ("sitemap_urls_json", "TEXT"),
    ("robots_meta_json", "TEXT"),
    ("crawl_stats_json", "TEXT"),
    ("pdf_report_path", "TEXT"),
]


def get_connection():
    """Return a new SQLite connection with row factory set to dict-like rows."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _ensure_columns(cur, table: str, columns: list):
    cur.execute(f"PRAGMA table_info({table})")
    existing = {row[1] for row in cur.fetchall()}
    for column_name, column_type in columns:
        if column_name not in existing:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {column_name} {column_type}")


def init_db():
    """Create all required tables if they do not already exist, and apply
    any pending column migrations to existing tables."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Websites (
            website_id INTEGER PRIMARY KEY AUTOINCREMENT,
            root_url TEXT NOT NULL,
            domain_name TEXT NOT NULL,
            date_added DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Pages (
            page_id INTEGER PRIMARY KEY AUTOINCREMENT,
            website_id INTEGER NOT NULL,
            page_url TEXT NOT NULL,
            status_code INTEGER,
            title TEXT,
            meta_description TEXT,
            meta_robots TEXT,
            canonical_url TEXT,
            h1_count INTEGER,
            h2_count INTEGER,
            word_count INTEGER,
            internal_links INTEGER,
            external_links INTEGER,
            broken_links INTEGER,
            image_count INTEGER,
            images_missing_alt INTEGER,
            is_https BOOLEAN,
            page_size_kb REAL,
            response_time_ms INTEGER,
            page_score REAL,
            FOREIGN KEY (website_id) REFERENCES Websites(website_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Images (
            image_id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_id INTEGER NOT NULL,
            image_url TEXT,
            alt_text TEXT,
            has_alt BOOLEAN DEFAULT 0,
            FOREIGN KEY (page_id) REFERENCES Pages(page_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Reports (
            report_id INTEGER PRIMARY KEY AUTOINCREMENT,
            website_id INTEGER NOT NULL,
            overall_score REAL,
            health_level TEXT,
            metadata_score REAL,
            technical_score REAL,
            images_score REAL,
            links_score REAL,
            sitemap_score REAL,
            robots_score REAL,
            performance_score REAL,
            generated_on DATETIME DEFAULT CURRENT_TIMESTAMP,
            html_report_path TEXT,
            csv_report_path TEXT,
            excel_report_path TEXT,
            FOREIGN KEY (website_id) REFERENCES Websites(website_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ScanHistory (
            scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            website_id INTEGER NOT NULL,
            scan_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            pages_scanned INTEGER,
            status TEXT,
            FOREIGN KEY (website_id) REFERENCES Websites(website_id)
        )
    """)

    # --- New tables added for the Issue Explorer / Link Graph upgrade ---
    # Reuses the existing Websites/Pages tables; these are purely additive
    # and do not touch or remove any pre-existing table or column.

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Issues (
            issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            website_id INTEGER NOT NULL,
            issue_type TEXT NOT NULL,
            category TEXT NOT NULL,
            severity TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            affected_url TEXT,
            affected_count INTEGER,
            recommendation TEXT,
            evidence_json TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (website_id) REFERENCES Websites(website_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS PageLinks (
            link_id INTEGER PRIMARY KEY AUTOINCREMENT,
            website_id INTEGER NOT NULL,
            source_url TEXT NOT NULL,
            target_url TEXT NOT NULL,
            is_broken BOOLEAN DEFAULT 0,
            FOREIGN KEY (website_id) REFERENCES Websites(website_id)
        )
    """)

    _ensure_columns(cur, "Pages", PAGE_COLUMN_MIGRATIONS)
    _ensure_columns(cur, "Reports", REPORT_COLUMN_MIGRATIONS)

    # Helpful indexes for the new lookup-heavy queries (issue filtering,
    # link-graph edge lookups). CREATE INDEX IF NOT EXISTS is idempotent.
    cur.execute("CREATE INDEX IF NOT EXISTS idx_issues_website ON Issues(website_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_issues_severity ON Issues(severity)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pagelinks_website ON PageLinks(website_id)")

    conn.commit()
    conn.close()
