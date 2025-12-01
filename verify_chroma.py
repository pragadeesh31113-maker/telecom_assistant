import sys
import os
import shutil

# Add project root to path
sys.path.append(os.getcwd())

from telecom_assistant.utils.document_loader import get_index
from telecom_assistant.agents.knowledge_agents import process_knowledge_query

# Clean up old storage if exists to force fresh creation (optional, but good for testing migration)
# if os.path.exists("telecom_assistant/data/chroma_db"):
#     shutil.rmtree("telecom_assistant/data/chroma_db")

print("--- Initializing ChromaDB Index ---")
try:
    index = get_index()
    if index:
        print("Index initialized successfully.")
    else:
        print("Failed to initialize index.")
except Exception as e:
    print(f"Error initializing index: {e}")

print("\n--- Testing Knowledge Query ---")
query = "How do I configure APN settings?"
try:
    response = process_knowledge_query(query)
    print(f"Query: {query}")
    print(f"Response:\n{response}")
except Exception as e:
    print(f"Error querying: {e}")
