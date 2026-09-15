import os
import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    research_dir = os.path.join(base_dir, "research papers")
    data_dir = os.path.join(base_dir, "data")
    
    os.makedirs(data_dir, exist_ok=True)
    
    # 1. Load PDFs and TXTs
    print(f"Loading files from {research_dir}...")
    pdf_files = glob.glob(os.path.join(research_dir, "*.pdf"))
    txt_files = glob.glob(os.path.join(research_dir, "*.txt"))
    
    documents = []
    for pdf_path in pdf_files:
        print(f"Loading {os.path.basename(pdf_path)}")
        try:
            loader = PyPDFLoader(pdf_path)
            documents.extend(loader.load())
        except Exception as e:
            print(f"Error loading {pdf_path}: {e}")
            
    from langchain_community.document_loaders import TextLoader
    for txt_path in txt_files:
        print(f"Loading {os.path.basename(txt_path)}")
        try:
            loader = TextLoader(txt_path, encoding='utf-8')
            documents.extend(loader.load())
        except Exception as e:
            print(f"Error loading {txt_path}: {e}")
            
    print(f"Loaded {len(documents)} pages/documents in total.")
    
    # 2. Split into chunks
    print("Chunking documents...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks.")
    
    # 3. Create Embeddings
    print("Initializing Ollama Embedding Model...")
    embeddings = OllamaEmbeddings(model="llama3.1")
    
    # 4. Create and Save FAISS index
    print("Creating FAISS index (this may take a while)...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    faiss_path = os.path.join(data_dir, "faiss_index")
    vectorstore.save_local(faiss_path)
    print(f"Saved FAISS index to {faiss_path}")
    print("Ingestion complete!")

if __name__ == "__main__":
    main()
