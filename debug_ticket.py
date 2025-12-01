import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from telecom_assistant.agents.network_agents import process_network_query

# Test with exact ID
query1 = "What is the status of ticket TKT001?"
print(f"--- TEST 1: '{query1}' ---")
try:
    response = process_network_query(query1)
    print(f"Response:\n{response}\n")
except Exception as e:
    print(f"Error: {e}\n")

# Test with fuzzy ID
query2 = "Check status for ticket TKT-001"
print(f"--- TEST 2: '{query2}' ---")
try:
    response = process_network_query(query2)
    print(f"Response:\n{response}\n")
except Exception as e:
    print(f"Error: {e}\n")
