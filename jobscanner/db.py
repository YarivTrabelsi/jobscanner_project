# Placeholder for SQLite database schema and access

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import os


class JobDatabase:
    """SQLite database manager for job listings."""
    
    def __init__(self, db_path: str = "jobs.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create the jobs table with the specified schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    company TEXT,
                    location TEXT,
                    url TEXT UNIQUE,
                    posted_date TEXT,
                    description TEXT,
                    status TEXT DEFAULT 'new',
                    metadata_json TEXT DEFAULT '{}'
                )
            ''')
            conn.commit()
    
    def insert_job(self, job_data: Dict) -> Optional[int]:
        """
        Insert a new job listing into the database.
        
        Args:
            job_data: Dictionary containing job fields
        
        Returns:
            Job ID if inserted successfully, None if URL already exists
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    INSERT INTO jobs (title, company, location, url, posted_date, description, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    job_data.get('title', ''),
                    job_data.get('company', ''),
                    job_data.get('location', ''),
                    job_data.get('url', ''),
                    job_data.get('posted_date', ''),
                    job_data.get('description', ''),
                    json.dumps(job_data.get('metadata', {}))
                ))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            # URL already exists
            return None
    
    def get_jobs(self, status: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """
        Retrieve jobs from the database.
        
        Args:
            status: Filter by job status (e.g., 'new', 'processed')
            limit: Maximum number of jobs to return
        
        Returns:
            List of job dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            query = "SELECT * FROM jobs"
            params = []
            
            if status:
                query += " WHERE status = ?"
                params.append(status)
            
            query += " ORDER BY id DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def update_job_status(self, job_id: int, status: str) -> bool:
        """Update the status of a job."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "UPDATE jobs SET status = ? WHERE id = ?",
                (status, job_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def job_exists(self, url: str) -> bool:
        """Check if a job with the given URL already exists."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT 1 FROM jobs WHERE url = ?", (url,))
            return cursor.fetchone() is not None
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'new' THEN 1 END) as new,
                    COUNT(CASE WHEN status = 'processed' THEN 1 END) as processed
                FROM jobs
            ''')
            row = cursor.fetchone()
            return {
                'total': row[0],
                'new': row[1],
                'processed': row[2]
            }
