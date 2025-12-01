import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from telecom_assistant.agents.network_agents import process_network_query
from telecom_assistant.agents.service_agents import process_recommendation_query

print("--- Testing Network Agent Style ---")
try:
    response = process_network_query("Is there a power outage in Mumbai?")
    print(f"\nNetwork Agent Response:\n{response}\n")
except Exception as e:
    print(f"Network Agent Error: {e}")

print("\n--- Testing Service Agent Style ---")
try:
    response = process_recommendation_query("I stream a lot of 4K video and have 3 people in my family. What plan is best?")
    print(f"\nService Agent Response:\n{response}\n")
except Exception as e:
    print(f"Service Agent Error: {e}")
