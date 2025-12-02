from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

OPENAI_API_KEY = "YOUR_API_KEY_HERE"

class RequestBody(BaseModel):
    message: str

@app.post("/ask")
def ask_chatgpt(body: RequestBody):
    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Reply in pure Urdu only."},
            {"role": "user", "content": body.message}
        ]
    }

    result = requests.post(url, headers=headers, json=data).json()

    reply = result["choices"][0]["message"]["content"]
    return {"reply": reply}
