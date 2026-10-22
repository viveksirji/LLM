from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import httpx
import ollama
from pypdf import PdfReader
from pypdf.errors import PdfReadError


CHAT_MODEL = "llama3.2:1b"
EMBEDDING_MODEL = "nomic-embed-text"
DOCUMENTS_DIR = Path(__file__).parent / "documents"
CHUNK_SIZE = 900
CHUNK_OVERLAP = 120
RESULTS_COUNT = 4
EMBEDDING_BATCH_SIZE = 32


@dataclass(frozen=True)
class DocumentChunk:
    source: str
    number: int
    text: str
    embedding: list[float]


def read_document(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return path.read_text(encoding="utf-8")


def split_into_chunks(text: str) -> list[str]:
    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        if end < len(text):
            paragraph_end = text.rfind("\n", start + CHUNK_SIZE // 2, end)
            if paragraph_end > start:
                end = paragraph_end

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = max(end - CHUNK_OVERLAP, start + 1)

    return chunks


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Embedding vectors have different dimensions.")

    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        raise ValueError("An embedding vector has zero length.")

    return sum(a * b for a, b in zip(left, right)) / (left_norm * right_norm)


def build_index() -> list[DocumentChunk]:
    paths = sorted(
        path
        for path in DOCUMENTS_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in {".txt", ".md", ".pdf"}
    )
    if not paths:
        raise FileNotFoundError(
            f"No PDF, TXT, or Markdown documents found in {DOCUMENTS_DIR}."
        )

    pending: list[tuple[str, int, str]] = []
    for path in paths:
        try:
            text = read_document(path)
        except (OSError, UnicodeError, ValueError, PdfReadError) as exc:
            raise RuntimeError(f"Could not read {path.name}: {exc}") from exc
        chunks = split_into_chunks(text)
        if not chunks:
            raise ValueError(f"No readable text found in {path.name}.")
        pending.extend((path.name, number, chunk) for number, chunk in enumerate(chunks, 1))

    indexed: list[DocumentChunk] = []
    for start in range(0, len(pending), EMBEDDING_BATCH_SIZE):
        batch = pending[start : start + EMBEDDING_BATCH_SIZE]
        response = ollama.embed(
            model=EMBEDDING_MODEL,
            input=[text for _, _, text in batch],
        )
        if len(response.embeddings) != len(batch):
            raise RuntimeError("Ollama returned an unexpected number of embeddings.")
        indexed.extend(
            DocumentChunk(source, number, text, embedding)
            for (source, number, text), embedding in zip(batch, response.embeddings)
        )

    return indexed


def retrieve(index: list[DocumentChunk], question: str) -> list[DocumentChunk]:
    response = ollama.embed(model=EMBEDDING_MODEL, input=question)
    if not response.embeddings:
        raise RuntimeError("Ollama returned no embedding for the question.")
    query_embedding = response.embeddings[0]
    return sorted(
        index,
        key=lambda chunk: cosine_similarity(query_embedding, chunk.embedding),
        reverse=True,
    )[:RESULTS_COUNT]


def answer_question(
    question: str,
    index: list[DocumentChunk],
    history: list[dict[str, str]],
) -> tuple[str, list[DocumentChunk]]:
    matches = retrieve(index, question)
    context = "\n\n".join(
        f"[{chunk.source}, chunk {chunk.number}]\n{chunk.text}"
        for chunk in matches
    )
    messages = [
        {
            "role": "system",
            "content": (
                "Answer using the retrieved document context. If it does not "
                "contain the answer, say you could not find it in the documents. "
                "Do not invent facts or citations."
            ),
        },
        *history,
        {
            "role": "user",
            "content": f"Question: {question}\n\nRetrieved document context:\n{context}",
        },
    ]
    response = ollama.chat(model=CHAT_MODEL, messages=messages)
    return response.message.content, matches


def main() -> int:
    print(f"PandeyBot RAG | chat: {CHAT_MODEL} | embeddings: {EMBEDDING_MODEL}")
    print(f"Reading documents from: {DOCUMENTS_DIR}")

    try:
        index = build_index()
    except (FileNotFoundError, RuntimeError, ValueError, ollama.ResponseError) as exc:
        print(f"Could not build the document index: {exc}")
        return 1
    except httpx.RequestError as exc:
        print(f"Could not connect to Ollama. Make sure Ollama is running: {exc}")
        return 1

    print(f"Indexed {len(index)} chunks. Type :reload, :quit, or ask a question.")
    history: list[dict[str, str]] = []

    while True:
        try:
            question = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return 0

        if not question:
            continue
        if question.lower() in {":quit", ":q", "exit"}:
            print("Goodbye.")
            return 0
        if question.lower() == ":reload":
            try:
                index = build_index()
            except (FileNotFoundError, RuntimeError, ValueError, ollama.ResponseError) as exc:
                print(f"Could not reload the document index: {exc}")
                continue
            except httpx.RequestError as exc:
                print(f"Could not connect to Ollama. Make sure Ollama is running: {exc}")
                continue
            history.clear()
            print(f"Re-indexed {len(index)} chunks; chat history cleared.")
            continue

        try:
            answer, matches = answer_question(question, index, history)
        except ollama.ResponseError as exc:
            print(f"Ollama could not answer: {exc.error}")
            continue
        except httpx.RequestError as exc:
            print(f"Could not connect to Ollama. Make sure Ollama is running: {exc}")
            continue
        except ValueError as exc:
            print(f"Could not retrieve document context: {exc}")
            continue

        print(f"\nPandeyBot: {answer}")
        print("Sources: " + ", ".join(sorted({chunk.source for chunk in matches})))
        history.extend(
            [
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer},
            ]
        )


if __name__ == "__main__":
    raise SystemExit(main())
