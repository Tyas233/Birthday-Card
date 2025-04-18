from flask import Flask
from threading import Thread
import telebot
import os

# Setup bot seperti biasa
bot = telebot.TeleBot(os.getenv('TOKEN'))

# ===== Bagian Baru untuk Replit =====
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Cut Bot Aktif 24 Jam!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    # Jalankan Flask dan bot secara bersamaan
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    
    # Jalankan bot dengan restart otomatis jika error
    while True:
        try:
            print("🔵 Bot mulai jalan...")
            bot.infinity_polling(timeout=30)
        except Exception as e:
            print(f"🔴 Error: {e}. Restart dalam 5 detik...")
            time.sleep(5)