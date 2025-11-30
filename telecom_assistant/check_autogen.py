import autogen
print("AutoGen imported successfully")
try:
    agent = autogen.UserProxyAgent(name="test", code_execution_config=False)
    print("UserProxyAgent created successfully")
except Exception as e:
    print(f"Error creating agent: {e}")
