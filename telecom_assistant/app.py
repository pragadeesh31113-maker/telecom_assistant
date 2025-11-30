import streamlit as st
import os
import sys
from pathlib import Path

# Add the current directory to sys.path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the Streamlit UI
from ui.streamlit_app import main

if __name__ == "__main__":
    main()
