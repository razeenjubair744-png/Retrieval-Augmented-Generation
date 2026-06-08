import sys
import traceback
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.config.config import Config
from src.document_ingestion.document_processor import DocumentProcessor
from src.vectorstore.vectorstore import VectorStore
from src.graph_builder.graph_builder import GraphBuilder

def test_run():
    print("Initializing...")
    llm = Config.get_llm()
    doc_processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
    
    with open("dummy.txt", "w") as f:
        f.write("Some dummy content with url https://example.com")
    docs = doc_processor.process_file(Path("dummy.txt"))
    
    vector_store = VectorStore()
    vector_store.create_vectorstore(docs)
    
    graph_builder = GraphBuilder(retriever=vector_store.get_retriever(), llm=llm)
    graph_builder.build()
    
    print("Running query...")
    try:
        result = graph_builder.run("What is in the urls?")
        print("Success:", result['answer'])
    except Exception as e:
        print("ERROR OCCURRED!")
        traceback.print_exc()

if __name__ == "__main__":
    test_run()
