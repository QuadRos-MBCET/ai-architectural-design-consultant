import os
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

# Singleton instance to hold the vector store
_vector_store = None

def get_vector_store():
    global _vector_store
    if _vector_store is not None:
        return _vector_store
        
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    faiss_path = os.path.join(base_dir, "data", "faiss_index")
    
    if not os.path.exists(faiss_path):
        print(f"Warning: FAISS index not found at {faiss_path}. Please run rag/ingest.py first.")
        return None
        
    print("Initializing Ollama Embedding Model...")
    embeddings = OllamaEmbeddings(model="llama3.1")
    
    # Allow dangerous deserialization because we created this index locally
    _vector_store = FAISS.load_local(faiss_path, embeddings, allow_dangerous_deserialization=True)
    return _vector_store

def retrieve_context(query: str, k: int = 3) -> str:
    """
    Retrieves the top k most similar chunks from the FAISS index based on the query.
    Returns a concatenated string of the chunk contents.
    """
    vs = get_vector_store()
    if vs is None:
        return "No architectural context could be retrieved (FAISS index missing)."
        
    docs = vs.similarity_search(query, k=k)
    
    context_str = ""
    for i, doc in enumerate(docs):
        # We can also extract metadata like page source here if needed
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "?")
        source_name = os.path.basename(source)
        
        context_str += f"[Source: {source_name}, Page {page}]\n"
        context_str += f"{doc.page_content}\n\n"
        
    return context_str.strip()
