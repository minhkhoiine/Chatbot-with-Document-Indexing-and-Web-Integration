# server_app.py
from llama_index.core import StorageContext, load_index_from_storage
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import FastAPI
import uvicorn
import os

class Query(BaseModel):
    question: str

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
print(api_key[:6] if api_key else "No API key")


storage = StorageContext.from_defaults(persist_dir="faq_index")
index = load_index_from_storage(storage)
engine = index.as_query_engine()

app = FastAPI()

# Healthcheck
@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/query")
async def query(q: Query):
    result = engine.query(q.question)
    return {"answer": str(result)}

@app.post("/")
async def query_root(q: Query):
    return await query(q)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
