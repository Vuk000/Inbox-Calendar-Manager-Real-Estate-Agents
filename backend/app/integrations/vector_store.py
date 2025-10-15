"""
Vector Store Integration - Pinecone for semantic email search
"""
from typing import List, Dict, Any, Optional
import pinecone
from pinecone import Pinecone, ServerlessSpec
import hashlib
from datetime import datetime

from ..config import settings


class VectorStore:
    """
    Pinecone vector database integration for semantic email search.
    Stores email embeddings for similarity search.
    """
    
    def __init__(self):
        self.api_key = settings.PINECONE_API_KEY
        self.environment = settings.PINECONE_ENVIRONMENT
        self.index_name = settings.PINECONE_INDEX_NAME
        self.dimension = 1536  # For OpenAI embeddings (can adjust for Claude if needed)
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.api_key)
        
        # Create index if not exists
        self._ensure_index_exists()
        
        # Get index
        self.index = self.pc.Index(self.index_name)
    
    def _ensure_index_exists(self):
        """Create Pinecone index if it doesn't exist"""
        try:
            # List existing indexes
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                # Create new index
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=self.environment
                    )
                )
                print(f"✅ Created Pinecone index: {self.index_name}")
        except Exception as e:
            print(f"⚠️ Pinecone index setup: {e}")
    
    def _generate_vector_id(self, message_id: str, user_id: int) -> str:
        """Generate unique vector ID"""
        return hashlib.sha256(f"{user_id}:{message_id}".encode()).hexdigest()[:32]
    
    async def upsert_email(
        self,
        message_id: str,
        user_id: int,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Store email embedding in vector database.
        
        Args:
            message_id: Email message ID
            user_id: User ID (for multi-tenancy)
            embedding: Vector embedding (1536 dimensions)
            metadata: Email metadata (subject, sender, category, etc.)
            
        Returns:
            Upsert result
        """
        try:
            vector_id = self._generate_vector_id(message_id, user_id)
            
            # Add user_id to metadata for filtering
            metadata["user_id"] = user_id
            metadata["message_id"] = message_id
            metadata["indexed_at"] = datetime.utcnow().isoformat()
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[(vector_id, embedding, metadata)],
                namespace=f"user_{user_id}"  # Multi-tenancy
            )
            
            return {
                "success": True,
                "vector_id": vector_id,
                "message_id": message_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def search_similar_emails(
        self,
        query_embedding: List[float],
        user_id: int,
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for similar emails using semantic search.
        
        Args:
            query_embedding: Query vector embedding
            user_id: User ID for filtering
            top_k: Number of results to return
            filter_metadata: Optional metadata filters (e.g., {"category": "lead"})
            
        Returns:
            List of similar emails with scores
        """
        try:
            # Build filter
            filter_dict = {"user_id": user_id}
            if filter_metadata:
                filter_dict.update(filter_metadata)
            
            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                namespace=f"user_{user_id}",
                filter=filter_dict
            )
            
            # Format results
            matches = []
            for match in results.get("matches", []):
                matches.append({
                    "message_id": match.metadata.get("message_id"),
                    "score": match.score,
                    "subject": match.metadata.get("subject"),
                    "sender": match.metadata.get("sender"),
                    "category": match.metadata.get("category"),
                    "priority": match.metadata.get("priority"),
                    "date": match.metadata.get("date"),
                    "metadata": match.metadata
                })
            
            return {
                "success": True,
                "matches": matches,
                "count": len(matches)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "matches": []
            }
    
    async def delete_email(
        self,
        message_id: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Delete email embedding from vector store.
        
        Args:
            message_id: Email message ID
            user_id: User ID
            
        Returns:
            Delete result
        """
        try:
            vector_id = self._generate_vector_id(message_id, user_id)
            
            self.index.delete(
                ids=[vector_id],
                namespace=f"user_{user_id}"
            )
            
            return {
                "success": True,
                "deleted": vector_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get statistics for user's vectors.
        
        Args:
            user_id: User ID
            
        Returns:
            Statistics
        """
        try:
            stats = self.index.describe_index_stats()
            
            user_namespace = f"user_{user_id}"
            user_stats = stats.get("namespaces", {}).get(user_namespace, {})
            
            return {
                "success": True,
                "total_vectors": user_stats.get("vector_count", 0),
                "dimension": stats.get("dimension"),
                "index_fullness": stats.get("index_fullness", 0)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

