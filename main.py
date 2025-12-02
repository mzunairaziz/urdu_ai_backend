from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests, time
from typing import Dict, List

app = FastAPI()

# -------------------------
# 🔐 Your API Key
# -------------------------
OPENAI_API_KEY = "YOUR_API_KEY_HERE"


# -------------------------
# 📌 In-Memory Conversation Store
# (Keeps messages per user)
# -------------------------
conversations: Dict[str, List[Dict[str, str]]] = {}


# -------------------------
# 📌 Request Model
# -------------------------
class RequestBody(BaseModel):
    user_id: str
    message: str


# -------------------------
# 📌 ChatGPT Helper Function
# -------------------------
def chatgpt_reply(messages: List[Dict[str, str]]) -> str:
    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": messages
    }

    res = requests.post(url, headers=headers, json=payload).json()
    return res["choices"][0]["message"]["content"]


# -------------------------
# 📌 Main AI Endpoint
# -------------------------
@app.post("/ask")
def ask_ai(body: RequestBody):

    user = body.user_id
    msg  = body.message.strip()

    # 1️⃣ Create session if new
    if user not in conversations:
        conversations[user] = [
            {"role": "system", "content": "آپ ہمیشہ اردو میں جواب دیں گے۔ بات چیت دوستانہ ہو۔"}
        ]

    # 2️⃣ Add user message
    conversations[user].append({"role": "user", "content": msg})

    try:
        # 3️⃣ Get reply
        reply = chatgpt_reply(conversations[user])

    except Exception as e:
        reply = "معذرت، سرور سے جواب موصول نہیں ہوسکا۔"

    # 4️⃣ Add assistant reply to memory
    conversations[user].append({"role": "assistant", "content": reply})

    # 5️⃣ Limit memory (avoid long chat history)
    if len(conversations[user]) > 20:
        conversations[user] = conversations[user][-20:]

    return {"reply": reply}


# -------------------------
# 📌 Health Check
# -------------------------
@app.get("/")
def home():
    return {"status": "running", "model": "gpt-4o-mini"}
