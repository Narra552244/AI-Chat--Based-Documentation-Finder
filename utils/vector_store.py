import os
import numpy as np
import faiss
import pickle
from typing import List, Dict, Tuple

class VectorStore:
    def __init__(self, index_dir: str = "data/index"):
        self.index_dir = index_dir
        self.index_path = os.path.join(index_dir, "faiss_index.idx")
        self.metadata_path = os.path.join(index_dir, "metadata.pkl")
        self.load_or_create_index()

    def load_or_create_index(self):
        """Load existing index or create a new one."""
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            self.index = None
            self.metadata = {
                'chunks': [],
                'file_info': []
            }

    def add_document(self, doc_data: Dict):
        """Add document embeddings to the index."""
        embeddings = np.array(doc_data['embeddings']).astype('float32')
        if self.index is None:
            self.index = faiss.IndexFlatL2(embeddings.shape[1])
        
        self.index.add(embeddings)
        start_idx = len(self.metadata['chunks'])
        
        self.metadata['chunks'].extend(doc_data['chunks'])
        self.metadata['file_info'].append({
            **doc_data['metadata'],
            'start_idx': start_idx,
            'end_idx': start_idx + len(doc_data['chunks'])
        })
        
        self.save_index()

    def search(self, query_embedding: List[float], k: int = 5) -> List[Tuple[str, float]]:
        """Search for similar documents."""
        if self.index is None:
            return []
        
        query_embedding = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx != -1:  # Valid index
                chunk = self.metadata['chunks'][idx]
                file_info = next(
                    (info for info in self.metadata['file_info'] 
                     if info['start_idx'] <= idx < info['end_idx']),
                    None
                )
                results.append({
                    'chunk': chunk,
                    'distance': float(distance),
                    'file_info': file_info
                })
        
        return results

    def save_index(self):
        """Save the index and metadata to disk."""
        os.makedirs(self.index_dir, exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)

    def get_stats(self) -> Dict:
        """Get statistics about the index."""
        return {
            'total_chunks': len(self.metadata['chunks']),
            'total_documents': len(self.metadata['file_info']),
            'documents': self.metadata['file_info']
        } 