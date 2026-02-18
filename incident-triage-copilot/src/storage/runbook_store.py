"""Runbook storage and retrieval."""

import os
from pathlib import Path
from typing import List, Dict, Optional
from src.storage.vector_store import VectorStore
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RunbookStore:
    """Manages runbook storage and retrieval."""
    
    def __init__(
        self,
        runbooks_dir: str = "data/runbooks",
        vector_store: Optional[VectorStore] = None
    ):
        self.runbooks_dir = Path(runbooks_dir)
        self.vector_store = vector_store or VectorStore()
        logger.info(f"Initialized RunbookStore from: {runbooks_dir}")
    
    def index_runbooks(self):
        """Index all runbooks from the runbooks directory."""
        if not self.runbooks_dir.exists():
            logger.warning(f"Runbooks directory not found: {self.runbooks_dir}")
            return
        
        # Clear existing runbooks
        self.vector_store.clear_all()
        
        # Index all markdown files
        runbook_files = list(self.runbooks_dir.glob("*.md"))
        logger.info(f"Found {len(runbook_files)} runbooks to index")
        
        for file_path in runbook_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract title from first line (assuming # Title format)
                lines = content.split('\n')
                title = lines[0].replace('#', '').strip() if lines else file_path.stem
                
                # Infer category from filename or content
                category = self._infer_category(file_path.stem, content)
                
                # Add to vector store
                self.vector_store.add_runbook(
                    title=title,
                    file_path=str(file_path),
                    content=content,
                    category=category
                )
                
                logger.info(f"Indexed: {title}")
            
            except Exception as e:
                logger.error(f"Error indexing {file_path}: {e}")
        
        logger.info(f"Successfully indexed {len(runbook_files)} runbooks")
    
    def _infer_category(self, filename: str, content: str) -> str:
        """Infer category from filename or content."""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        # Category mappings
        categories = {
            "Database": ["db", "database", "postgres", "mysql", "sql"],
            "API/Service": ["api", "service", "gateway", "rest", "http"],
            "Infrastructure": ["infra", "kubernetes", "k8s", "docker", "aws"],
            "Network": ["network", "dns", "firewall", "load balancer"],
            "Performance": ["performance", "latency", "slow", "timeout"],
            "Data Pipeline": ["kafka", "pipeline", "stream", "queue", "consumer"],
            "Security": ["security", "auth", "ssl", "certificate"]
        }
        
        for category, keywords in categories.items():
            if any(kw in filename_lower or kw in content_lower for kw in keywords):
                return category
        
        return "General"
    
    def search_runbooks(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None
    ) -> List[Dict]:
        """Search for relevant runbooks."""
        return self.vector_store.search(query, top_k=top_k, category=category)
    
    def get_runbook_by_path(self, file_path: str) -> Optional[str]:
        """Get runbook content by file path."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading runbook {file_path}: {e}")
            return None
    
    def list_all_runbooks(self) -> List[Dict]:
        """List all indexed runbooks."""
        return self.vector_store.get_all_runbooks()
