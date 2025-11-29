import os
from flask import Flask, request, jsonify, send_from_directory
import requests
from dotenv import load_dotenv

# Load API key
load_dotenv()
API_KEY = os.getenv('OPENAI_API_KEY')

if not API_KEY:
    raise SystemExit("ERROR: Missing API key. Add it in .env as OPENAI_API_KEY=your_key")

# OpenAI API endpoint
OPENAI_URL = "https://api.openai.com/v1/chat/completions"

app = Flask(__name__, static_folder='static', static_url_path='')

# Basic system instructions
SYSTEM_PROMPT = "You are a helpful AI assistant. Reply clearly and simply."

def call_openai(messages):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",   # You can change to any model you have access to
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 200
    }

    res = requests.post(OPENAI_URL, json=payload, headers=headers)
    res.raise_for_status()
    data = res.json()
    return data["choices"][0]["message"]["content"]

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    body = request.json or {}
    user_msg = body.get("message", "")
    history = body.get("history", [])

    if user_msg.strip() == "":
        return jsonify({"error": "Empty message"}), 400

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history,
        {"role": "user", "content": user_msg}
    ]

    try:
        reply = call_openai(messages)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True, port=8000)
