import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure we can import from the project root
sys.path.append(os.getcwd())

from telecom_assistant.agents.network_agents import process_network_query
from telecom_assistant.agents.billing_agents import process_billing_query
from telecom_assistant.agents.service_agents import process_recommendation_query

def test_network_agent():
    print("\n--- Testing Network Agent ---")
    query = "Is there any network issue in Mumbai?"
    print(f"Query: {query}")
    try:
        response = process_network_query(query)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

def test_billing_agent():
    print("\n--- Testing Billing Agent ---")
    customer_id = "CUST001" # Assuming this ID exists in the new DB, might need to check
    query = "What is my current plan and how much data have I used?"
    print(f"Query: {query} (Customer ID: {customer_id})")
    try:
        response = process_billing_query(customer_id, query)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

def test_service_agent():
    print("\n--- Testing Service Agent ---")
    query = "I need a plan with more data for streaming. What do you recommend?"
    print(f"Query: {query}")
    try:
        response = process_recommendation_query(query)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_network_agent()
    test_billing_agent()
    test_service_agent()
