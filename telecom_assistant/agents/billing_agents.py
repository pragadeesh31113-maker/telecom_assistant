from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_openai import ChatOpenAI
from typing import Any

# --- ABSOLUTE IMPORTS ---
from telecom_assistant.utils.database import get_sql_database
from telecom_assistant.config.config import LLM_MODEL, LLM_TEMPERATURE
# ------------------------

class DatabaseQueryTool(BaseTool):
    name: str = "Database Query Tool"
    description: str = "Executes a SQL query against the telecom database. Input should be a fully formed SQL query."

    def _run(self, query: str) -> str:
        try:
            # Re-initialize db inside the tool to ensure thread safety
            db = get_sql_database()
            sql_tool = QuerySQLDataBaseTool(db=db)
            return sql_tool.invoke(query)
        except Exception as e:
            return f"Error executing SQL: {str(e)}"

def create_billing_crew(customer_id: str, query: str):
    """Create and return a CrewAI crew for handling billing inquiries"""
    
    # Initialize LLM
    llm = ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
    
    # Create CrewAI Tool
    billing_tool = DatabaseQueryTool()
    
    billing_tools = [billing_tool]

    # Billing Specialist Agent
    billing_specialist = Agent(
        role='Billing Specialist',
        goal='Provide extensive, detailed explanations of bill components, identify unusual changes with reasoning, and clarify all charges thoroughly.',
        backstory="You are a senior billing analyst with 10 years of experience in telecom. You believe in transparency and explaining every detail to the customer so they fully understand their bill.",
        tools=billing_tools,
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    # Service Advisor Agent
    service_advisor = Agent(
        role='Service Advisor',
        goal='Provide comprehensive plan analysis, identifying if the customer is on the optimal plan with detailed reasoning and cost-benefit analysis of alternatives.',
        backstory="You help customers optimize their telecom services. You provide detailed financial breakdowns to show customers exactly how much they can save.",
        tools=billing_tools,
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    # Tasks
    task1 = Task(
        description=f"""
        User's request: {query}

        Analyze the billing history for customer ID {customer_id}. 
        1. Write and execute a SQL query to get the billing records (Table: customer_usage).
        2. Identify any changes in charges.
        3. Explain each charge line item in detail.

        **Database Schema:**
        - Table `customer_usage`: usage_id (VARCHAR), customer_id (VARCHAR), billing_period_start (DATE), billing_period_end (DATE), total_amount (DECIMAL), payment_status (VARCHAR)
        - Table `service_plans`: plan_id (VARCHAR), name (VARCHAR), monthly_cost (DECIMAL), data_limit_gb (INT), voice_minutes (INT), sms_count (INT), description (TEXT)
        """,
        agent=billing_specialist,
        expected_output="""
        A highly detailed analysis of the customer's recent bill, including:
        - A list of the last 3 billing dates and amounts.
        - Identification of any price increases or irregularities, with potential reasons.
        - A clear, extensive explanation of what each charge represents.
        - DO NOT be brief. Explain the "Why" behind the numbers.
        """
    )

    task2 = Task(
        description=f"""
        User's request: {query}

        Review usage patterns for customer ID {customer_id}.
        1. Query the usage table (Table: customer_usage).
        2. Compare with plan limits.
        3. Suggest a better plan if needed, with a full cost justification.

        **Database Schema:**
        - Table `customer_usage`: usage_id (VARCHAR), customer_id (VARCHAR), data_used_gb (DECIMAL), voice_minutes_used (INT), sms_count_used (INT)
        - Table `service_plans`: plan_id (VARCHAR), name (VARCHAR), monthly_cost (DECIMAL), data_limit_gb (INT), voice_minutes (INT), sms_count (INT), description (TEXT)
        """,
        agent=service_advisor,
        expected_output="""
        A comprehensive recommendation that includes:
        - The customer's average monthly data and voice usage (show the numbers!).
        - The limits of their current plan.
        - A direct comparison (e.g., "Used 12GB vs Limit 10GB").
        - A specific plan recommendation with a detailed cost analysis (e.g., "Switching to Premium will cost $X more but save $Y in overages").
        - Explain the reasoning for the recommendation extensively.
        """
    )

    # Crew
    billing_crew = Crew(
        agents=[billing_specialist, service_advisor],
        tasks=[task1, task2],
        process=Process.sequential,
        verbose=True
    )

    return billing_crew

def process_billing_query(customer_id: str, query: str, chat_history: list = []) -> str:
    """Process a billing query using CrewAI."""
    try:
        # Format history
        context = ""
        if chat_history:
            context = "Previous Conversation:\n" + "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history[-3:]]) + "\n\n"
            
        billing_crew = create_billing_crew(customer_id, context + query)
        result = billing_crew.kickoff()
        return str(result)
    except Exception as e:
        return f"Error processing billing query: {str(e)}"