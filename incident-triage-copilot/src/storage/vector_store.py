"""Vector store using SQLite with sqlite-vec extension."""

import sqlite3
import json
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer
from src.utils.logger import get_logger

logger = get_logger(__name__)


class VectorStore:
    """SQLite-based vector store for runbook embeddings."""
    
    def __init__(
        self,
        db_path: str = "data/vector_store.db",
        embedding_model: str = "all-MiniLM-L6-v2",
        dimension: int = 384
    ):
        self.db_path = db_path
        self.dimension = dimension
        self.embedding_model = SentenceTransformer(embedding_model)
        self._init_db()
        logger.info(f"Initialized VectorStore with model: {embedding_model}")
    
    def _init_db(self):
        """Initialize SQLite database with vector extension."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create runbooks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS runbooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                file_path TEXT NOT NULL UNIQUE,
                content TEXT NOT NULL,
                category TEXT,
                embedding BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster searches
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category ON runbooks(category)
        """)
        
        conn.commit()
        conn.close()
        logger.info("Database initialized")
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text."""
        embedding = self.embedding_model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    def add_runbook(
        self,
        title: str,
        file_path: str,
        content: str,
        category: Optional[str] = None
    ):
        """Add a runbook to the vector store."""
        try:
            # Generate embedding
            embedding = self.embed_text(content)
            embedding_blob = json.dumps(embedding).encode('utf-8')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO runbooks (title, file_path, content, category, embedding)
                VALUES (?, ?, ?, ?, ?)
            """, (title, file_path, content, category, embedding_blob))
            
            conn.commit()
            conn.close()
            logger.info(f"Added runbook: {title}")
        
        except Exception as e:
            logger.error(f"Error adding runbook {title}: {e}")
            raise
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None
    ) -> List[Dict]:
        """Search for relevant runbooks using cosine similarity."""
        try:
            # Generate query embedding
            query_embedding = self.embed_text(query)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Fetch all runbooks (with optional category filter)
            if category:
                cursor.execute("""
                    SELECT id, title, file_path, content, category, embedding
                    FROM runbooks
                    WHERE category = ?
                """, (category,))
            else:
                cursor.execute("""
                    SELECT id, title, file_path, content, category, embedding
                    FROM runbooks
                """)
            
            results = []
            for row in cursor.fetchall():
                runbook_id, title, file_path, content, cat, embedding_blob = row
                
                # Deserialize embedding
                stored_embedding = json.loads(embedding_blob.decode('utf-8'))
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_embedding, stored_embedding)
                
                results.append({
                    "id": runbook_id,
                    "title": title,
                    "file_path": file_path,
                    "content": content,
                    "category": cat,
                    "similarity": similarity
                })
            
            conn.close()
            
            # Sort by similarity and return top_k
            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:top_k]
        
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            raise
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def get_all_runbooks(self) -> List[Dict]:
        """Get all runbooks from the store."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, file_path, content, category
            FROM runbooks
        """)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "title": row[1],
                "file_path": row[2],
                "content": row[3],
                "category": row[4]
            })
        
        conn.close()
        return results
    
    def delete_runbook(self, file_path: str):
        """Delete a runbook by file path."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM runbooks WHERE file_path = ?", (file_path,))
        
        conn.commit()
        conn.close()
        logger.info(f"Deleted runbook: {file_path}")
    
    def clear_all(self):
        """Clear all runbooks from the store."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM runbooks")
        
        conn.commit()
        conn.close()
        logger.info("Cleared all runbooks")
