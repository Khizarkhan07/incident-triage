"""Ollama LLM client for local inference."""

import ollama
from typing import List, Dict, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class OllamaClient:
    """Client for interacting with Ollama LLM."""
    
    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.1,
        max_tokens: int = 2048
    ):
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = ollama.Client(host=base_url)
        logger.info(f"Initialized Ollama client with model: {model}")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate text completion from prompt."""
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            response = self.client.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": temperature or self.temperature,
                    "num_predict": max_tokens or self.max_tokens
                }
            )
            
            return response['message']['content']
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Multi-turn chat conversation."""
        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": temperature or self.temperature,
                    "num_predict": max_tokens or self.max_tokens
                }
            )
            
            return response['message']['content']
        
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            raise
    
    def embed(self, text: str) -> List[float]:
        """Generate embeddings for text (if model supports it)."""
        try:
            response = self.client.embeddings(
                model=self.model,
                prompt=text
            )
            return response['embedding']
        except Exception as e:
            logger.warning(f"Embedding failed with Ollama model, will use sentence-transformers: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            models = self.client.list()
            available_models = [m['name'] for m in models.get('models', [])]
            return any(self.model in m for m in available_models)
        except Exception as e:
            logger.error(f"Ollama not available: {e}")
            return False
    
    def pull_model(self):
        """Pull the model if not already available."""
        try:
            logger.info(f"Pulling model: {self.model}")
            self.client.pull(self.model)
            logger.info(f"Model {self.model} pulled successfully")
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            raise
