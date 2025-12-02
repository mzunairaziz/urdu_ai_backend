from fastapi import FastAPI
from pydantic import BaseModel
import requests
from typing import Dict, List

app = FastAPI()

# -------------------------
# 🔐 Gemini API Key (Free)
# -------------------------
GEMINI_API_KEY = "AIzaSyCDQ6oI6O7wK3RuLFDiGV0BZZ5kd4z6vx4"

# Conversation memory per user
conversations: Dict[str, List[Dict[str, str]]] = {}


# -------------------------
# 📌 Request Model
# -------------------------
class RequestBody(BaseModel):
    user_id: str
    message: str


# -------------------------
# 📌 Gemini Text Generation Function
# -------------------------
def ask_gemini(messages: List[Dict[str, str]]) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    # Prepare text prompt for Gemini
    full_prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])

    payload = {
        "contents": [
            {"parts": [{"text": full_prompt}]}
        ]
    }

    res = requests.post(url, json=payload).json()

    reply = res["candidates"][0]["content"]["parts"][0]["text"]
    return reply


# -------------------------
# 📌 Main Endpoint
# -------------------------
@app.post("/ask")
def ask_ai(body: RequestBody):

    user = body.user_id
    msg  = body.message.strip()

    if user not in conversations:
        conversations[user] = [
            {"role": "system", "content": "آپ ہمیشہ سادہ، واضح اور دوستانہ اردو میں جواب دیں۔"}
        ]

    # Add user message
    conversations[user].append({"role": "user", "content": msg})

    try:
        reply = ask_gemini(conversations[user])
    except:
        reply = "معذرت، مجھے جواب نہیں مل سکا۔"

    # Save assistant reply
    conversations[user].append({"role": "assistant", "content": reply})

    # Keep memory light
    if len(conversations[user]) > 20:
        conversations[user] = conversations[user][-20:]

    return {"reply": reply}


@app.get("/")
def home():
    return {"status": "running", "model": "gemini-1.5-flash"}
