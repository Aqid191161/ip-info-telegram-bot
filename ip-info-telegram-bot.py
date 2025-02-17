import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Memuat token dari file .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Token bot dari .env

# Fungsi untuk memeriksa apakah pengguna diizinkan
def is_allowed_user(update: Update) -> bool:
    user_id = update.message.from_user.id
    # Membaca ID pengguna yang diizinkan dari file allowed_users.txt
    with open("allowed_users.txt", "r") as file:
        allowed_users = file.read().splitlines()
    return str(user_id) in allowed_users

# Fungsi untuk menangani perintah /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_allowed_user(update):
        await update.message.reply_text(
            "Halo! Gunakan perintah /info <IP> untuk mendapatkan informasi IP. 😊"
        )
    else:
        await update.message.reply_text("❌ Anda tidak diizinkan mengakses bot ini.")

# Fungsi untuk mendapatkan informasi IP
def get_ip_info(ip: str) -> str:
    url = f"http://ip-api.com/json/{ip}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "success":
            return (
                f"🔍 **IP Information**:\n"
                f"• **IP**: {data['query']}\n"
                f"• **Country**: {data['country']} ({data['countryCode']})\n"
                f"• **Region**: {data['regionName']}\n"
                f"• **City**: {data['city']}\n"
                f"• **ISP**: {data['isp']}\n"
                f"• **Latitude/Longitude**: {data['lat']}, {data['lon']}\n"
                f"• **Timezone**: {data['timezone']}"
            )
        return "❌ IP tidak valid atau tidak ditemukan."
    return "❌ Gagal mendapatkan informasi IP."

# Fungsi untuk menangani perintah /info
async def ip_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed_user(update):
        await update.message.reply_text("❌ Anda tidak diizinkan mengakses bot ini.")
        return

    # Pastikan pengguna menyertakan argumen (IP)
    if len(context.args) == 0:
        await update.message.reply_text("❌ Silakan masukkan IP setelah perintah /info.")
        return

    ip = context.args[0]  # Ambil IP dari argumen
    info = get_ip_info(ip)
    await update.message.reply_text(info, parse_mode="Markdown")

# Main function untuk menjalankan bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handler untuk perintah /start
    app.add_handler(CommandHandler("start", start))

    # Handler untuk perintah /info
    app.add_handler(CommandHandler("info", ip_info))

    # Menjalankan bot
    print("Bot sedang berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()
