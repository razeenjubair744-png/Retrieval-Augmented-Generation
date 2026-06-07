# Document RAG System

An advanced, modern Retrieval-Augmented Generation (RAG) system built with LangChain, LangGraph, and Gradio. This application allows you to converse with your own custom documents (PDF, Markdown, TXT) and predefined URLs using AI-powered semantic search.

## Features
- **Dynamic Gradio Interface**: A pristine, Claude-inspired frontend with custom advanced configurations.
- **Multi-format Support**: Upload PDFs, TXTs, or Markdown files easily.
- **Advanced Processing**: Granular control over text Chunk Size and Chunk Overlap natively built into the UI.
- **Source Citations**: AI responses include the exact excerpted document text that informed the answer.

## Setup Instructions

### 1. Requirements
This project uses `uv` for lightning-fast package and environment management. 
Python 3.12 is highly recommended.

### 2. Installation
Clone the repository, navigate into the project directory, and run the following command to automatically create a virtual environment and sync the dependencies:
```bash
uv sync
```

### 3. Environment Variables
You must provide an OpenAI API key to power the RAG system.
Create a `.env` file in the root directory:
```bash
touch .env
```
Inside `.env`, add your OpenAI API key:
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 4. Running the Application
Launch the Gradio server by running:
```bash
uv run python gradio_app.py
```
Then, open the local URL provided in your terminal (usually `http://127.0.0.1:7860`) in your web browser.

## Customization
You can modify the default URLs the system checks by editing `src/config/config.py`.
