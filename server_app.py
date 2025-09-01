# server_app.py
from typing import List, Dict, Any
import os
import uvicorn
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import FastAPI

from llama_index.core import (
    StorageContext,
    load_index_from_storage,
    Settings,
)

# ---- Config ----
PERSIST_DIR = os.getenv("FAQ_PERSIST_DIR", "faq_index")
TOP_K = int(os.getenv("FAQ_TOP_K", "3"))

# Do NOT let this service call an LLM. We only return retrieved text.
Settings.llm = None

# ---- Load index once ----
load_dotenv()
storage = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
index = load_index_from_storage(storage)

# Compact, snippet-like results; only retrieve (no synthesis)
engine = index.as_query_engine(
    similarity_top_k=TOP_K,
    response_mode="compact",
)

# ---- API ----
app = FastAPI()

class Query(BaseModel):
    question: str

@app.get("/")
def health():
    return {"status": "ok", "persist_dir": PERSIST_DIR, "top_k": TOP_K}

@app.post("/query")
def query(q: Query):
    """
    Returns short concatenated context in 'answer' and a 'sources' list
    with the top-k chunks + similarity scores. The client should pass
    'answer' as grounding context to its LLM call.
    """
    result = engine.query(q.question)

    # Main compact text (good as context)
    context_text = str(result).strip()

    # Collect sources (chunk text + score) for optional UI display/debugging
    sources: List[Dict[str, Any]] = []
    try:
        for node in getattr(result, "source_nodes", [])[:TOP_K]:
            # node.node.get_content() is the chunk text
            chunk = node.node.get_content() if hasattr(node, "node") else ""
            score = getattr(node, "score", None)
            sources.append({
                "score": float(score) if score is not None else None,
                "text": chunk[:800],  # keep it short
            })
    except Exception:
        pass

    return {
        "answer": context_text,
        "sources": sources,
    }

# Optional root alias
@app.post("/")
def query_root(q: Query):
    return query(q)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
