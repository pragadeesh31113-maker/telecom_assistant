from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph, END

# --- ABSOLUTE IMPORTS ---
from telecom_assistant.agents.billing_agents import process_billing_query
from telecom_assistant.agents.network_agents import process_network_query
from telecom_assistant.agents.service_agents import process_recommendation_query
from telecom_assistant.agents.knowledge_agents import process_knowledge_query
# ------------------------

# Define the state structure
class TelecomAssistantState(TypedDict):
    query: str
    customer_info: Dict[str, Any]
    classification: str
    intermediate_responses: Dict[str, Any]
    final_response: str
    chat_history: List[Dict[str, str]]

def classify_query(state: TelecomAssistantState) -> TelecomAssistantState:
    """Classify the query into different categories"""
    query = state["query"].lower()
    
    classification = "fallback_handler"
    
    # 1. Knowledge/Procedural Queries (Priority: "How to", "Steps", "Guide")
    # Added "what to do", "what should i do", "what can i do" to catch general troubleshooting questions
    if any(phrase in query for phrase in ["how to", "how do i", "steps to", "procedure", "guide", "configure", "setup", "apn", "troubleshoot", "what to do", "what should i do", "what can i do"]):
        classification = "knowledge_retrieval"
        
    # 2. Billing & Account
    elif any(word in query for word in ["bill", "charge", "payment", "account", "invoice", "cost", "usage", "balance"]):
        classification = "billing_account"
        
    # 3. Service Recommendations (Plan advice, but NOT "how to change")
    elif any(word in query for word in ["recommend", "best plan", "cheapest", "upgrade", "new plan", "compare"]):
        classification = "service_recommendation"
        
    # 4. Network Issues
    elif any(word in query for word in ["network", "signal", "connection", "call", "data", "slow", "internet", "5g", "4g", "outage", "status", "down", "issue", "problem", "ticket"]):
        classification = "network_troubleshooting"
        
    # 5. Specific "Change Plan" ambiguity handling
    elif "plan" in query:
        if "change" in query or "switch" in query:
             # "How to change plan" -> Knowledge
             classification = "knowledge_retrieval" 
        else:
            # "Recommend a plan" -> Service
            classification = "service_recommendation"

    return {**state, "classification": classification}

def route_query(state: TelecomAssistantState) -> str:
    """Route the query to the appropriate node based on classification"""
    classification = state["classification"]
    if classification == "billing_account":
        return "crew_ai_node"
    elif classification == "network_troubleshooting":
        return "autogen_node"
    elif classification == "service_recommendation":
        return "langchain_node"
    elif classification == "knowledge_retrieval":
        return "llamaindex_node"
    else:
        return "fallback_handler"

def crew_ai_node(state: TelecomAssistantState) -> TelecomAssistantState:
    query = state["query"]
    chat_history = state.get("chat_history", [])
    customer_id = state.get("customer_info", {}).get("id", "CUST001")
    response = process_billing_query(customer_id, query, chat_history)
    return {**state, "intermediate_responses": {"crew_ai": response}}

def autogen_node(state: TelecomAssistantState) -> TelecomAssistantState:
    query = state["query"]
    chat_history = state.get("chat_history", [])
    response = process_network_query(query, chat_history)
    return {**state, "intermediate_responses": {"autogen": response}}

def langchain_node(state: TelecomAssistantState) -> TelecomAssistantState:
    query = state["query"]
    chat_history = state.get("chat_history", [])
    customer_id = state.get("customer_info", {}).get("id", "CUST001")
    response = process_recommendation_query(customer_id, query, chat_history)
    return {**state, "intermediate_responses": {"langchain": response}}

def llamaindex_node(state: TelecomAssistantState) -> TelecomAssistantState:
    query = state["query"]
    chat_history = state.get("chat_history", [])
    response = process_knowledge_query(query, chat_history)
    return {**state, "intermediate_responses": {"llamaindex": response}}

def fallback_handler(state: TelecomAssistantState) -> TelecomAssistantState:
    response = "I'm not sure how to help with that. Could you ask about billing, plans, or technical support?"
    return {**state, "intermediate_responses": {"fallback": response}}

def formulate_response(state: TelecomAssistantState) -> TelecomAssistantState:
    intermediate_responses = state["intermediate_responses"]
    response_value = next(iter(intermediate_responses.values()))
    return {**state, "final_response": str(response_value)}

def create_graph():
    """Create and return the workflow graph"""
    workflow = StateGraph(TelecomAssistantState)
    
    workflow.add_node("classify_query", classify_query)
    workflow.add_node("crew_ai_node", crew_ai_node)
    workflow.add_node("autogen_node", autogen_node)
    workflow.add_node("langchain_node", langchain_node)
    workflow.add_node("llamaindex_node", llamaindex_node)
    workflow.add_node("fallback_handler", fallback_handler)
    workflow.add_node("formulate_response", formulate_response)
    
    workflow.add_conditional_edges(
        "classify_query",
        route_query,
        {
            "crew_ai_node": "crew_ai_node",
            "autogen_node": "autogen_node",
            "langchain_node": "langchain_node",
            "llamaindex_node": "llamaindex_node",
            "fallback_handler": "fallback_handler"
        }
    )
    
    workflow.add_edge("crew_ai_node", "formulate_response")
    workflow.add_edge("autogen_node", "formulate_response")
    workflow.add_edge("langchain_node", "formulate_response")
    workflow.add_edge("llamaindex_node", "formulate_response")
    workflow.add_edge("fallback_handler", "formulate_response")
    workflow.add_edge("formulate_response", END)
    
    workflow.set_entry_point("classify_query")
    return workflow.compile()