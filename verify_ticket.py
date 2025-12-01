import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from telecom_assistant.agents.network_agents import process_network_query

query = "What is the status of ticket TKT-001?"
print(f"--- Testing Network Agent with Ticket Query: '{query}' ---")

try:
    response = process_network_query(query)
    print(f"\nResponse:\n{response}")
except Exception as e:
    print(f"\nError:\n{e}")
