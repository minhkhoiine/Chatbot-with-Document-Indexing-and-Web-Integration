# -*- coding: utf-8 -*-
"""
Created on Thu May 16 21:54:23 2024

@author: Admin
"""
from pydantic import BaseModel 

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage

from dotenv import load_dotenv
import os

from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI

class Item(BaseModel):
    question: str 

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("API key: " + api_key[0:6])
else:
    print("API key not found")

storage_context = StorageContext.from_defaults(persist_dir = "ml_index")

index = load_index_from_storage(storage_context)

engine = index.as_query_engine()

app = FastAPI()

@app.post("/")
async def query(item: Item):
    result = engine.query(item.question)
    return(result)

if __name__ == "__main__":
    uvicorn.run("server:app", host = "127.0.0.1", port = 8000, reload = True)



