import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class DBHandler:
    def __init__(self, db_path: str = "data/docfinder.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create documents table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
        """)

        # Create queries table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            response TEXT,
            relevant_docs TEXT
        )
        """)

        conn.commit()
        conn.close()

    def log_document(self, filename: str, file_type: str, metadata: Dict) -> int:
        """Log a new document upload."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO documents (filename, file_type, metadata) VALUES (?, ?, ?)",
            (filename, file_type, json.dumps(metadata))
        )

        doc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return doc_id

    def log_query(self, query: str, response: str, relevant_docs: List[Dict]) -> int:
        """Log a query and its response."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO queries (query, response, relevant_docs) VALUES (?, ?, ?)",
            (query, response, json.dumps(relevant_docs))
        )

        query_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return query_id

    def get_document_history(self) -> List[Dict]:
        """Get history of document uploads."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT id, filename, file_type, upload_timestamp, metadata
        FROM documents
        ORDER BY upload_timestamp DESC
        """)

        documents = []
        for row in cursor.fetchall():
            documents.append({
                'id': row[0],
                'filename': row[1],
                'file_type': row[2],
                'upload_timestamp': row[3],
                'metadata': json.loads(row[4])
            })

        conn.close()
        return documents

    def get_query_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get history of queries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
        SELECT id, query, timestamp, response, relevant_docs
        FROM queries
        ORDER BY timestamp DESC
        """
        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query)

        queries = []
        for row in cursor.fetchall():
            queries.append({
                'id': row[0],
                'query': row[1],
                'timestamp': row[2],
                'response': row[3],
                'relevant_docs': json.loads(row[4])
            })

        conn.close()
        return queries

    def get_query_stats(self) -> Dict:
        """Get statistics about queries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        # Total queries
        cursor.execute("SELECT COUNT(*) FROM queries")
        stats['total_queries'] = cursor.fetchone()[0]

        # Queries in last 24 hours
        cursor.execute("""
        SELECT COUNT(*) FROM queries
        WHERE timestamp > datetime('now', '-1 day')
        """)
        stats['queries_last_24h'] = cursor.fetchone()[0]

        # Total documents
        cursor.execute("SELECT COUNT(*) FROM documents")
        stats['total_documents'] = cursor.fetchone()[0]

        conn.close()
        return stats 