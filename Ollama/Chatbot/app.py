import httpx
import ollama
import streamlit as st


MODEL = "llama3.2:1b"
SYSTEM_PROMPT = (
    "You are a helpful chatbot. Keep answers concise by default, usually "
    "two to four short sentences. Use more detail only when the user asks."
)

st.set_page_config(page_title="PandeyBot", page_icon="💬")
st.title("PandeyBot")
st.caption(f"Chat locally with **{MODEL}** using Ollama.")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.subheader("Local model")
    st.write(f"`{MODEL}`")
    st.caption("Prompts are processed by Ollama on this computer.")
    if st.button("New chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Message the chatbot"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    conversation = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *st.session_state.messages,
    ]

    with st.chat_message("assistant"):
        try:
            chunks = ollama.chat(
                model=MODEL,
                messages=conversation,
                stream=True,
                options={"num_predict": 256},
            )

            def response_text():
                for chunk in chunks:
                    content = chunk.message.content
                    if content:
                        yield content

            answer = st.write_stream(response_text())
        except ollama.ResponseError as exc:
            st.error(f"Ollama could not answer: {exc.error}")
        except httpx.RequestError as exc:
            st.error(
                "Could not connect to the local Ollama service. Make sure "
                "Ollama is running, then try again."
            )
            st.caption(str(exc))
        else:
            if answer:
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
            else:
                st.warning("The model returned an empty response. Try again.")
