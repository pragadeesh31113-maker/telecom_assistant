from langchain_openai import ChatOpenAI
# --- FIX: Use langchain_core for modern imports ---
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
# --------------------------------------------------
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool

# --- ROBUST IMPORT FOR AGENT EXECUTOR ---
try:
    # Try the new LangGraph prebuilt agent first (most stable for Python 3.13)
    from langgraph.prebuilt import create_react_agent
    USE_LANGGRAPH = True
except ImportError:
    # Fallback to standard LangChain
    from langchain.agents import create_react_agent, AgentExecutor
    USE_LANGGRAPH = False
from langchain_openai import ChatOpenAI
# --- FIX: Use langchain_core for modern imports ---
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
# --------------------------------------------------
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool

# --- ROBUST IMPORT FOR AGENT EXECUTOR ---
try:
    # Try the new LangGraph prebuilt agent first (most stable for Python 3.13)
    from langgraph.prebuilt import create_react_agent
    USE_LANGGRAPH = True
except ImportError:
    # Fallback to standard LangChain
    from langchain.agents import create_react_agent, AgentExecutor
    USE_LANGGRAPH = False

# --- ABSOLUTE IMPORTS ---
from telecom_assistant.utils.database import get_sql_database
from telecom_assistant.config.config import LLM_MODEL, LLM_TEMPERATURE
# ------------------------

# Define a prompt template for service recommendations
SERVICE_RECOMMENDATION_TEMPLATE = """You are a telecom service advisor.
Your goal is to help customers understand their current plan and find better ones if needed.

**Instructions:**
1. **Current Plan**: If the user asks about their *current* plan, use the `customer_id` to query the `customer_usage` table (to find `plan_id` or usage) and `service_plans` table.
2. **List Plans**: If the user asks to see available plans, query the `service_plans` table.
3. **Recommend**: If the user asks for a recommendation, you can use the `EstimateDataUsage` tool to guess their needs based on activities, OR analyze their actual usage from the database if available.

**Database Schema:**
- Table `service_plans`: plan_id, name, monthly_cost, data_limit_gb, voice_minutes, sms_count, description
- Table `customer_usage`: usage_id, customer_id, data_used_gb, voice_minutes_used, sms_count_used

**Tool Usage:**
- Use `sql_db_query` to check the database.
- ONLY use `EstimateDataUsage` if the user describes activities (e.g., "I watch a lot of Netflix") and you need to guess their data needs. DO NOT use it for "list plans" or "what is my plan".
"""

def estimate_data_usage(activities: str) -> str:
    """Estimate monthly data usage based on activities. ONLY use this if the user describes specific activities like streaming, browsing, etc."""
    if "stream" in activities.lower() or "video" in activities.lower():
        return "High data usage estimated (>50GB/month)"
    elif "browse" in activities.lower() or "email" in activities.lower():
        return "Low data usage estimated (<10GB/month)"
    else:
        return "Medium data usage estimated (10-50GB/month)"

def create_service_agent():
    """Create and return a LangChain agent for service recommendations"""
    llm = ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
    
    db = get_sql_database()
    sql_tool = QuerySQLDataBaseTool(db=db)
    
    usage_tool = Tool(
        name="EstimateDataUsage",
        func=estimate_data_usage,
        description="Estimate data usage based on user activities. Input should be a string of activities."
    )
    
    tools = [sql_tool, usage_tool]
    
    # Logic to handle different agent versions
    if USE_LANGGRAPH:
        # The new way (LangGraph)
        return create_react_agent(llm, tools)
    else:
        # The old way (LangChain Legacy)
        # For legacy, the prompt needs to include {input} for the agent to work correctly.
        # We will append it here for the legacy path.
        legacy_prompt_template = SERVICE_RECOMMENDATION_TEMPLATE + "\nUser query: {input}"
        prompt = PromptTemplate.from_template(legacy_prompt_template)
        agent = create_react_agent(llm, tools, prompt)
        return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

def process_recommendation_query(customer_id: str, query: str, chat_history: list = []) -> str:
    """Process a service recommendation query using the LangChain agent"""
    try:
        executor = create_service_agent()
        
        # Format history
        context = ""
        if chat_history:
            context = "Previous Conversation:\n" + "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history[-3:]]) + "\n\n"
            
        full_query = f"Customer ID: {customer_id}\n{context}{query}"

        if USE_LANGGRAPH:
            # New LangGraph Syntax
            from langchain_core.messages import HumanMessage, SystemMessage
            messages = [
                SystemMessage(content=SERVICE_RECOMMENDATION_TEMPLATE), 
                HumanMessage(content=full_query)
            ]
            result = executor.invoke({"messages": messages})
            # Extract the AI's last message content
            return result["messages"][-1].content
        else:
            # Old LangChain Syntax
            result = executor.invoke({"input": full_query})
            return result["output"]
            
    except Exception as e:
        return f"Error processing recommendation: {str(e)}"