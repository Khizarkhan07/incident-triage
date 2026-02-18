"""Incident history storage and retrieval."""

import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from src.models import TriageResult
from src.utils.logger import get_logger

logger = get_logger(__name__)


class IncidentStore:
    """Manages incident triage history storage."""
    
    def __init__(self, db_path: str = "data/vector_store.db"):
        self.db_path = db_path
        self._init_db()
        logger.info(f"Initialized IncidentStore at: {db_path}")
    
    def _init_db(self):
        """Initialize incident history table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incident_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT NOT NULL UNIQUE,
                timestamp TEXT NOT NULL,
                alert_name TEXT NOT NULL,
                severity TEXT NOT NULL,
                category TEXT NOT NULL,
                root_causes TEXT,
                mitigation_plan TEXT,
                relevant_runbooks TEXT,
                processing_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_incident_id 
            ON incident_history(incident_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON incident_history(timestamp DESC)
        """)
        
        conn.commit()
        conn.close()
        logger.info("Incident history table initialized")
    
    def save_incident(
        self,
        result: TriageResult,
        alert_name: str
    ):
        """Save a triaged incident to history."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert lists/dicts to JSON strings
            root_causes_json = json.dumps(result.root_causes)
            mitigation_plan_json = json.dumps(result.mitigation_plan)
            runbooks_json = json.dumps([
                {
                    "title": rb["title"],
                    "file_path": rb["file_path"],
                    "similarity": rb["similarity"]
                }
                for rb in result.relevant_runbooks
            ])
            
            cursor.execute("""
                INSERT OR REPLACE INTO incident_history 
                (incident_id, timestamp, alert_name, severity, category, 
                 root_causes, mitigation_plan, relevant_runbooks, processing_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.incident_id,
                result.timestamp,
                alert_name,
                result.severity,
                result.category,
                root_causes_json,
                mitigation_plan_json,
                runbooks_json,
                result.processing_time
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Saved incident to history: {result.incident_id}")
            
        except Exception as e:
            logger.error(f"Error saving incident to history: {e}")
            raise
    
    def get_all_incidents(self, limit: int = 50) -> List[Dict]:
        """Get all incidents from history, most recent first."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT incident_id, timestamp, alert_name, severity, category,
                       root_causes, mitigation_plan, relevant_runbooks, 
                       processing_time, created_at
                FROM incident_history
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            incidents = []
            for row in cursor.fetchall():
                incidents.append({
                    "incident_id": row[0],
                    "timestamp": row[1],
                    "alert_name": row[2],
                    "severity": row[3],
                    "category": row[4],
                    "root_causes": json.loads(row[5]) if row[5] else [],
                    "mitigation_plan": json.loads(row[6]) if row[6] else {},
                    "relevant_runbooks": json.loads(row[7]) if row[7] else [],
                    "processing_time": row[8],
                    "created_at": row[9]
                })
            
            conn.close()
            return incidents
            
        except Exception as e:
            logger.error(f"Error retrieving incidents: {e}")
            return []
    
    def get_incident_by_id(self, incident_id: str) -> Optional[Dict]:
        """Get a specific incident by ID."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT incident_id, timestamp, alert_name, severity, category,
                       root_causes, mitigation_plan, relevant_runbooks, 
                       processing_time, created_at
                FROM incident_history
                WHERE incident_id = ?
            """, (incident_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "incident_id": row[0],
                    "timestamp": row[1],
                    "alert_name": row[2],
                    "severity": row[3],
                    "category": row[4],
                    "root_causes": json.loads(row[5]) if row[5] else [],
                    "mitigation_plan": json.loads(row[6]) if row[6] else {},
                    "relevant_runbooks": json.loads(row[7]) if row[7] else [],
                    "processing_time": row[8],
                    "created_at": row[9]
                }
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving incident {incident_id}: {e}")
            return None
    
    def search_incidents(
        self,
        severity: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Search incidents by severity and/or category."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = """
                SELECT incident_id, timestamp, alert_name, severity, category,
                       root_causes, mitigation_plan, relevant_runbooks, 
                       processing_time, created_at
                FROM incident_history
                WHERE 1=1
            """
            params = []
            
            if severity:
                query += " AND severity = ?"
                params.append(severity)
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            
            incidents = []
            for row in cursor.fetchall():
                incidents.append({
                    "incident_id": row[0],
                    "timestamp": row[1],
                    "alert_name": row[2],
                    "severity": row[3],
                    "category": row[4],
                    "root_causes": json.loads(row[5]) if row[5] else [],
                    "mitigation_plan": json.loads(row[6]) if row[6] else {},
                    "relevant_runbooks": json.loads(row[7]) if row[7] else [],
                    "processing_time": row[8],
                    "created_at": row[9]
                })
            
            conn.close()
            return incidents
            
        except Exception as e:
            logger.error(f"Error searching incidents: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get statistics about stored incidents."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total incidents
            cursor.execute("SELECT COUNT(*) FROM incident_history")
            total = cursor.fetchone()[0]
            
            # By severity
            cursor.execute("""
                SELECT severity, COUNT(*) 
                FROM incident_history 
                GROUP BY severity
            """)
            by_severity = dict(cursor.fetchall())
            
            # By category
            cursor.execute("""
                SELECT category, COUNT(*) 
                FROM incident_history 
                GROUP BY category
            """)
            by_category = dict(cursor.fetchall())
            
            # Avg processing time
            cursor.execute("SELECT AVG(processing_time) FROM incident_history")
            avg_time = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                "total_incidents": total,
                "by_severity": by_severity,
                "by_category": by_category,
                "avg_processing_time": f"{avg_time:.2f}s"
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
