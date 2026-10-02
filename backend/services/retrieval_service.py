import os
import json

# Singleton instance to hold the vector store
_vector_store = None

def get_vector_store():
    global _vector_store
    if _vector_store is not None:
        return _vector_store
        
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    faiss_path = os.path.join(base_dir, "data", "faiss_index")
    
    if not os.path.exists(faiss_path):
        return None
        
    try:
        from langchain_community.vectorstores import FAISS
        from langchain_ollama import OllamaEmbeddings
        embeddings = OllamaEmbeddings(model="llama3.1")
        _vector_store = FAISS.load_local(faiss_path, embeddings, allow_dangerous_deserialization=True)
        return _vector_store
    except Exception as e:
        print(f"FAISS Vector Store loading notice: {e}")
        return None

def retrieve_context(query: str, k: int = 3) -> str:
    """
    Retrieves top k similar chunks from FAISS index or returns structured architectural knowledge base fallback.
    """
    query_lower = query.lower()
    
    # 1. Try FAISS retrieval if available
    vs = get_vector_store()
    if vs is not None:
        try:
            docs = vs.similarity_search(query, k=k)
            context_str = ""
            for doc in docs:
                source = doc.metadata.get("source", "Unknown")
                page = doc.metadata.get("page", "?")
                source_name = os.path.basename(source)
                context_str += f"[Source: {source_name}, Page {page}]\n{doc.page_content}\n\n"
            if context_str.strip():
                return context_str.strip()
        except Exception as e:
            print(f"Similarity search notice: {e}")

    # 2. Structured Architectural Knowledge Base Fallback
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, "data", "typology_database.json")
    
    building_type = "library"
    if "hospital" in query_lower or "clinic" in query_lower: building_type = "hospital"
    elif "office" in query_lower: building_type = "office"
    elif "school" in query_lower or "educational" in query_lower: building_type = "school"
    elif "house" in query_lower or "villa" in query_lower: building_type = "house"

    if os.path.exists(db_path):
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                db = json.load(f)
            if building_type in db:
                info = db[building_type]
                desc = info.get("description", "Architectural facility design guidelines.")
                rules = ", ".join([f"{r['type']}: min {r.get('min_area_sqm', 15)}m²" for r in info.get("required_rooms", [])[:4]])
                return f"[Case Study & Standard Reference: {building_type.capitalize()} Typology]\n{desc}\nSpatial Program Requirements: {rules}"
        except Exception:
            pass

    return (
        "[Retrieved Case Study: High-Performance Educational & Commercial Architecture]\n"
        "Guidance recommends segregating quiet primary zones from service cores. "
        "Hot-humid climates require East-West longitudinal orientation, deep facade shading, and minimum 2.4m clear egress corridors."
    )
