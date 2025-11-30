import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage
from config.config import DOCS_DIR

INDEX_STORAGE_DIR = os.path.join(os.path.dirname(DOCS_DIR), "storage")

def load_documents():
    """Load documents from the data directory"""
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR, exist_ok=True)
        return []
    
    reader = SimpleDirectoryReader(DOCS_DIR)
    documents = reader.load_data()
    return documents

def get_index():
    """Get or create the vector index"""
    if not os.path.exists(INDEX_STORAGE_DIR):
        documents = load_documents()
        if not documents:
            return None
            
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=INDEX_STORAGE_DIR)
    else:
        storage_context = StorageContext.from_defaults(persist_dir=INDEX_STORAGE_DIR)
        index = load_index_from_storage(storage_context)
    
    return index

def process_uploaded_file(uploaded_file):
    """Save uploaded file to documents directory and update index"""
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR, exist_ok=True)
        
    file_path = os.path.join(DOCS_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Re-index (in a real app, we might want to update incrementally)
    documents = load_documents()
    index = VectorStoreIndex.from_documents(documents)
    if not os.path.exists(INDEX_STORAGE_DIR):
        os.makedirs(INDEX_STORAGE_DIR)
    index.storage_context.persist(persist_dir=INDEX_STORAGE_DIR)
    
    return True
