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
SERVICE_RECOMMENDATION_TEMPLATE = """You are a telecom service advisor who helps customers find the best plan for their needs.
When recommending plans, consider:
1. The customer's usage patterns (data, voice, SMS)
2. Number of people/devices that will use the plan
3. Special requirements (international calling, streaming, etc.)
4. Budget constraints

**RESPONSE GUIDELINES:**
- **Be Extensive**: Provide detailed explanations for your recommendations.
- **Show Reasoning**: Explain *why* a plan is a good fit based on the user's specific usage data.
- **Compare Options**: If applicable, compare the recommended plan with others to show value.
- **Be Helpful**: Offer tips on how to optimize usage or save money.
- **Do NOT be brief**: The user wants a comprehensive answer.

You have access to a database with plan information. Use it to find available plans.

**Database Schema:**
- Table `service_plans`: plan_id (VARCHAR), name (VARCHAR), monthly_cost (DECIMAL), data_limit_gb (INT), voice_minutes (INT), sms_count (INT), description (TEXT)
- Table `customer_usage`: usage_id (VARCHAR), customer_id (VARCHAR), data_used_gb (DECIMAL), voice_minutes_used (INT), sms_count_used (INT)

User query: {input}
"""

def estimate_data_usage(activities: str) -> str:
    """Estimate monthly data usage based on activities."""
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
        description="Estimate data usage based on user activities"
    )
    
    tools = [sql_tool, usage_tool]
    
    # Logic to handle different agent versions
    if USE_LANGGRAPH:
        # The new way (LangGraph)
        return create_react_agent(llm, tools)
    else:
        # The old way (LangChain Legacy)
        prompt = PromptTemplate.from_template(SERVICE_RECOMMENDATION_TEMPLATE)
        agent = create_react_agent(llm, tools, prompt)
        return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

def process_recommendation_query(query: str, chat_history: list = []) -> str:
    """Process a service recommendation query using the LangChain agent"""
    try:
        executor = create_service_agent()
        
        # Format history
        context = ""
        if chat_history:
            context = "Previous Conversation:\n" + "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history[-3:]]) + "\n\n"
            
        full_query = context + query

        if USE_LANGGRAPH:
            # New LangGraph Syntax
            from langchain_core.messages import HumanMessage
            result = executor.invoke({"messages": [HumanMessage(content=full_query)]})
            # Extract the AI's last message content
            return result["messages"][-1].content
        else:
            # Old LangChain Syntax
            result = executor.invoke({"input": full_query})
            return result["output"]
            
    except Exception as e:
        return f"Error processing recommendation: {str(e)}"