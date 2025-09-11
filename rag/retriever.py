import faiss
import numpy as np
import os
from sentence_transformers import SentenceTransformer
import json

# Load FAISS index
index_path = os.path.join(os.path.dirname(__file__), "rag_data", "rag_data_index.faiss")
index = faiss.read_index(index_path)

# Load chunk metadata
chunk_file = os.path.join(os.path.dirname(__file__), "rag_data", "chunk_metadata.json")
with open(chunk_file, "r", encoding="utf-8") as f:
    chunk_metadata = json.load(f)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Function to retrieve top-k similar documents
def retrieve_similar(query, top_k=3):
    query_embedding = model.encode([query])
    distances, indices = index.search(np.array(query_embedding, dtype=np.float32), top_k)

    results = []
    for i in indices[0]:
        if 0 <= i < len(chunk_metadata):
            chunk_info = chunk_metadata[i]
            source = chunk_info.get("source", "Unknown source")
            text = chunk_info.get("text", "No text available.")
            results.append(f"Source: {source}\nText: {text}")

    return "\n\n".join(results)

if __name__ == "__main__":
    print("✅ FAISS retriever is ready!")
    query = "What is internet marketing success?"
    print(f"Query: {query}")
    print(retrieve_similar(query, top_k=3))