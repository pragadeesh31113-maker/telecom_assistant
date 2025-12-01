import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.getcwd(), 'telecom_assistant'))

from agents.network_agents import process_network_query

print("Testing Network Agent...")
response = process_network_query("Is there any network issue in Bangalore?")
print("\n--- Response ---")
print(response)
