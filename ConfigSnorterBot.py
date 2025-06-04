import requests
import telebot
import qrcode
from io import BytesIO
from flask import Flask, request

import os
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_HOST = os.environ.get("WEBHOOK_URL")  # مثلاً: https://your-project.up.railway.app

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

SOURCE_URL = 'https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list.raw.txt'

@app.route('/', methods=['GET'])
def index():
    return 'Bot is alive!', 200

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'ok', 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 سلام! من بات Webhook جدیدم. بزن /get تا کانفیگ Reality بفرستم.")

@bot.message_handler(commands=['get'])
def send_config(message):
    try:
        res = requests.get(SOURCE_URL)
        links = [line for line in res.text.split('\\n') if 'reality' in line.lower() or 'vless://' in line.lower()]
        if not links:
            bot.reply_to(message, "🚫 هیچ کانفیگ سالمی پیدا نشد.")
            return
        config = links[0]
        img = qrcode.make(config)
        bio = BytesIO()
        bio.name = 'qrcode.png'
        img.save(bio, 'PNG')
        bio.seek(0)
        bot.send_message(message.chat.id, f"🔗 کانفیگ:\n{config}")
        bot.send_photo(message.chat.id, bio, caption="📱 اینو با Hiddify اسکن کن.")
    except Exception as e:
        bot.reply_to(message, f"💥 خطا: {str(e)}")

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_HOST}/{BOT_TOKEN}")
    app.run(host='0.0.0.0', port=8000)
