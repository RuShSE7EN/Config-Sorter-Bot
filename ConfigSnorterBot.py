import requests
import telebot
import qrcode
from io import BytesIO

# === BOT TOKEN ===
BOT_TOKEN = 'PASTE_YOUR_BOT_TOKEN_HERE'
bot = telebot.TeleBot(BOT_TOKEN)

# === DATA SOURCE ===
SOURCE_URL = 'https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list.raw.txt'

# === START COMMAND ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 سلام! من ConfigSnorterBot هستم. دستور /get رو بزن تا برات یه کانفیگ سالم Reality بفرستم برای Hiddify. 🧠")

# === GET COMMAND ===
@bot.message_handler(commands=['get'])
def send_config(message):
    try:
        res = requests.get(SOURCE_URL)
        links = [line for line in res.text.split('\n') if 'reality' in line.lower() or 'vless://' in line.lower()]
        if not links:
            bot.reply_to(message, "🚫 هیچ کانفیگ سالمی پیدا نشد. لعنت به فیلترینگ.")
            return

        config = links[0]  # اولین کانفیگ موجود رو می‌فرسته

        # QR code
        img = qrcode.make(config)
        bio = BytesIO()
        bio.name = 'qrcode.png'
        img.save(bio, 'PNG')
        bio.seek(0)

        bot.send_message(message.chat.id, f"🔗 کانفیگ آماده‌ست:\n{config}")
        bot.send_photo(message.chat.id, bio, caption="📱 این QR Code رو توی Hiddify اسکن کن.")
    except Exception as e:
        bot.reply_to(message, f"💥 خطا در دریافت کانفیگ: {str(e)}")

# === RUN ===
if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling()
