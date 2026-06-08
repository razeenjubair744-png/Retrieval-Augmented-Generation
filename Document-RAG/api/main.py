from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
import tempfile
from pathlib import Path
import builtins
import uuid

# Fix any obscure 3rd-party missing import errors for uuid globally
builtins.uuid = uuid

# Fix python path since api is inside Document-RAG
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.config.config import Config
from src.document_ingestion.document_processor import DocumentProcessor
from src.vectorstore.vectorstore import VectorStore
from src.graph_builder.graph_builder import GraphBuilder

app = FastAPI(title="RAG Document Search API")

# Setup CORS for development React server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class RAGManager:
    def __init__(self):
        self.graph_builder = None
        self.doc_count = 0

rag_manager = RAGManager()

class ChatRequest(BaseModel):
    question: str
    history: List[dict] = []

@app.post("/api/init/urls")
async def init_urls():
    if not Config.OPENAI_API_KEY:
        raise HTTPException(status_code=400, detail="OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")
        
    try:
        llm = Config.get_llm()
        doc_processor = DocumentProcessor(chunk_size=Config.CHUNK_SIZE, chunk_overlap=Config.CHUNK_OVERLAP)
        vector_store = VectorStore()
        
        docs = doc_processor.process_urls(Config.DEFAULT_URLS)
        if not docs:
            raise HTTPException(status_code=400, detail="No documents found in URLs.")
            
        vector_store.create_vectorstore(docs)
        rag_manager.graph_builder = GraphBuilder(retriever=vector_store.get_retriever(), llm=llm)
        rag_manager.graph_builder.build()
        rag_manager.doc_count = len(docs)
        
        return {"message": f"System ready! ({len(docs)} chunks loaded from Default URLs)", "count": len(docs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize with URLs: {str(e)}")

@app.post("/api/init/files")
async def init_files(
    files: List[UploadFile] = File(...),
    chunk_size: int = Form(500),
    chunk_overlap: int = Form(50)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")
        
    try:
        llm = Config.get_llm()
        doc_processor = DocumentProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        vector_store = VectorStore()
        
        all_documents = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            for file in files:
                temp_path = Path(temp_dir) / file.filename
                with open(temp_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                if file.filename.lower().endswith('.pdf'):
                    documents = doc_processor.process_pdf(temp_path)
                else:
                    documents = doc_processor.process_file(temp_path)
                all_documents.extend(documents)
                
        if not all_documents:
            raise HTTPException(status_code=400, detail="No documents extracted from files.")
            
        vector_store.create_vectorstore(all_documents)
        rag_manager.graph_builder = GraphBuilder(retriever=vector_store.get_retriever(), llm=llm)
        rag_manager.graph_builder.build()
        rag_manager.doc_count = len(all_documents)
        
        return {"message": f"Files processed! ({len(all_documents)} chunks loaded from Custom Files)", "count": len(all_documents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize with files: {str(e)}")

@app.post("/api/chat")
async def chat(request: ChatRequest):
    if not rag_manager.graph_builder:
        raise HTTPException(status_code=400, detail="System not initialized. Please load documents first.")
        
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Please enter a valid question.")

    import time
    start_time = time.time()
    
    try:
        result = rag_manager.graph_builder.run(request.question)
        elapsed_time = time.time() - start_time
        
        answer = result.get('answer', 'No answer generated')
        docs = result.get('retrieved_docs', [])
        
        docs_text = ""
        for i, doc in enumerate(docs, 1):
            content = doc.page_content
            display_text = content[:500] + "..." if len(content) > 500 else content
            docs_text += f"### Document {i}\n{display_text}\n\n---\n\n"
            
        history = request.history.copy()
        history.append({"role": "user", "content": request.question})
        history.append({"role": "assistant", "content": answer})
        
        return {
            "answer": answer,
            "docs_text": docs_text,
            "history": history,
            "time": f"{elapsed_time:.2f}s"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# Mount static React frontend (only useful after running `npm run build` in frontend directory)
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists() and frontend_dist.is_dir():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
