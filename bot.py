
import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=30
    )

def ask_ai(text):
    response = requests.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4.1-mini",
            "instructions": "Sen RAVSHANOV AI nomli yordamchisan. O'zbek tilida samimiy va tushunarli javob ber.",
            "input": text
        },
        timeout=60
    )
    response.raise_for_status()
    data = response.json()

    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                return content.get("text", "")

    return "Kechirasiz, javob tayyorlay olmadim."

@app.route("/")
def home():
    return "RAVSHANOV AI ishlayapti!"

@app.route("/telegram/" + os.environ["WEBHOOK_SECRET"], methods=["POST"])
def telegram():
    data = request.json or {}
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    if not chat_id or not text:
        return "OK"

    if text == "/start":
        send_message(
            chat_id,
            "Assalomu alaykum! 🤖 RAVSHANOV AI botiga xush kelibsiz!\nSavolingizni yozing."
        )
        return "OK"

    try:
        answer = ask_ai(text)
        send_message(chat_id, answer[:4000])
    except Exception:
        send_message(chat_id, "Hozir javob berishda xatolik yuz berdi. Keyinroq urinib ko'ring.")

    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    external_url = os.environ.get("RENDER_EXTERNAL_URL")

    if external_url:
        requests.post(
            f"{TELEGRAM_API}/setWebhook",
            json={
                "url": f"{external_url}/telegram/{WEBHOOK_SECRET}"
            },
            timeout=30
        )

    app.run(host="0.0.0.0", port=port)
