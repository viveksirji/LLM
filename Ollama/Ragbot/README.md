# Ragbot

Ragbot is a local retrieval-augmented generation (RAG) chatbot. It can run in
the terminal or in a Streamlit browser interface, and uses Ollama for both
document search embeddings and answer generation.

## What is RAG?

A normal language-model chatbot answers from information learned during
training and the conversation. RAG adds a document search step:

1. **Read:** Ragbot extracts text from PDF, TXT, and Markdown files.
2. **Chunk:** It splits that text into overlapping passages.
3. **Embed:** Ollama's `nomic-embed-text` model turns each passage into a
   numeric vector representing its meaning.
4. **Retrieve:** When you ask a question, Ragbot embeds it and compares its
   vector with the passage vectors using cosine similarity. The four closest
   passages are selected.
5. **Generate:** The `llama3.2:1b` chat model receives the question and those
   passages, then generates an answer. Ragbot asks it to say when the
   documents don't contain the answer.

The embedding model is not the chat model: both are needed. Ragbot currently
keeps the index in memory and rebuilds it at startup or when requested. It
does not use a vector database.

## Requirements

- Windows 10 or 11
- Python 3.10 or newer
- Ollama installed and running
- Ollama models `llama3.2:1b` and `nomic-embed-text`
- Python packages from `Ollama\requirements.txt`
- PDF, TXT, or Markdown documents (PDFs must contain extractable text; scanned
  image-only PDFs need OCR, which this project does not currently provide)

From the repository root (`E:\LLM`), install the shared Python packages:

```powershell
.\Ollama\.venv\Scripts\python.exe -m pip install -r .\Ollama\requirements.txt
```

Download the embedding model once if you have not already:

```powershell
ollama pull nomic-embed-text
```

The chat model is `llama3.2:1b`. Download it if needed:

```powershell
ollama pull llama3.2:1b
```

## Add your documents

Copy supported documents directly into:

```text
E:\LLM\Ollama\Ragbot\documents
```

The current indexer reads files in that folder, not nested subfolders.
Documents are intentionally excluded from Git so private or copyrighted
material is not published with the source code.

## Run in Streamlit

From `E:\LLM` in PowerShell:

```powershell
Set-Location .\Ollama\Ragbot
E:\LLM\Ollama\.venv\Scripts\python.exe -m streamlit run .\streamlit_app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.
Indexing starts when the app opens. Once it finishes, enter a question in the
chat box. Use **Re-index documents** after adding or changing a document; this
rebuilds the index and clears the current chat. Use **New chat** to clear the
conversation without re-indexing. Stop Streamlit with `Ctrl+C` in its
PowerShell terminal.

## Run in the terminal

From `E:\LLM` in PowerShell:

```powershell
Set-Location .\Ollama\Ragbot
E:\LLM\Ollama\.venv\Scripts\python.exe .\ragbot.py
```

The terminal version indexes documents at startup. Enter questions at the
`You:` prompt. Type `:reload` to rebuild the index and clear conversation
history, or `:quit` to exit.

## Code walkthrough

### `ragbot.py`: shared retrieval and answer logic

- **Imports:** `pathlib` locates the documents directory; `dataclasses`
  defines a chunk record; `math` is used for cosine similarity. `pypdf`
  extracts PDF page text. `ollama` calls the local models, and `httpx` errors
  are handled by the terminal interface.
- **Configuration constants:** `CHAT_MODEL` and `EMBEDDING_MODEL` select the
  two Ollama models. `DOCUMENTS_DIR` points beside the Python file. The
  remaining constants set chunk length, overlap, result count, and embedding
  batch size.
- **`DocumentChunk`:** A frozen record containing a source filename, chunk
  number, passage text, and its embedding vector.
- **`read_document`:** Uses `pypdf` for PDFs and UTF-8 text decoding for TXT
  and Markdown.
- **`split_into_chunks`:** Breaks extracted text into passages up to 900
  characters, preferring a nearby line break and overlapping adjacent
  passages by 120 characters to preserve context.
- **`cosine_similarity`:** Validates vector dimensions and lengths, then
  scores how closely two vectors point in the same direction.
- **`build_index`:** Finds supported files in the documents directory,
  extracts and chunks each file, then requests embeddings from Ollama in
  batches of 32. The returned list is the in-memory search index. File and
  embedding problems are surfaced to the calling interface.
- **`retrieve`:** Embeds a question, scores every indexed passage against it,
  sorts by similarity, and returns up to four most relevant chunks.
- **`answer_question`:** Formats retrieved passages as context, includes chat
  history, calls the chat model, and returns both the answer and matched
  chunks so the interfaces can display their source filenames.
- **`main`:** Implements the terminal experience: build the index, read
  questions, support `:reload` and `:quit`, call the shared answer function,
  and report connection or model errors.
- **Main guard:** Runs the terminal loop only when `ragbot.py` is executed
  directly. This lets Streamlit import the shared functions without starting
  a second terminal interface.

### `streamlit_app.py`: browser interface

- **Imports:** Loads Streamlit and the local Ollama/HTTP error types, then
  imports the shared models, document path, index type, and RAG functions
  from `ragbot.py`.
- **Page setup and session state:** Sets the page title and icon. The index
  and message history are stored in `st.session_state`, so they survive
  Streamlit reruns in the current browser session.
- **`load_index`:** Calls `build_index` and displays document, Ollama model,
  and connection errors in the page instead of silently hiding them.
- **Sidebar:** Shows the model names and documents folder, lists supported
  files, and provides **Re-index documents** and **New chat** controls.
  Re-indexing rebuilds the embeddings and clears history if successful.
- **Initial indexing:** If this Streamlit session has no index yet, it builds
  one and shows a spinner while document text is embedded.
- **Chat history display:** Re-renders previous user and assistant messages
  after Streamlit reruns, including source filenames for assistant replies.
- **Question handling:** Disables the chat box until indexing succeeds. For a
  question, it calls `answer_question`, shows a spinner, renders the answer
  and source filenames, and stores the exchange in session state.

## Project files

```text
Ollama/
├── requirements.txt       # Shared Python dependencies, including pypdf
└── Ragbot/
    ├── documents/         # Local input documents; ignored by Git
    ├── ragbot.py           # Shared RAG functions and terminal interface
    ├── streamlit_app.py    # Streamlit browser interface
    ├── README.md           # Project overview and code walkthrough
    └── Ragbot_Guide.md     # Setup commands and development log
```

## Current limitations

- Indexing is in memory and is rebuilt for each new process or Streamlit
  session; large document collections may take time to embed.
- Only files directly inside `documents` are indexed.
- The supported file types are PDF, TXT, and Markdown.
- Image-only scanned PDFs are not OCR'd.
- Retrieval uses cosine similarity over all chunks, without a persistent
  vector database.
- Answers depend on the quality and relevance of the retrieved passages.

See [Ragbot_Guide.md](./Ragbot_Guide.md) for the setup command log and
development milestones.
