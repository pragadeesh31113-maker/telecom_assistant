import streamlit as st
import pandas as pd
import os
import sys
import nest_asyncio
import logging
import traceback
from pathlib import Path

# Add project root to path
root_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_path))

from telecom_assistant.orchestration.graph import create_graph

# --- CONFIGURATION ---
nest_asyncio.apply()
logging.basicConfig(level=logging.INFO)

def render_chat_interface(role_name="User"):
    st.subheader(f"Chat with Support ({role_name})")
    
    # Display chat history
    for message in st.session_state.chat_history:
        role = message["role"]
        content = message["content"]
        # Updated Avatars: 📡 for AI, 🧑‍💼 for User
        avatar = "🧑‍💼" if role == "user" else "📡"
        with st.chat_message(role, avatar=avatar):
            st.write(content)
    
    # Chat Input
    if prompt := st.chat_input("Ask about plans, billing, or technical issues..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💼"):
            st.write(prompt)
        
        # Generate response
        with st.chat_message("assistant", avatar="📡"):
            with st.spinner("Thinking..."):
                # process_query now returns the full state dict
                execution_result = process_query(prompt, st.session_state.user)
                
                if isinstance(execution_result, dict):
                    final_response = execution_result.get("final_response", "No response generated.")
                    # Store the full state for the debug tab
                    st.session_state.last_thought_process = execution_result
                else:
                    final_response = execution_result
                    st.session_state.last_thought_process = {"error": execution_result}

                st.write(final_response)
        
        # Add assistant message
        st.session_state.chat_history.append({"role": "assistant", "content": final_response})

def show_customer_dashboard():
    st.title("Customer Dashboard")
    
    # Add a new tab for "Internal Thoughts"
    tab1, tab2, tab3, tab4 = st.tabs(["💬 AI Assistant", "📊 My Usage", "📡 Network Status", "🧠 Internal Thoughts"])
    
    with tab1:
        render_chat_interface("Customer")

    with tab2:
        st.subheader("Current Usage")
        col1, col2, col3 = st.columns(3)
        col1.metric("Data", "12.5 GB", "85% Used")
        col2.metric("Voice", "450 Mins", "Unlimited")
        col3.metric("SMS", "120", "Unlimited")
        
        st.info("Your bill of $49.99 is due on Dec 5th.")

    with tab3:
        st.subheader("Network Status")
        st.success("✅ All Systems Operational in your area (Mumbai)")
        st.map(pd.DataFrame({'lat': [19.0760], 'lon': [72.8777]}))

    with tab4:
        st.subheader("🧠 Internal Logic & Flow")
        if "last_thought_process" in st.session_state and st.session_state.last_thought_process:
            state = st.session_state.last_thought_process
            
            # 1. Classification
            st.markdown("### 1. Classification")
            classification = state.get("classification", "Unknown")
            st.info(f"Query Classified As: **{classification}**")
            
            # 2. Routing
            st.markdown("### 2. Routing")
            if classification == "billing_account":
                st.success("Routed to: **Billing Crew (CrewAI)**")
            elif classification == "network_troubleshooting":
                st.success("Routed to: **Network Specialist (AutoGen)**")
            elif classification == "service_recommendation":
                st.success("Routed to: **Service Advisor (LangChain)**")
            elif classification == "knowledge_retrieval":
                st.success("Routed to: **Knowledge Base (LlamaIndex)**")
            else:
                st.warning("Routed to: **Fallback Handler**")
                
            # 3. Intermediate Output
            st.markdown("### 3. Agent Output (Raw)")
            intermediate = state.get("intermediate_responses", {})
            st.json(intermediate)
            
            # 4. Full State Dump
            with st.expander("View Full State JSON"):
                st.json(state)
        else:
            st.info("Ask a question in the Chat tab to see the internal thought process here.")

def show_admin_dashboard():
    try:
        import plotly.express as px
        import plotly.graph_objects as go
    except ImportError:
        st.error("Plotly is not installed. Please install it using `pip install plotly`.")
        return

    st.title("Admin Dashboard")
    
    # Admin Navigation
    with st.sidebar:
        st.markdown("---")
        admin_page = st.radio("Navigate", ["Overview", "Analytics", "System Health", "AI Assistant"])
    
    if admin_page == "Overview":
        st.header("Overview")
        # Top Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Users", "1,245", "+12%")
        col2.metric("Active Tickets", "45", "-5%")
        col3.metric("Avg Response Time", "1.2s", "-0.3s")
        col4.metric("System Health", "98.5%", "Stable")
        
        st.markdown("### Recent System Logs")
        st.code("INFO: User login success (admin)\nINFO: Database backup completed\nWARN: High latency in region-east\nINFO: New plan 'Premium 5G' added", language="log")

    elif admin_page == "Analytics":
        st.header("Analytics")
        # Charts Row 1
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("User Growth (Last 6 Months)")
            data_growth = pd.DataFrame({
                "Month": ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                "Users": [800, 950, 1020, 1100, 1180, 1245]
            })
            fig_growth = px.area(data_growth, x="Month", y="Users", template="plotly_dark")
            fig_growth.update_traces(line_color='#3b82f6', fillcolor='rgba(59, 130, 246, 0.3)')
            st.plotly_chart(fig_growth, use_container_width=True)

        with col_chart2:
            st.subheader("Ticket Distribution")
            data_tickets = pd.DataFrame({
                "Category": ["Network", "Billing", "Service", "Technical"],
                "Count": [35, 25, 15, 25]
            })
            fig_tickets = px.pie(data_tickets, values="Count", names="Category", hole=0.4, template="plotly_dark")
            fig_tickets.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_tickets, use_container_width=True)

    elif admin_page == "System Health":
        st.header("System Health & Knowledge Base")
        col_kb, col_dummy = st.columns([1, 1])
        
        with col_kb:
            st.subheader("Manage Knowledge Base")
            uploaded_file = st.file_uploader("Upload Policy Documents (PDF/MD)", type=['pdf', 'md', 'txt'])
            if uploaded_file:
                if st.button("Process Document"):
                    with st.spinner("Indexing..."):
                        if process_uploaded_file(uploaded_file):
                            st.success("Document added to Knowledge Base!")
                        else:
                            st.error("Failed to process document.")
                            
    elif admin_page == "AI Assistant":
        render_chat_interface("Admin")

def process_query(query, user_info):
    """Process query using the AI Graph"""
    if "graph" not in st.session_state or st.session_state.graph is None:
        return "System Error: AI Brain not initialized."
        
    state = {
        "query": query,
        "customer_info": {"id": user_info.get("customer_id", "CUST001"), "email": "user@example.com"},
        "classification": "",
        "intermediate_responses": {},
        "final_response": "",
        "chat_history": st.session_state.chat_history # Pass history!
    }
    
    try:
        # Return the full dict result, not just the string
        result = st.session_state.graph.invoke(state)
        return result
    except Exception as e:
        traceback.print_exc()
        return f"Error processing query: {str(e)}"

def process_uploaded_file(file):
    # Placeholder for file processing
    return True

def main():
    # Initialize Session State
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "user" not in st.session_state:
        st.session_state.user = None
    
    # Initialize AI Graph
    if "graph" not in st.session_state:
        try:
            st.session_state.graph = create_graph()
            logging.info("AI Graph initialized successfully.")
        except Exception as e:
            st.error(f"Failed to initialize AI Brain: {str(e)}")
            logging.error(f"Graph initialization failed: {traceback.format_exc()}")
            st.session_state.graph = None

    # Login Screen
    if not st.session_state.authenticated:
        st.title("Nexus Telecom Portal")
        st.subheader("Please Login")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login as Customer (John Doe)", use_container_width=True):
                st.session_state.user = {"username": "John Doe", "role": "Customer", "customer_id": "CUST001"}
                st.session_state.authenticated = True
                st.rerun()
                
        with col2:
            if st.button("Login as Admin", use_container_width=True):
                st.session_state.user = {"username": "System Admin", "role": "Admin", "customer_id": "ADM001"}
                st.session_state.authenticated = True
                st.rerun()
        return

    user = st.session_state.user
    role = user.get("role", "Customer")

    # Sidebar
    with st.sidebar:
        st.title(f"Nexus Telecom")
        st.caption(f"Welcome, {user['username']}")
        st.caption(f"Role: {role}")
        
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.chat_history = []
            st.session_state.last_thought_process = None # Clear thought process on logout
            st.rerun()
            
    # Main Content
    if role == "Admin":
        show_admin_dashboard()
    else:
        show_customer_dashboard()

if __name__ == "__main__":
    main()