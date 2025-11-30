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
# Get the absolute path to the telecom_assistant folder
current_file = Path(__file__).resolve()
# If in ui/, go up two levels: ui -> telecom_assistant
project_root = current_file.parent.parent
sys.path.append(str(project_root))

print(f"[SYSTEM] Project root added to path: {project_root}")

# --- SAFE IMPORTS ---
# Initialize variables to None first so we don't get NameError
create_graph = None
process_uploaded_file = None

try:
    # Now that we fixed the dots in graph.py, this should work!
    from orchestration.graph import create_graph
    from utils.document_loader import process_uploaded_file
except ImportError as e:
    print(f"\n[CRITICAL IMPORT ERROR] {e}")
    # We don't crash here; we handle it in main()

def main():
    st.set_page_config(page_title="Telecom Service Assistant", page_icon="📞", layout="wide")

    # Session State Init
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_type" not in st.session_state:
        st.session_state.user_type = None
    if "email" not in st.session_state:
        st.session_state.email = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # --- GRAPH INITIALIZATION ---
    if "graph" not in st.session_state:
        if create_graph is None:
            st.error("⚠️ System Error: The AI Brain (orchestration) failed to load.")
            st.warning("Did you update `orchestration/graph.py` to remove the `..` dots from imports?")
            st.stop() # Stop execution safely
        else:
            with st.spinner("Initializing AI Brain..."):
                try:
                    st.session_state.graph = create_graph()
                    print("[SYSTEM] Graph initialized successfully.")
                except Exception as e:
                    st.error(f"Failed to compile graph: {e}")

    # Helper function to run the graph
    def process_query(query: str):
        state = {
            "query": query,
            "customer_info": {"email": st.session_state.email, "id": "CUST001"},
            "classification": "",
            "intermediate_responses": {},
            "final_response": "",
            "chat_history": st.session_state.chat_history
        }
        try:
            result = st.session_state.graph.invoke(state)
            return result["final_response"]
        except Exception as e:
            traceback.print_exc()
            return f"Error: {str(e)}"

    # --- SIDEBAR ---
    with st.sidebar:
        st.title("Telecom Service Assistant")
        if not st.session_state.authenticated:
            st.subheader("Login")
            email = st.text_input("Email Address")
            user_type = st.selectbox("User Type", ["Customer", "Admin"])
            if st.button("Login"):
                if email and "@" in email:
                    st.session_state.authenticated = True
                    st.session_state.user_type = user_type
                    st.session_state.email = email
                    st.success(f"Logged in as {user_type}")
                    st.rerun()
        else:
            st.success(f"Logged in as {st.session_state.user_type}")
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.user_type = None
                st.session_state.email = None
                st.session_state.chat_history = []
                st.rerun()

    # --- MAIN CONTENT ---
    if st.session_state.authenticated:
        if st.session_state.user_type == "Customer":
            st.title("Welcome to Telecom Service Assistant")
            tab1, tab2, tab3 = st.tabs(["Chat Assistant", "My Account", "Network Status"])
            
            with tab1:
                st.header("Chat with our AI Assistant")
                for message in st.session_state.chat_history:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])
                
                if prompt := st.chat_input("How can I help you today?"):
                    st.session_state.chat_history.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.write(prompt)
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            response = process_query(prompt)
                            st.write(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})

            with tab2:
                st.header("My Account")
                st.write("Standard Plan (STD_500)")
            with tab3:
                st.header("Network Status")
                st.info("System Normal")

if __name__ == "__main__":
    main()