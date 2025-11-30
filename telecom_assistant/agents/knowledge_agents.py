from llama_index.core import VectorStoreIndex
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector
from llama_index.llms.openai import OpenAI

# --- ABSOLUTE IMPORTS (FIXED) ---
from utils.document_loader import get_index
from config.config import LLM_MODEL
# --------------------------------

def create_knowledge_engine():
    """Create and return a LlamaIndex query engine for knowledge retrieval"""
    index = get_index()
    if not index:
        return None
        
    vector_query_engine = index.as_query_engine()
    
    query_engine_tools = [
        QueryEngineTool(
            query_engine=vector_query_engine,
            metadata=ToolMetadata(
                name="vector_tool",
                description="Useful for retrieving specific technical information from documentation."
            )
        )
    ]
    
    llm = OpenAI(model=LLM_MODEL)
    
    query_engine = RouterQueryEngine(
        selector=LLMSingleSelector.from_defaults(llm=llm),
        query_engine_tools=query_engine_tools
    )
    
    return query_engine

def process_knowledge_query(query):
    """Process a knowledge retrieval query using the LlamaIndex query engine"""
    try:
        engine = create_knowledge_engine()
        if not engine:
            return "Knowledge base is empty. Please upload documents."
            
        response = engine.query(query)
        return str(response)
    except Exception as e:
        return f"Error processing knowledge query: {str(e)}"