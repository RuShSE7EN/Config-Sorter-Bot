import os
import requests
import telebot
import qrcode
from io import BytesIO
from flask import Flask, request

# === تنظیمات توکن و دامنه Webhook از Environment ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_HOST = os.environ.get("WEBHOOK_URL")  # مثل https://your-app.up.railway.app

# === بررسی وجود توکن ===
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN تعریف نشده. لطفاً تو Railway مقدارشو تنظیم کن.")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# === منبع کانفیگ ===
SOURCE_URL = 'https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt'

# === مسیر اصلی وب‌سایت (چک سلامت) ===
@app.route('/', methods=['GET'])
def index():
    return '✅ Bot is alive.', 200

# === مسیر Webhook برای دریافت پیام‌ها ===
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'ok', 200

# === فرمان /start ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 سلام! من ConfigSnorterBot هستم. بزن /get تا برات یه کانفیگ VLESS بیارم از دل تحریم و فیلتر.")

# === فرمان /get ===
@bot.message_handler(commands=['get'])
def send_config(message):
    try:
        SOURCES = [
            'https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt',
            'https://raw.githubusercontent.com/AzadNetCH/Clash/main/vless.txt',
            'https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list.raw.txt'
        ]

        config = None
        for url in SOURCES:
            res = requests.get(url, timeout=5)
            lines = [line.strip() for line in res.text.split('\n') if line.strip().startswith('vless://')]
            if lines:
                config = random.choice(lines)
                break  # وقتی پیدا شد، بپر بیرون

        if not config:
            bot.reply_to(message, "🚫 هیچ کانفیگ VLESS‌ای از هیچ‌کدوم از منابع پیدا نشد. شاید فردا بهتر باشه :)")
            return

        img = qrcode.make(config)
        bio = BytesIO()
        bio.name = 'qrcode.png'
        img.save(bio, 'PNG')
        bio.seek(0)

        bot.send_message(message.chat.id, f"🔗 کانفیگ:\n{config}")
        bot.send_photo(message.chat.id, bio, caption="📱 این QR Code رو توی Hiddify اسکن کن.")
    except Exception as e:
        bot.reply_to(message, f"💥 خطا در دریافت کانفیگ:\n{str(e)}")
