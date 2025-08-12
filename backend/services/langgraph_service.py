# services/langgraph_service.py
import uuid
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama

from backend.services.milvus_service import search_context
from backend.settings import settings

memory = MemorySaver()

model = ChatOllama(
    model="qwen3:8b",
    base_url=settings.ollama_url,
    temperature=0
)

app = create_react_agent(
    model,
    tools=[],
    checkpointer=memory
)


def stream_chat(user_message: str, thread_id: str = None):
    """Stream chat with Milvus context injection."""
    context = search_context(user_message, top_k=3)
    augmented_message = f"Context:\n{context}\n\nUser: {user_message}"

    if not thread_id:
        thread_id = str(uuid.uuid4())

    config = {"configurable": {"thread_id": thread_id}}
    input_message = HumanMessage(content=augmented_message)

    for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
        yield event["messages"][-1].content
