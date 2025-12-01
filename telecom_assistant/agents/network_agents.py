import autogen
from typing import Annotated
from telecom_assistant.utils.database import get_sql_database
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from telecom_assistant.config.config import LLM_MODEL, LLM_TEMPERATURE, OPENAI_API_KEY
import traceback

# --- TOOL DEFINITION ---
def execute_sql_query(query: Annotated[str, "The SQL query to execute"]) -> str:
    """Executes a SQL query against the telecom database."""
    print(f"[DEBUG] Executing SQL: {query}")
    try:
        db = get_sql_database()
        sql_tool = QuerySQLDataBaseTool(db=db)
        return sql_tool.invoke(query)
    except Exception as e:
        print(f"[ERROR] SQL Execution Failed: {e}")
        traceback.print_exc()
        return f"Error executing SQL: {str(e)}"

# --- AGENT FACTORY ---
def create_network_agents():
    """Creates the UserProxy and Assistant agents for network troubleshooting."""
    
    # Configuration
    config_list = [{"model": LLM_MODEL, "api_key": OPENAI_API_KEY, "temperature": LLM_TEMPERATURE}]
    llm_config = {
        "config_list": config_list,
        "timeout": 120,
    }

    # 1. User Proxy Agent (Executes tools)
    user_proxy = autogen.UserProxyAgent(
        name="User_Proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=5,
        is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={"work_dir": "coding", "use_docker": False},
    )

    # 2. Assistant Agent (Generates plans and queries)
    assistant = autogen.AssistantAgent(
        name="Network_Specialist",
        llm_config=llm_config,
        system_message="""You are a Network Troubleshooting Specialist.
        Your goal is to diagnose network issues and check support ticket status by querying the database and providing comprehensive, well-reasoned explanations.
        
        **Database Schema:**
        - Table `network_incidents`: incident_id (VARCHAR), incident_type (VARCHAR), location (VARCHAR), affected_services (TEXT), start_time (TIMESTAMP), resolution_time (TIMESTAMP), status (VARCHAR), severity (VARCHAR), description (TEXT), resolution_details (TEXT)
        - Table `support_tickets`: ticket_id (VARCHAR), customer_id (VARCHAR), issue_type (VARCHAR), description (TEXT), status (VARCHAR), created_at (TIMESTAMP), resolved_at (TIMESTAMP), priority (VARCHAR), resolution_notes (TEXT)
        
        **Process:**
        1.  Analyze the user's query to identify if it's about a general network issue or a specific support ticket.
        2.  **For Ticket Status:**
            - Use `execute_sql_query` to check `support_tickets`.
            - Search by `ticket_id` if provided. If the ID format is slightly different (e.g., TKT-001 vs TKT001), try using `LIKE` or removing hyphens.
            - If no ticket ID is provided, ask the user for it or search by `customer_id` if available.
        3.  **For Network Issues:**
            - Use `execute_sql_query` to check `network_incidents`.
            - **IMPORTANT**: Use `LIKE` operator for location searches (e.g., `location LIKE '%Mumbai%'`) to match specific areas like "Mumbai Central".
            - **IMPORTANT**: Use `LIKE` operator for issue keywords in `description` or `incident_type` (e.g., `description LIKE '%power%'` OR `incident_type LIKE '%power%'`).
            - Check for active statuses (e.g., 'Open', 'In Progress', 'Ongoing', 'Scheduled').
        4.  Interpret the results and provide a detailed status update to the user.
        5.  If there is an incident or ticket, explain the details, including status, priority, and notes.
        
        **RESPONSE GUIDELINES:**
        - **Be Extensive**: Do not give short answers. Provide a full explanation of the situation.
        - **Show Reasoning**: Explain how you arrived at your conclusion based on the data.
        - **NO HALLUCINATIONS**: If the database query returns no results, state clearly that no ticket or incident was found. DO NOT make up a status or details.
        - **Be Helpful**: Offer context and reassurance where appropriate.
        - **Control Signal**: End your message with TERMINATE only after you have provided the full, detailed response.
        """
    )

    # Register the tool
    autogen.register_function(
        execute_sql_query,
        caller=assistant,
        executor=user_proxy,
        name="execute_sql_query",
        description="Executes a SQL query against the telecom database."
    )

    return user_proxy, assistant

# --- ENTRY POINT ---
def process_network_query(query: str, chat_history: list = []) -> str:
    """Process a network troubleshooting query using AG2 agents."""
    try:
        user_proxy, assistant = create_network_agents()
        
        # Format history for context (simplified)
        context = ""
        if chat_history:
            context = "Previous Conversation:\n" + "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history[-3:]]) + "\n\n"
        
        full_message = context + query

        # Initiate chat
        chat_result = user_proxy.initiate_chat(
            assistant,
            message=full_message,
            summary_method="last_msg"
        )
        
        # Extract the final response (stripping TERMINATE)
        final_response = chat_result.summary.replace("TERMINATE", "").strip()
        return final_response
        
    except Exception as e:
        print(f"[ERROR] Network Agent Failed: {e}")
        traceback.print_exc()
        return f"Error processing network query: {str(e)}"