import httpx
import ollama
import streamlit as st

from ragbot import (
    CHAT_MODEL,
    DOCUMENTS_DIR,
    EMBEDDING_MODEL,
    DocumentChunk,
    answer_question,
    build_index,
)


st.set_page_config(page_title="PandeyBot RAG", page_icon="📚")
st.title("PandeyBot RAG")
st.caption("Ask questions grounded in your local documents.")

if "rag_index" not in st.session_state:
    st.session_state.rag_index = None
if "messages" not in st.session_state:
    st.session_state.messages = []


def load_index() -> list[DocumentChunk] | None:
    try:
        return build_index()
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        st.error(f"Could not build the document index: {exc}")
    except ollama.ResponseError as exc:
        st.error(f"Ollama could not build the document index: {exc.error}")
    except httpx.RequestError as exc:
        st.error(
            "Could not connect to Ollama. Make sure Ollama is running, "
            "then try again."
        )
        st.caption(str(exc))
    return None


with st.sidebar:
    st.subheader("Local models")
    st.write(f"Chat: `{CHAT_MODEL}`")
    st.write(f"Embeddings: `{EMBEDDING_MODEL}`")
    st.caption(f"Documents folder: `{DOCUMENTS_DIR}`")

    try:
        document_names = sorted(
            path.name
            for path in DOCUMENTS_DIR.iterdir()
            if path.is_file() and path.suffix.lower() in {".txt", ".md", ".pdf"}
        )
    except OSError as exc:
        st.error(f"Could not list documents: {exc}")
        document_names = []

    if document_names:
        st.caption("Documents")
        for name in document_names:
            st.write(f"- {name}")
    else:
        st.info("Add PDF, TXT, or Markdown files to the documents folder.")

    if st.button("Re-index documents", use_container_width=True):
        with st.spinner("Reading documents and creating embeddings..."):
            st.session_state.rag_index = load_index()
        if st.session_state.rag_index is not None:
            st.session_state.messages = []
            st.success(f"Indexed {len(st.session_state.rag_index)} chunks.")

    if st.button("New chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if st.session_state.rag_index is None:
    with st.spinner("Reading documents and creating embeddings..."):
        st.session_state.rag_index = load_index()

if st.session_state.rag_index is not None:
    st.caption(f"Indexed {len(st.session_state.rag_index)} document chunks.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            st.caption(f"Sources: {', '.join(message['sources'])}")

prompt = st.chat_input(
    "Ask a question about your documents",
    disabled=st.session_state.rag_index is None,
)
if prompt and st.session_state.rag_index is not None:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    history = [
        {"role": message["role"], "content": message["content"]}
        for message in st.session_state.messages[:-1]
    ]
    with st.chat_message("assistant"):
        try:
            with st.spinner("Searching documents and generating an answer..."):
                answer, matches = answer_question(
                    prompt,
                    st.session_state.rag_index,
                    history,
                )
        except ollama.ResponseError as exc:
            st.error(f"Ollama could not answer: {exc.error}")
        except httpx.RequestError as exc:
            st.error(
                "Could not connect to Ollama. Make sure Ollama is running, "
                "then try again."
            )
            st.caption(str(exc))
        except ValueError as exc:
            st.error(f"Could not retrieve document context: {exc}")
        else:
            st.markdown(answer)
            sources = sorted({chunk.source for chunk in matches})
            st.caption(f"Sources: {', '.join(sources)}")
            st.session_state.messages.append(
                {"role": "assistant", "content": answer, "sources": sources}
            )
