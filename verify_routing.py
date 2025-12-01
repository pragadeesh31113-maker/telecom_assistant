import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from telecom_assistant.orchestration.graph import classify_query

def test_routing():
    print("Testing Routing Logic...")
    
    test_cases = [
        ("How to change plan", "knowledge_retrieval"),
        ("I want to switch plan", "knowledge_retrieval"), # Ambiguous, but "switch" often implies procedure or action, sticking to knowledge for now as per logic
        ("Recommend a best plan", "service_recommendation"),
        ("My internet is slow", "network_troubleshooting"),
        ("What is my bill?", "billing_account"),
        ("Steps to configure APN", "knowledge_retrieval")
    ]
    
    for query, expected in test_cases:
        state = {"query": query}
        result = classify_query(state)
        classification = result["classification"]
        
        if classification == expected:
            print(f"PASS: '{query}' -> {classification}")
        else:
            print(f"FAIL: '{query}' -> {classification} (Expected: {expected})")

if __name__ == "__main__":
    test_routing()
