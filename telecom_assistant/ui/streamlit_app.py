import streamlit as st
import pandas as pd
import os
import sys
import nest_asyncio
import logging
import traceback
from pathlib import Path

# --- CONFIGURATION ---
nest_asyncio.apply()
logging.basicConfig(level=logging.INFO)

# --- PATH SETUP ---
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.append(str(project_root))

# --- IMPORTS ---
try:
    from telecom_assistant.orchestration.graph import create_graph
    from telecom_assistant.utils.document_loader import process_uploaded_file
    from telecom_assistant.utils.auth import authenticate_user, create_user
except ImportError as e:
    st.error(f"Critical Import Error: {e}")
    st.stop()

# --- ASSETS ---
CSS_FILE = os.path.join(os.path.dirname(__file__), "style.css")

def load_css():
    with open(CSS_FILE, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Telecom Service Assistant", page_icon="📞", layout="wide")
    load_css()

    # --- SESSION STATE ---
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "graph" not in st.session_state:
        with st.spinner("Initializing AI Brain..."):
            try:
                st.session_state.graph = create_graph()
            except Exception as e:
                st.error(f"Failed to initialize AI: {e}")

    # --- AUTHENTICATION FLOW ---
    if not st.session_state.authenticated:
        show_login_signup()
    else:
        show_dashboard()

def show_login_signup():
    st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>Telecom Service Assistant</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login", use_container_width=True)
                
                if submitted:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")

        with tab2:
            with st.form("signup_form"):
                new_user = st.text_input("Choose Username")
                new_pass = st.text_input("Choose Password", type="password")
                confirm_pass = st.text_input("Confirm Password", type="password")
                role = "Customer" # Default
                submitted = st.form_submit_button("Sign Up", use_container_width=True)
                
                if submitted:
                    if new_pass != confirm_pass:
                        st.error("Passwords do not match")
                    elif len(new_pass) < 4:
                        st.error("Password must be at least 4 characters")
                    else:
                        if create_user(new_user, new_pass, role, customer_id="CUST_NEW"):
                            st.success("Account created! Please log in.")
                        else:
                            st.error("Username already exists")

def show_dashboard():
    user = st.session_state.user
    role = user["role"]
    
    # Sidebar
    with st.sidebar:
        st.title(f"Welcome, {user['username']}")
        st.caption(f"Role: {role}")
        
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.chat_history = []
            st.rerun()
            
    # Main Content
    if role == "Admin":
        show_admin_dashboard()
    else:
        show_customer_dashboard()

def show_customer_dashboard():
    st.title("Customer Dashboard")
    
    tab1, tab2, tab3 = st.tabs(["💬 AI Assistant", "📊 My Usage", "📡 Network Status"])
    
    with tab1:
        st.subheader("Chat with Support")
        
        # Display chat history
        for message in st.session_state.chat_history:
            role = message["role"]
            content = message["content"]
            with st.chat_message(role):
                st.write(content)
        
        # Chat Input
        if prompt := st.chat_input("Ask about plans, billing, or technical issues..."):
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            
            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = process_query(prompt, st.session_state.user)
                    st.write(response)
            
            # Add assistant message
            st.session_state.chat_history.append({"role": "assistant", "content": response})

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

def show_admin_dashboard():
    st.title("Admin Dashboard")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Users", "1,245", "+12%")
    col2.metric("Active Tickets", "45", "-5%")
    col3.metric("System Health", "98.5%", "Stable")
    
    st.subheader("System Logs")
    st.code("INFO: User login success (admin)\nINFO: Database backup completed\nWARN: High latency in region-east", language="log")
    
    st.subheader("Manage Knowledge Base")
    uploaded_file = st.file_uploader("Upload Policy Documents (PDF/MD)", type=['pdf', 'md', 'txt'])
    if uploaded_file:
        if st.button("Process Document"):
            with st.spinner("Indexing..."):
                if process_uploaded_file(uploaded_file):
                    st.success("Document added to Knowledge Base!")
                else:
                    st.error("Failed to process document.")

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
        result = st.session_state.graph.invoke(state)
        return result.get("final_response", "I couldn't generate a response.")
    except Exception as e:
        traceback.print_exc()
        return f"Error processing query: {str(e)}"

if __name__ == "__main__":
    main()