
import streamlit as st
import logging

from ai_researcher_2 import INITIAL_PROMPT, graph, config
from langchain_core.messages import AIMessage
from generate_pdf import generate_pdf

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App configuration
st.set_page_config(page_title="Research AI Agent", page_icon="📄")
st.title("📄 Research AI Agent")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "latest_response" not in st.session_state:
    st.session_state.latest_response = ""

# Display previous conversation
for item in st.session_state.chat_history:
    if item["role"] in ("user", "assistant"):
        with st.chat_message(item["role"]):
            st.markdown(item["content"])

# Chat interface
user_input = st.chat_input("What research topic would you like to explore?")

if user_input:
    logger.info("User input received")

    st.session_state.chat_history.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    chat_input = {
        "messages": [
            {"role": "system", "content": INITIAL_PROMPT}
        ] + st.session_state.chat_history
    }

    logger.info("Starting agent processing...")
    full_response = ""

    with st.chat_message("assistant"):
        response_placeholder = st.empty()

        for s in graph.stream(
            chat_input, config, stream_mode="values"
        ):
            message = s["messages"][-1]

            # Log tool calls
            for tool_call in getattr(message, "tool_calls", []):
                logger.info("Tool call: %s", tool_call["name"])

            # Extract only readable text from AI messages
            if isinstance(message, AIMessage) and message.content:
                if isinstance(message.content, str):
                    text_content = message.content

                elif isinstance(message.content, list):
                    text_parts = []

                    for block in message.content:
                        if isinstance(block, dict):
                            if (
                                block.get("type") == "text"
                                and isinstance(block.get("text"), str)
                            ):
                                text_parts.append(block["text"])

                    text_content = "\n".join(text_parts)

                else:
                    text_content = ""

                if text_content.strip():
                    full_response = text_content
                    response_placeholder.markdown(full_response)

    # Save the final answer
    if full_response.strip():
        st.session_state.chat_history.append(
            {"role": "assistant", "content": full_response}
        )
        st.session_state.latest_response = full_response

# Download button
if st.session_state.latest_response.strip():
    pdf_bytes = generate_pdf(st.session_state.latest_response)

    st.download_button(
        label="📥 Download Research as PDF",
        data=pdf_bytes,
        file_name="research_result.pdf",
        mime="application/pdf",
        key="download_research_pdf",
    )
