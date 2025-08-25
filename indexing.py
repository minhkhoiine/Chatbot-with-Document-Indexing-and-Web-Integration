# indexing.py
from pathlib import Path
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

DATA_DIR = Path("/Users/khoivu/Desktop/chatbot/pdf")            
STORAGE_DIR = Path("faq_index")   
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

Settings.embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)

def build_or_load_index():
    if STORAGE_DIR.exists():
        storage_context = StorageContext.from_defaults(persist_dir=str(STORAGE_DIR))
        return load_index_from_storage(storage_context)
    
    documents = SimpleDirectoryReader(str(DATA_DIR)).load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=str(STORAGE_DIR))
    return index

if __name__ == "__main__":
    index = build_or_load_index()
    print("✅ Index ready, stored in", STORAGE_DIR)
