# ------------------------

def execute_sql_query(query: str):
    """
    Executes a SQL query against the telecom database to retrieve billing or plan info.
    Input should be a fully formed SQL query (e.g., "SELECT * FROM billing WHERE id='CUST001'").
    """
    try:
        # Re-initialize db inside the tool to ensure thread safety
        db = get_sql_database()
        sql_tool = QuerySQLDataBaseTool(db=db)
        return sql_tool.invoke(query)
    except Exception as e:
        return f"Error executing SQL: {str(e)}"

def create_billing_crew(customer_id: str):
    """Create and return a CrewAI crew for handling billing inquiries"""
    
    # Initialize LLM
    llm = ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
    
    # Create CrewAI Tool
    billing_tool = Tool(
        name="Database Query Tool",
        func=execute_sql_query,
        description="Executes a SQL query against the telecom database. Input should be a fully formed SQL query."
    )
    
    billing_tools = [billing_tool]

    # Billing Specialist Agent
    billing_specialist = Agent(
        role='Billing Specialist',
        goal='Explain bill components, identify unusual changes, clarify all charges',
        backstory="You are a senior billing analyst with 10 years of experience in telecom. You are precise and helpful.",
        tools=billing_tools,
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    # Service Advisor Agent
    service_advisor = Agent(
        role='Service Advisor',
        goal='Identify if customer is on optimal plan, suggest alternatives if needed',
        backstory="You help customers optimize their telecom services. You look for ways to save the customer money.",
        tools=billing_tools,
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    # Tasks
    task1 = Task(
        description=f"""
        Analyze the billing history for customer ID {customer_id}. 
        1. Write and execute a SQL query to get the billing records (Table: billing).
        2. Identify any changes in charges.
        3. Explain each charge line item.
        """,
        agent=billing_specialist,
        expected_output="A detailed analysis of the customer's recent bill."
    )

    task2 = Task(
        description=f"""
        Review usage patterns for customer ID {customer_id}.
        1. Query the usage table (Table: usage).
        2. Compare with plan limits.
        3. Suggest a better plan if needed.
        """,
        agent=service_advisor,
        expected_output="A recommendation on whether the customer should switch plans."
    )

    # Crew
    billing_crew = Crew(
        agents=[billing_specialist, service_advisor],
        tasks=[task1, task2],
        process=Process.sequential,
        verbose=True
    )

    return billing_crew

def process_billing_query(customer_id, query):
    """Process a billing query using the CrewAI crew"""
    try:
        crew = create_billing_crew(customer_id)
        result = crew.kickoff(inputs={"query": query})
        return str(result)
    except Exception as e:
        return f"Error processing billing query: {str(e)}"