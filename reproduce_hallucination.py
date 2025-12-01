import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from telecom_assistant.agents.service_agents import process_recommendation_query

def test_hallucination():
    print("Testing Service Agent for Hallucinations...")
    
    # This should now work correctly with the fix
    response = process_recommendation_query("CUST001", "what is my current plan")
    print(f"Query: 'what is my current plan'\nResponse: {response}\n")
    
    response_plans = process_recommendation_query("CUST001", "list all plans")
    print(f"Query: 'list all plans'\nResponse: {response_plans}\n")

if __name__ == "__main__":
    test_hallucination()
