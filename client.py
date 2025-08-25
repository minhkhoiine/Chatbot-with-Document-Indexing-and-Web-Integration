# client.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from openai import OpenAI, RateLimitError, APIError

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY) if API_KEY else None

app = FastAPI(title="NailPro Chat Backend")

@app.get("/chat", response_class=HTMLResponse)
def chat_page():
    return """
    <!doctype html>
    <html lang="vi">
    <head>
      <meta charset="utf-8">
      <title>NailPro — Chat</title>
      <style>
        body{font-family:system-ui,Arial,sans-serif;margin:0;padding:28px;max-width:820px}
        h1{margin-top:0}
        textarea{width:100%;height:120px;font-size:16px;padding:10px}
        .btn{margin-top:12px;padding:10px 18px;border:0;background:#6C63FF;color:#fff;border-radius:8px;cursor:pointer}
        .card{margin-top:18px;padding:14px;border:1px solid #eee;border-radius:10px;background:#fafafa}
        a{color:#6C63FF;text-decoration:none}
      </style>
    </head>
    <body>
      <h1>💬 NailPro Chat</h1>
      <form method="post" action="/ask">
        <textarea name="message" placeholder="Nhập câu hỏi của bạn (VN/EN)..."></textarea><br/>
        <button class="btn" type="submit">Gửi</button>
      </form>
      <p class="card">Gợi ý: “Giới thiệu sản phẩm hot”, “Shop mở cửa giờ nào?”, “Tư vấn sơn gel cho móng yếu”.</p>
      <p><a href="http://127.0.0.1:8000/chat">Làm mới trang</a></p>
    </body>
    </html>
    """

@app.post("/ask", response_class=HTMLResponse)
def chat_ask(message: str = Form(...)):
    user_text = (message or "").strip()

    if not user_text:
        answer = "Please enter..."
    elif client is None:
        answer = "N/A"
    else:
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Bạn là trợ lý bán hàng thân thiện của NailPro. Trả lời ngắn gọn, ưu tiên tiếng Việt khi khách dùng tiếng Việt."},
                    {"role": "user", "content": user_text},
                ],
                temperature=0.3,
                max_tokens=300,
            )
            answer = resp.choices[0].message.content
        except RateLimitError:
            answer = "AI hết quota/billing. Vui lòng thử lại sau."
        except APIError as e:
            answer = f"Hệ thống đang bận ({e.__class__.__name__}). Thử lại nhé."

    return f"""
    <!doctype html>
    <html lang="vi">
    <head>
      <meta charset="utf-8">
      <title>Kết quả chat</title>
      <style>
        body{{font-family:system-ui,Arial,sans-serif;margin:0;padding:28px;max-width:820px}}
        .box{{padding:14px;border:1px solid #eee;border-radius:10px;margin:10px 0}}
        .you{{background:#f0f7ff}}
        .bot{{background:#fafafa}}
        a{{color:#6C63FF;text-decoration:none}}
        .btn{{display:inline-block;margin-top:12px;padding:8px 14px;background:#6C63FF;color:#fff;border-radius:8px}}
      </style>
    </head>
    <body>
      <h1>💬 NailPro Chat</h1>
      <div class="box you"><b>Bạn:</b><br>{user_text}</div>
      <div class="box bot"><b>Bot:</b><br>{answer}</div>
      <a class="btn" href="/chat">⬅ Hỏi tiếp</a>
    </body>
    </html>
    """

@app.get("/", response_class=HTMLResponse)
def root():
    return '<meta charset="utf-8"><p>✅ Chat backend đang chạy. Truy cập <a href="/chat">/chat</a> để trò chuyện.</p>'

#uvicorn client:app --reload --port 8000
