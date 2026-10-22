# Ragbot development guide

This guide records the commands and implementation updates for building a
local retrieval-augmented generation (RAG) chatbot in `Ollama\Ragbot`. The
existing PandeyBot in `Ollama\Chatbot` remains unchanged.

## What Ragbot uses

- `llama3.2:1b` (already installed) writes the answers.
- `nomic-embed-text` converts document passages and questions into vectors for
  semantic search. It is a separate, small Ollama model; the chat model does
  not replace the embedding model.
- PDF, TXT, and Markdown files are read from `Ragbot\documents`.
- Both terminal and Streamlit interfaces use the same RAG implementation.
  They build the index in memory; no vector database or remote service is used.
- `Ragbot\ragbot.py` chunks the files, retrieves the four closest chunks,
  passes those excerpts to the chat model, and prints the source filenames.
- `Ragbot\streamlit_app.py` provides the browser interface, a re-index button,
  and document source labels.

## Development log

### 1. Terminal RAG prototype

**Status:** Implemented. The separate `Ragbot` folder contains the terminal
chatbot and this guide. The PDF reader is installed in the shared environment.
PandeyBot's Streamlit app has not been changed.

The terminal workflow is: add documents, install requirements, download the
embedding model once, then run the Python script. Add `:reload` to re-index
documents during a running session, or `:quit` to exit.

### 2. Streamlit interface

**Status:** Implemented. The Streamlit interface uses the same indexing and
retrieval functions as the terminal chatbot. It loads documents when the app
starts, shows the indexed filenames, and provides a **Re-index documents**
button after files are added or changed. Chat history and the index are kept
in the current Streamlit session.

## Commands to set up and run

Run these commands in PowerShell from the repository root, `E:\LLM`.

### Install the added PDF reader

`pypdf` was added to the shared `Ollama\requirements.txt` for PDF extraction.
Install the updated shared requirements:

```powershell
python -m pip install -r .\Ollama\requirements.txt
```

If the shared environment is not active, use its interpreter directly:

```powershell
.\Ollama\.venv\Scripts\python.exe -m pip install -r .\Ollama\requirements.txt
```

### Download the embedding model once

The chat model `llama3.2:1b` is already installed. Download the additional
embedding model used for semantic retrieval:

```powershell
ollama pull nomic-embed-text
```

### Add documents and start the terminal chatbot

Copy `.pdf`, `.txt`, or `.md` files into `E:\LLM\Ollama\Ragbot\documents`.
Then run:

```powershell
Set-Location .\Ollama\Ragbot
python .\ragbot.py
```

If you are not using the shared environment, run it explicitly:

```powershell
E:\LLM\Ollama\.venv\Scripts\python.exe .\ragbot.py
```

While chatting, type `:reload` after adding or changing documents. Type
`:quit` or press `Ctrl+C` to exit.

### Run the Streamlit chatbot

In PowerShell, from the repository root, `E:\LLM`:

```powershell
Set-Location .\Ollama\Ragbot
E:\LLM\Ollama\.venv\Scripts\python.exe -m streamlit run .\streamlit_app.py
```

Streamlit prints a local URL (usually `http://localhost:8501`) to open in a
browser. Keep the terminal running while using the app. Stop it with `Ctrl+C`.
Copy new documents into `Ragbot\documents` and select **Re-index documents**
in the sidebar. This clears the current chat because its prior answers may
have depended on the old document index.

The existing `Ollama\Chatbot\app.py` remains unchanged.
