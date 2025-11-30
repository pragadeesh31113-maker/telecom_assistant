import streamlit as st

def sidebar_info():
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This assistant is powered by:
        - **LangGraph**: Orchestration
        - **CrewAI**: Billing & Service Agents
        - **AutoGen**: Network Troubleshooting
        - **LangChain**: General Support
        """)
        st.divider()
        st.caption("Version 1.0.0")

def chat_message(role, content):
    with st.chat_message(role):
        st.markdown(content)
