import os
import chromadb
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.vector_stores.chroma import ChromaVectorStore
from telecom_assistant.config.config import DOCS_DIR

# Define ChromaDB persistence directory
CHROMA_DB_DIR = os.path.join(os.path.dirname(DOCS_DIR), "chroma_db")
COLLECTION_NAME = "telecom_docs"

def load_documents():
    """Load documents from the data directory"""
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR, exist_ok=True)
        return []
    
    reader = SimpleDirectoryReader(DOCS_DIR)
    documents = reader.load_data()
    return documents

def get_index():
    """Get or create the ChromaDB vector index"""
    
    # Initialize ChromaDB client
    db = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    chroma_collection = db.get_or_create_collection(COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR, exist_ok=True)
        return None

    # Check if collection is empty (naive check, or just always load from storage context)
    # LlamaIndex with Chroma is often best handled by creating from documents if new, 
    # or loading from vector store if exists.
    
    try:
        # Try to load existing index from the vector store
        index = VectorStoreIndex.from_vector_store(
            vector_store,
            storage_context=storage_context,
        )
        # If index is empty, we might need to populate it. 
        # But VectorStoreIndex.from_vector_store assumes it's there.
        # A better pattern is to check if we have docs and if the DB is empty.
        
        if chroma_collection.count() == 0:
            documents = load_documents()
            if documents:
                index = VectorStoreIndex.from_documents(
                    documents, storage_context=storage_context
                )
        
        return index
        
    except Exception as e:
        print(f"Error loading index: {e}")
        # Fallback: create new
        documents = load_documents()
        if documents:
            index = VectorStoreIndex.from_documents(
                documents, storage_context=storage_context
            )
            return index
        return None

def process_uploaded_file(uploaded_file):
    """Save uploaded file to documents directory and update index"""
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR, exist_ok=True)
        
    file_path = os.path.join(DOCS_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Re-index / Update
    # For Chroma, we can just add the new document to the existing index
    try:
        db = chromadb.PersistentClient(path=CHROMA_DB_DIR)
        chroma_collection = db.get_or_create_collection(COLLECTION_NAME)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # Load ONLY the new file to avoid re-indexing everything (optimization)
        # For simplicity in this demo, we'll reload all to ensure consistency, 
        # or we can just create an index from this one file and merge? 
        # Safest for now: Reload all or just append.
        
        # Let's just append this document
        reader = SimpleDirectoryReader(input_files=[file_path])
        documents = reader.load_data()
        
        index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
        index.insert_nodes(documents) # This inserts nodes into the index and vector store
        
        return True
    except Exception as e:
        print(f"Error updating index: {e}")
        return False
