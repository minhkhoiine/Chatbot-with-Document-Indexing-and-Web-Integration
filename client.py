# client.py
import os
from dotenv import load_dotenv
import httpx
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from openai import (
    OpenAI,
    RateLimitError,
    APIError,
    BadRequestError,
    APIConnectionError,
    AuthenticationError,
)

# --- Config & client ---
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
MODEL_ID = os.getenv("OPENAI_MODEL_ID", "gpt-5-nano-2025-08-07")
FAQ_URL = os.getenv("FAQ_URL", "http://127.0.0.1:8000/query")

client = OpenAI(api_key=API_KEY) if API_KEY else None
app = FastAPI(title="PhuongCong Chat Backend")

# --- Serve index.html as homepage ---
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(ROOT_DIR, "index.html")

@app.get("/", response_class=FileResponse)
@app.get("/home", response_class=FileResponse)
def homepage():
    return FileResponse(INDEX_PATH)

# --- UI: /chat page ---
@app.get("/chat", response_class=HTMLResponse)
def chat_page():
    return """
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <title>PhuongCong — Chat</title>
      <style>
        :root{--pri:#6C63FF}
        body{font-family:system-ui,Arial,sans-serif;margin:0;padding:28px;max-width:860px}
        h1{margin-top:0}
        textarea{width:100%;height:120px;font-size:16px;padding:10px}
        .btn{margin-top:12px;padding:10px 18px;border:0;background:var(--pri);color:#fff;border-radius:8px;cursor:pointer;text-decoration:none}
        .card{margin-top:18px;padding:14px;border:1px solid #eee;border-radius:10px;background:#fafafa}
        a{color:#fff}
        .row{display:flex;gap:10px;margin-top:14px}
      </style>
    </head>
    <body>
      <h1>💬 PhuongCong Chat</h1>
      <form action="/ask" method="post">
        <textarea name="message" placeholder="Type your question…"></textarea>
        <br/>
        <div class="row">
          <button class="btn" type="submit">Send</button>
          <a class="btn" href="/">🏠 Back to Homepage</a>
        </div>
      </form>
      <div class="card">Tip: ask “opening hours”</div>
    </body>
    </html>
    """

# --- Helper: fetch context from FAQ index ---
def fetch_index_answer(question: str) -> str:
    try:
        r = httpx.post(FAQ_URL, json={"question": question}, timeout=6.0)
        r.raise_for_status()
        data = r.json()
        return (data.get("answer") or "").strip()
    except Exception:
        return ""

# --- Action: /ask (Form POST) ---
@app.post("/ask", response_class=HTMLResponse)
def chat_ask(message: str = Form(...)):
    user_text = (message or "").strip()

    if not user_text:
        answer = "Please enter a message."
    elif client is None or not API_KEY:
        answer = "Missing OPENAI_API_KEY. Add it to your .env and restart."
    else:
        try:
            indexed = fetch_index_answer(user_text)

            system_prompt = (
                "You are a PhuongCong shop assistant. "
                "Answer ONLY using the provided context. "
                "If the context does not contain the answer, say you don't know "
                "and ask the user for the specific store/city."
            )
            user_prompt = f"Question: {user_text}\n\nContext:\n{indexed or '[no indexed context]'}"

            resp = client.responses.create(
                model=MODEL_ID,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]
            )
            answer = getattr(resp, "output_text", None) or str(resp)

        except AuthenticationError:
            answer = "Authentication error: bad or missing API key."
        except BadRequestError as e:
            answer = f"BadRequest: {getattr(e, 'message', str(e))}"
        except RateLimitError:
            answer = "Rate limited. Please wait a moment and try again."
        except APIConnectionError:
            answer = "Network error reaching the API. Please try again."
        except APIError as e:
            answer = f"API error: {getattr(e, 'message', str(e))}"
        except Exception as e:
            answer = f"Unexpected error: {e}"

    return f"""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <title>Response</title>
      <style>
        body{{font-family:system-ui,Arial,sans-serif;margin:0;padding:28px;max-width:860px}}
        .box{{padding:14px;border:1px solid #eee;border-radius:10px;margin:10px 0}}
        .you{{background:#f0f7ff}}
        .bot{{background:#fafafa}}
        .row{{display:flex;gap:10px;margin-top:14px}}
        .btn{{padding:10px 18px;border:0;background:#6C63FF;color:#fff;border-radius:8px;text-decoration:none}}
      </style>
    </head>
    <body>
      <h1>💬 PhuongCong Chat</h1>
      <div class="box you"><b>Bạn:</b><br>{user_text}</div>
      <div class="box bot"><b>Bot:</b><br>{answer}</div>
      <div class="row">
        <a class="btn" href="/">🏠 Back to Homepage</a>
        <a class="btn" href="/chat">⬅ Ask another question</a>
      </div>
    </body>
    </html>
    """

# Health check
@app.get("/health", response_class=HTMLResponse)
def health():
    return '<meta charset="utf-8"><p>✅ Backend is running. Try <a href="/">Home</a> or <a href="/chat">Chat</a>.</p>'
