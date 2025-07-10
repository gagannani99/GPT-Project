import os
from sentence_transformers import SentenceTransformer
import chromadb

chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection("alliance_docs")

# Updated model for better semantic similarity
embedding_model = SentenceTransformer("all-MiniLM-L12-v2")

def get_context(question, top_k=3):  # Increased from 1 to 3
    question_emb = embedding_model.encode(question).tolist()
    results = collection.query(query_embeddings=[question_emb], n_results=top_k)

    docs = results['documents'][0] if results['documents'] else []
    
    print("\n🔍 Retrieved Context Chunks:")
    for i, doc in enumerate(docs):
        print(f"Chunk {i+1}: {doc[:200]}...\n")

    return "\n---\n".join(docs)
