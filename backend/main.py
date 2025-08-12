# main.py
from fastapi import FastAPI
from backend.routes import chat

app = FastAPI(title="LangGraph Qwen3 + Milvus Chatbot")
app.include_router(chat.router)


@app.get("/")
def health():
    return {"status": "ok"}
