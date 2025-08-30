import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from db import get_conn, init_db

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'hook')
BASE_URL = os.getenv('BASE_URL')
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = Flask(__name__)
init_db()

# إعداد الويبهوك مرة واحدة (اختياري تنفيذه يدوياً بعد التشغيل)
@app.route('/set-webhook', methods=['POST'])
def set_webhook():
    url = f"{BASE_URL}/webhook/{WEBHOOK_SECRET}"
    r = requests.post(f"{TG_API}/setWebhook", json={"url": url})
    return jsonify(r.json())

# نقطة الويبهوك التي يستقبلها تيليجرام
@app.route(f"/webhook/{WEBHOOK_SECRET}", methods=['POST'])
def webhook():
    update = request.get_json(force=True, silent=True) or {}
    message = update.get('message') or update.get('edited_message')
    if not message:
        return jsonify({"ok": True})

    user = message.get('from', {})
    text = message.get('text', '')
    date = message.get('date', 0)
    user_id = user.get('id')

    conn = get_conn()
    c = conn.cursor()
    # حفظ المستخدم
    c.execute("INSERT OR IGNORE INTO users (id, first_name, last_name, username) VALUES (?, ?, ?, ?)",
              (user_id, user.get('first_name'), user.get('last_name'), user.get('username')))
    # حفظ الرسالة
    c.execute("INSERT OR IGNORE INTO messages (id, user_id, text, date) VALUES (?, ?, ?, ?)",
              (message.get('message_id'), user_id, text, date))
    conn.commit()

    # مثال: رد تلقائي بسيط
    if text.strip().lower() == '/start':
        requests.post(f"{TG_API}/sendMessage", json={"chat_id": user_id, "text": "مرحبا! بياناتك محفوظة."})

    return jsonify({"ok": True})

# REST API للتطبيق
@app.route('/api/users', methods=['GET'])
def api_users():
    conn = get_conn(); c = conn.cursor()
    rows = c.execute("SELECT id, first_name, last_name, username FROM users ORDER BY id DESC").fetchall()
    users = [ {"id": r[0], "first_name": r[1], "last_name": r[2], "username": r[3]} for r in rows ]
    return jsonify(users)

@app.route('/api/messages', methods=['GET'])
def api_messages():
    user_id = request.args.get('user_id')
    conn = get_conn(); c = conn.cursor()
    if user_id:
        rows = c.execute("SELECT id, user_id, text, date FROM messages WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
    else:
        rows = c.execute("SELECT id, user_id, text, date FROM messages ORDER BY id DESC LIMIT 200").fetchall()
    msgs = [ {"id": r[0], "user_id": r[1], "text": r[2], "date": r[3]} for r in rows ]
    return jsonify(msgs)

@app.route('/api/send', methods=['POST'])
def api_send():
    body = request.get_json(force=True) or {}
    chat_id = body.get('chat_id')
    text = body.get('text')
    if not chat_id or not text:
        return jsonify({"ok": False, "error": "chat_id & text required"}), 400
    r = requests.post(f"{TG_API}/sendMessage", json={"chat_id": chat_id, "text": text})
    return jsonify(r.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
