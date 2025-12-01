import sys
import os
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from telecom_assistant.agents.billing_agents import process_billing_query

def test_billing_speed():
    print("Testing Billing Agent Speed...")
    
    start_time = time.time()
    response = process_billing_query("CUST001", "What is my current bill?")
    end_time = time.time()
    
    duration = end_time - start_time
    print(f"Response Time: {duration:.2f} seconds")
    print(f"Response: {response[:100]}...") # Print first 100 chars
    
    if duration < 10:
        print("PASS: Response time is acceptable (<10s)")
    else:
        print("WARN: Response time is still high (>10s)")

if __name__ == "__main__":
    test_billing_speed()
