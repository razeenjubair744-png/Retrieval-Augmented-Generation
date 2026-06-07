import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.config.config import Config
from src.document_ingestion.document_processor import DocumentProcessor
from src.vectorstore.vectorstore import VectorStore
from src.graph_builder.graph_builder import GraphBuilder

print("Initializing...")
llm = Config.get_llm()
vector_store = VectorStore()
from langchain_core.documents import Document
print("Testing file upload pipeline...")
try:
    # Create a dummy file
    with open("dummy_test.txt", "w") as f:
        f.write("This is a dummy document for testing purposes.")
    
    class DummyFile:
        def __init__(self, name):
            self.name = name
            
    files = [DummyFile("dummy_test.txt")]
    from gradio_app import initialize_rag_with_files, answer_question
    
    rag_sys, count, msg = initialize_rag_with_files(files, 500, 50)
    print(msg)
    
    history = []
    history, _, docs_text, time_str = answer_question(rag_sys, history, "Tell something")
    print("History:", history)
except Exception as e:
    import traceback
    traceback.print_exc()
