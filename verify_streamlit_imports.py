import sys
import os
from pathlib import Path

# Mimic streamlit_app.py path setup
# Assuming this script is run from project root, but let's simulate being in ui/
# We will just manually add the path as streamlit_app.py does

# In streamlit_app.py:
# current_file = Path(__file__).resolve()
# project_root = current_file.parent.parent.parent

# Here we are at root, so we just need to add current directory to path?
# No, streamlit_app.py adds the root to path.
# If I run this script from root, os.getcwd() is root.

project_root = os.getcwd()
sys.path.append(str(project_root))

print(f"Project root added to path: {project_root}")

try:
    print("Attempting imports...")
    from telecom_assistant.orchestration.graph import create_graph
    from telecom_assistant.utils.document_loader import process_uploaded_file
    print("✅ Imports successful!")
except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ An error occurred: {e}")
