from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool

# --- ROBUST IMPORT FOR AGENT EXECUTOR ---
try:
    from langgraph.prebuilt import create_react_agent
    USE_LANGGRAPH = True
except ImportError:
    from langchain.agents import create_react_agent, AgentExecutor
    USE_LANGGRAPH = False

# --- ABSOLUTE IMPORTS ---
from telecom_assistant.utils.database import get_sql_database
from telecom_assistant.config.config import LLM_MODEL, LLM_TEMPERATURE
# ------------------------

BILLING_AGENT_TEMPLATE = """You are a Billing & Service Specialist for a telecom company.
Your goal is to explain bills, analyze usage, and check for plan suitability.

**Database Schema:**
- Table `customer_usage`: usage_id, customer_id, billing_period_start, billing_period_end, total_amount, payment_status, data_used_gb, voice_minutes_used, sms_count_used
- Table `service_plans`: plan_id, name, monthly_cost, data_limit_gb, voice_minutes, sms_count, description

**Instructions:**
1. **Analyze**: When asked about a bill, query `customer_usage` for the given customer ID.
2. **Explain**: Break down the charges. If the `total_amount` is higher than the plan's `monthly_cost`, explain why (e.g., overage).
3. **Compare**: Check if their usage fits their current plan limits.
4. **Recommend**: If they are consistently over-using, suggest a better plan from `service_plans`.

**Response Guidelines:**
- Be detailed and helpful.
- Explain the "Why" behind the numbers.
- If everything looks normal, reassure the customer.

User query: {input}
"""

def create_billing_agent():
    """Create and return a fast LangChain agent for billing"""
    llm = ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
    
    db = get_sql_database()
    sql_tool = QuerySQLDataBaseTool(db=db)
    
    tools = [sql_tool]
    
    if USE_LANGGRAPH:
        return create_react_agent(llm, tools)
    else:
        prompt = PromptTemplate.from_template(BILLING_AGENT_TEMPLATE)
        agent = create_react_agent(llm, tools, prompt)
        return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

def process_billing_query(customer_id: str, query: str, chat_history: list = []) -> str:
    """Process a billing query using the optimized LangChain agent"""
    try:
        executor = create_billing_agent()
        
        # Format history
        context = ""
        if chat_history:
            context = "Previous Conversation:\n" + "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history[-3:]]) + "\n\n"
            
        full_query = f"Customer ID: {customer_id}\n{context}{query}"

        if USE_LANGGRAPH:
            from langchain_core.messages import HumanMessage, SystemMessage
            # Add system prompt for LangGraph agent
            messages = [
                SystemMessage(content=BILLING_AGENT_TEMPLATE.format(input="")), # Pre-load system instruction
                HumanMessage(content=full_query)
            ]
            result = executor.invoke({"messages": messages})
            return result["messages"][-1].content
        else:
            result = executor.invoke({"input": full_query})
            return result["output"]
            
    except Exception as e:
        return f"Error processing billing query: {str(e)}"