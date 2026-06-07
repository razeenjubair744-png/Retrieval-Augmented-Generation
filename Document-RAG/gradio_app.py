"""Gradio UI for Agentic RAG System - Modernized Version."""

import os
import sys
import time
from pathlib import Path
from typing import Optional, Tuple, List

import gradio as gr

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.config.config import Config
from src.document_ingestion.document_processor import DocumentProcessor
from src.vectorstore.vectorstore import VectorStore
from src.graph_builder.graph_builder import GraphBuilder


def initialize_rag_with_urls() -> Tuple[object, int, str]:
    """Initialize the RAG system with default URLs."""
    try:
        if not Config.OPENAI_API_KEY:
            return None, 0, "❌ OpenAI API key not found. Please set OPENAI_API_KEY in your .env file."

        llm = Config.get_llm()
        doc_processor = DocumentProcessor(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        vector_store = VectorStore()

        urls = Config.DEFAULT_URLS
        documents = doc_processor.process_urls(urls)

        if not documents:
            return None, 0, "No documents found in URLs."

        vector_store.create_vectorstore(documents)

        graph_builder = GraphBuilder(
            retriever=vector_store.get_retriever(),
            llm=llm
        )
        graph_builder.build()

        return graph_builder, len(documents), f"✅ System ready! ({len(documents)} chunks loaded from Default URLs)"
    except Exception as e:
        return None, 0, f"❌ Failed to initialize with URLs: {str(e)}"


def initialize_rag_with_files(uploaded_files, chunk_size: int, chunk_overlap: int) -> Tuple[object, int, str]:
    """Initialize the RAG system with uploaded files."""
    try:
        if not uploaded_files:
            return None, 0, "No files uploaded."

        llm = Config.get_llm()
        doc_processor = DocumentProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        vector_store = VectorStore()

        all_documents = []

        for file_obj in uploaded_files:
            file_path = file_obj.name
            
            # Process based on file type
            if file_path.lower().endswith('.pdf'):
                documents = doc_processor.process_pdf(file_path)
            else:
                documents = doc_processor.process_file(file_path)

            all_documents.extend(documents)

        if not all_documents:
            return None, 0, "No documents extracted from files."

        vector_store.create_vectorstore(all_documents)

        graph_builder = GraphBuilder(
            retriever=vector_store.get_retriever(),
            llm=llm
        )
        graph_builder.build()

        return graph_builder, len(all_documents), f"✅ Files processed! ({len(all_documents)} chunks loaded from Custom Files)"
    except Exception as e:
        return None, 0, f"❌ Failed to initialize with files: {str(e)}"


def answer_question(rag_system, history: list, question: str):
    """Answer a question using the RAG system and update chat history."""
    if not rag_system:
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": "⚠️ System is not initialized. Please load documents first."})
        return history, "", "System not ready", "N/A"

    if not question.strip():
        return history, "", "Please enter a valid question.", "N/A"

    start_time = time.time()
    try:
        result = rag_system.run(question)
        elapsed_time = time.time() - start_time
        
        answer = result.get('answer', 'No answer generated')
        docs = result.get('retrieved_docs', [])
        
        # Format the retrieved docs for the accordion
        docs_text = ""
        for i, doc in enumerate(docs, 1):
            content = doc.page_content
            display_text = content[:500] + "..." if len(content) > 500 else content
            docs_text += f"### Document {i}\n{display_text}\n\n---\n\n"

        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})

        return history, "", docs_text, f"{elapsed_time:.2f}s"
    except Exception as e:
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": f"❌ Search failed: {str(e)}"})
        return history, "", f"Error: {str(e)}", "N/A"


# Define Claude-like Theme
claude_theme = gr.themes.Base(
    primary_hue="zinc",
    secondary_hue="stone",
    neutral_hue="stone",
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
).set(
    body_background_fill="#fcfcfc",
    body_background_fill_dark="#fcfcfc",
    body_text_color="#1a1a1a",
    body_text_color_dark="#1a1a1a",
    block_background_fill="#ffffff",
    block_background_fill_dark="#ffffff",
    block_border_width="1px",
    block_border_color="#e5e5e5",
    block_border_color_dark="#e5e5e5",
    block_shadow="0 1px 2px 0 rgba(0, 0, 0, 0.03)",
    block_shadow_dark="0 1px 2px 0 rgba(0, 0, 0, 0.03)",
    block_radius="12px",
    button_primary_background_fill="#1a1a1a",
    button_primary_background_fill_dark="#1a1a1a",
    button_primary_text_color="#ffffff",
    button_primary_text_color_dark="#ffffff",
    button_primary_background_fill_hover="#333333",
    button_primary_background_fill_hover_dark="#333333",
    button_secondary_background_fill="#f3f4f6",
    button_secondary_background_fill_dark="#f3f4f6",
    button_secondary_background_fill_hover="#e5e7eb",
    button_secondary_background_fill_hover_dark="#e5e7eb",
    border_color_primary="#e5e5e5",
    border_color_primary_dark="#e5e5e5",
    background_fill_secondary="#f9fafb",
    background_fill_secondary_dark="#f9fafb",
    color_accent_soft="#f3f4f6",
    color_accent_soft_dark="#f3f4f6",
    panel_background_fill="#ffffff",
    panel_background_fill_dark="#ffffff",
    input_background_fill="#ffffff",
    input_background_fill_dark="#ffffff",
)

custom_css = """
/* Make the chat bubbles look like Claude */
.message.user {
    background-color: #f3f4f6 !important;
    border-color: #e5e7eb !important;
    color: #111827 !important;
}
.message.bot {
    background-color: transparent !important;
    border-color: transparent !important;
}
/* Force text colors in case Gradio dark mode classes bleed through */
.gradio-container {
    max-width: 1200px !important;
    color: #1a1a1a !important;
}
.markdown-text {
    color: #1a1a1a !important;
}
.markdown-text h1, .markdown-text h2, .markdown-text h3 {
    color: #111827 !important;
}
"""

with gr.Blocks(title="🤖 RAG Document Search") as app:
    # State variables
    rag_system_state = gr.State(None)
    
    gr.Markdown(
        """
        # 🤖 RAG Document Search
        *Ask questions about your documents with AI-powered retrieval*
        """
    )
    
    with gr.Row():
        # LEFT COLUMN: Configuration
        with gr.Column(scale=1):
            gr.Markdown("## ⚙️ Configuration")
            
            with gr.Tabs():
                with gr.TabItem("📚 Default Documents"):
                    gr.Markdown("Load predefined URLs configured in your environment.")
                    load_url_btn = gr.Button("🔄 Load Default Documents", variant="primary")
                
                with gr.TabItem("📤 Custom Files"):
                    gr.Markdown("Upload your custom documents and configure processing parameters.")
                    
                    with gr.Accordion("⚙️ Advanced Processing Options", open=False):
                        chunk_size = gr.Slider(minimum=100, maximum=2000, value=Config.CHUNK_SIZE, step=100, label="Chunk Size", info="Number of characters per chunk.")
                        chunk_overlap = gr.Slider(minimum=0, maximum=500, value=Config.CHUNK_OVERLAP, step=10, label="Chunk Overlap", info="Overlap between consecutive chunks.")
                    
                    file_input = gr.File(label="Choose files to upload", file_types=[".pdf", ".txt", ".md"], file_count="multiple")
                    process_file_btn = gr.Button("🚀 Process Files", variant="primary")
            
            status_box = gr.Markdown("### 📊 System Status\n**Status:** Not Initialized")
            
        # RIGHT COLUMN: Chat Interface
        with gr.Column(scale=2):
            gr.Markdown("## 💬 Chat Interface")
            
            chatbot = gr.Chatbot(height=500)
            
            with gr.Row():
                question_input = gr.Textbox(placeholder="What would you like to know about the documents?", label="Your question:", scale=4)
                search_btn = gr.Button("🔍 Search", variant="primary", scale=1)
                
            with gr.Row():
                time_display = gr.Textbox(label="Response Time", interactive=False)
                
            with gr.Accordion("📄 Source Documents", open=False):
                source_docs_display = gr.Markdown("Retrieved documents will appear here.")
    
    # Event Handlers
    def handle_load_urls():
        rag_sys, count, msg = initialize_rag_with_urls()
        return rag_sys, f"### 📊 System Status\n**Status:** {msg}"
        
    def handle_load_files(files, c_size, c_overlap):
        rag_sys, count, msg = initialize_rag_with_files(files, c_size, c_overlap)
        return rag_sys, f"### 📊 System Status\n**Status:** {msg}"
    
    load_url_btn.click(
        fn=handle_load_urls,
        inputs=[],
        outputs=[rag_system_state, status_box]
    )
    
    process_file_btn.click(
        fn=handle_load_files,
        inputs=[file_input, chunk_size, chunk_overlap],
        outputs=[rag_system_state, status_box]
    )
    
    # Handle chat submission from button or pressing Enter
    submit_events = [search_btn.click, question_input.submit]
    for event in submit_events:
        event(
            fn=answer_question,
            inputs=[rag_system_state, chatbot, question_input],
            outputs=[chatbot, question_input, source_docs_display, time_display]
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.launch(theme=claude_theme, css=custom_css, server_name="0.0.0.0", server_port=port)
