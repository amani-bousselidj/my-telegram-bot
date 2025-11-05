# 📁 app.py (لخوادم الويب)
from flask import Flask, request, jsonify
import os
from telegram import Update

from production_bot import البوت_الإنتاجي

app = Flask(__name__)
بوت = None

@app.route('/')
def الصفحة_الرئيسية():
    return "🤖 البوت يعمل بشكل صحيح! API جاهز."

@app.route('/webhook/8210077803:AAEDBEPJQd94z3DaRgs_LqxdajandeqVtiU', methods=['POST'])
def webhook(token):
    if بوت:
        update = Update.de_json(request.get_json(), بوت.application.bot)
        بوت.application.process_update(update)
    return jsonify({"status": "ok"})

@app.route('/health')
def فحص_الصحة():
    return jsonify({"status": "healthy", "service": "telegram-bot"})

if __name__ == '__main__':
    بوت = البوت_الإنتاجي()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)