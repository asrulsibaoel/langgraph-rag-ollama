# frontend.py
import re
import streamlit as st
import requests

API_URL = "http://localhost:8000/chat/stream"

st.set_page_config(page_title="LangGraph RAG Chat", layout="wide")
st.title("💬 LangGraph RAG Chat")

# --- Helper to split visible text & thinking text ---


def split_thinking(text: str):
    """
    Returns (visible_text, thinking_text) from the model's output.
    """
    match = re.search(r"<think>(.*?)</think>", text, flags=re.DOTALL)
    thinking_text = match.group(1).strip() if match else None
    visible_text = re.sub(r"<think>.*?</think>", "",
                          text, flags=re.DOTALL).strip()
    return visible_text, thinking_text


# --- Session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display history ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            visible, thinking = split_thinking(msg["content"])
            st.markdown(visible)
            if thinking:
                with st.expander("🤔 Thinking process"):
                    st.markdown(thinking)
        else:
            st.markdown(msg["content"])

# --- User input ---
if user_input := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        streamed_text = ""

        try:
            with requests.post(API_URL, json={"message": user_input}, stream=True) as r:
                r.raise_for_status()

                for chunk in r.iter_content(chunk_size=None):
                    if chunk:
                        streamed_text += chunk.decode("utf-8")
                        visible, thinking = split_thinking(streamed_text)
                        display = visible
                        if thinking:
                            display += f"\n\n<details><summary>🤔 Thinking process</summary>\n\n{thinking}\n</details>"
                        message_placeholder.markdown(display + "▌")

            visible, thinking = split_thinking(streamed_text)
            final_display = visible
            if thinking:
                with st.expander("🤔 Thinking process"):
                    st.markdown(thinking)

            message_placeholder.markdown(visible)
            st.session_state.messages.append(
                {"role": "assistant", "content": streamed_text})

        except requests.RequestException as e:
            st.error(f"Error: {e}")
