import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

print("Testing imports...")

try:
    print("Importing graph...")
    from telecom_assistant.orchestration.graph import create_graph
    print("✅ Graph imported successfully")
except Exception as e:
    print(f"❌ Error importing graph: {e}")

try:
    print("Importing network agents...")
    from telecom_assistant.agents.network_agents import process_network_query
    print("✅ Network agents imported successfully")
except Exception as e:
    print(f"❌ Error importing network agents: {e}")

try:
    print("Importing billing agents...")
    from telecom_assistant.agents.billing_agents import process_billing_query
    print("✅ Billing agents imported successfully")
except Exception as e:
    print(f"❌ Error importing billing agents: {e}")

try:
    print("Importing service agents...")
    from telecom_assistant.agents.service_agents import process_recommendation_query
    print("✅ Service agents imported successfully")
except Exception as e:
    print(f"❌ Error importing service agents: {e}")

try:
    print("Importing knowledge agents...")
    from telecom_assistant.agents.knowledge_agents import process_knowledge_query
    print("✅ Knowledge agents imported successfully")
except Exception as e:
    print(f"❌ Error importing knowledge agents: {e}")
