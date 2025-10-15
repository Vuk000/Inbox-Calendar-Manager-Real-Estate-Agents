"""
Mock responses for Pinecone vector store
"""
from typing import Dict, Any, List


class MockPineconeIndex:
    """Mock Pinecone index"""
    
    def __init__(self, name: str):
        self.name = name
        self._vectors = {}
    
    def upsert(self, vectors: List[tuple], namespace: str = ""):
        """Mock upsert operation"""
        for vec_id, embedding, metadata in vectors:
            self._vectors[vec_id] = {
                "id": vec_id,
                "values": embedding,
                "metadata": metadata
            }
        return {"upserted_count": len(vectors)}
    
    def query(
        self,
        vector: List[float],
        top_k: int = 10,
        namespace: str = "",
        include_metadata: bool = True,
        filter: Dict = None
    ) -> Dict[str, Any]:
        """Mock query operation"""
        return {
            "matches": [
                {
                    "id": "email_1",
                    "score": 0.95,
                    "metadata": {
                        "subject": "Property Inquiry",
                        "sender": "client@example.com",
                        "category": "lead"
                    }
                },
                {
                    "id": "email_2",
                    "score": 0.87,
                    "metadata": {
                        "subject": "Offer Submission",
                        "sender": "buyer@example.com",
                        "category": "offer"
                    }
                }
            ],
            "namespace": namespace
        }
    
    def delete(self, ids: List[str] = None, delete_all: bool = False, namespace: str = ""):
        """Mock delete operation"""
        if delete_all:
            self._vectors.clear()
        elif ids:
            for vec_id in ids:
                self._vectors.pop(vec_id, None)
        return {}
    
    def describe_index_stats(self) -> Dict[str, Any]:
        """Mock index stats"""
        return {
            "dimension": 1536,
            "index_fullness": 0.1,
            "total_vector_count": len(self._vectors),
            "namespaces": {"": {"vector_count": len(self._vectors)}}
        }


class MockPinecone:
    """Mock Pinecone client"""
    
    def __init__(self):
        self._indexes = {}
    
    def Index(self, name: str) -> MockPineconeIndex:
        """Get or create mock index"""
        if name not in self._indexes:
            self._indexes[name] = MockPineconeIndex(name)
        return self._indexes[name]
    
    def list_indexes(self) -> List[str]:
        """List mock indexes"""
        return list(self._indexes.keys())
    
    def create_index(self, name: str, dimension: int, metric: str = "cosine"):
        """Mock create index"""
        self._indexes[name] = MockPineconeIndex(name)
        return {"name": name, "dimension": dimension}
    
    def delete_index(self, name: str):
        """Mock delete index"""
        self._indexes.pop(name, None)

