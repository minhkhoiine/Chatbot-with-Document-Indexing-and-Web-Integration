# Chatbot-with-Document-Indexing-and-Web-Integration
readme = r"""# PhuongCong Supply — Chatbot + Landing (FastAPI)

A tiny full-stack setup for a storefront landing page (`index.html`) and a grounded FAQ chatbot (`client.py`) using **FastAPI** and the **OpenAI Responses API**. Retrieval is done via a separate FAQ service (`/query`) that returns context for answers.

> This repo started from the “NailPro/PhuongCong” demo. It’s production-ready enough for a single instance on a VM (EC2/Render/Fly) and easy to extend.
> http://3.14.88.21:8080

---

## ✨ Features
- **Landing page** at `/` with a CTA → goes to `/chat`
- **Chat UI** at `/chat` posting to `/ask`
- **Grounded answers**: the model must answer **only** from context returned by your FAQ service (`FAQ_URL`)
- Clean HTML/CSS (no framework) and single-file FastAPI backend
- Works locally or on a server; no hard-coded host/port in links
- Easy to plug in your own retriever/indexer

---

## 🧱 Architecture
flowchart LR
  U[User Browser] -->|GET /| FE[index.html (Landing)]
  U -->|Click "Chat with us"| CHAT[/chat (FastAPI view)/]

  subgraph APP [FastAPI app - client.py (port 5000)]
    CHAT -->|POST /ask (Form)| ASK[Handler /ask]
    ASK -->|httpx POST| FAQ[(FAQ Service /query @8000)]
    ASK -->|OpenAI Responses API| OAI[(OpenAI API)]
    ASK --> RESP[Response Page]
  end

  FE -->|href "/chat"| CHAT
  RESP -->|Link /| FE

  subgraph FAQS [FAQ Index Service (port 8000)]
    FAQ -->|Retrieve context| IDX[(faq_index / DB / files)]
    IDX --> FAQ
  end

<img width="2056" height="1329" alt="Screenshot 2025-09-01 at 11 01 00" src="https://github.com/user-attachments/assets/bc59b0e7-c5e7-4687-9793-0824ce6fe6c0" />
<img width="2056" height="1329" alt="Screenshot 2025-09-01 at 11 00 32" src="https://github.com/user-attachments/assets/1faa0fb9-d3d7-4daa-834e-eab18cf2a5bd" />
<img width="2056" height="1329" alt="Screenshot 2025-09-01 at 11 00 05" src="https://github.com/user-attachments/assets/770a5782-4e43-439f-b0e2-fb3b0c74e829" />
