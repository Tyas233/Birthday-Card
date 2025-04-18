import os
import random
import json
import tempfile
import time
import yt_dlp
from dotenv import load_dotenv
import google.generativeai as genai
import telebot
from gtts import gTTS
from telebot.types import (InlineKeyboardMarkup, InlineKeyboardButton, 
                          ReplyKeyboardMarkup, KeyboardButton)
from requests.exceptions import ReadTimeout
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

# ===== 1. INITIAL SETUP =====
load_dotenv()
bot = telebot.TeleBot(os.getenv('TOKEN'), parse_mode='MARKDOWN')
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Initialize models
cut_pro = genai.GenerativeModel('gemini-1.5-pro-latest')
cut_flash = genai.GenerativeModel('gemini-1.5-flash-latest')

# Databases
BLACKLIST_FILE = 'cut_blacklist.json'
ADMINS = [int(id) for id in os.getenv('ADMIN_IDS', '').split(',') if id]
MUSIC_QUEUE = {}
GAME_DATA = {}  # {chat_id: game_state}
TRIVIA_SCORES = {}  # {chat_id: {user_id: score}}
MATH_SCORES = {}    # {chat_id: {user_id: score}}

# ===== 2. CORE FUNCTIONS =====
def cut_response(prompt):
    """AI response generator with error handling"""
    try:
        model, style = (cut_flash, "⚡") if len(prompt.split()) <= 5 else (cut_pro, "🧠")
        response = model.generate_content(
            f"Respond as friendly assistant Cut in Bahasa Indonesia: {prompt}",
            generation_config={"temperature": 0.7, "max_output_tokens": 200}
        )
        return f"{style} *Cut*: {response.text}"
    except Exception as e:
        print(f"AI Error: {e}")
        return random.choice([
            "Aku lagi error nih...",
            "Coba tanya lagi ya!",
            "Wah, Cut lagi pusing~"
        ])

# ===== 3. TRIVIA GAME WITH VOICE =====
TRIVIA_DB = {
    "hewan": [
        {"question": "Hewan berkaki empat yang suka mengeong?", "answer": "kucing", "voice": "meong"},
        {"question": "Hewan berkaki dua yang bisa terbang?", "answer": "burung", "voice": "kukuruyuk"}
    ],
    "sayur": [
        {"question": "Sayur berwarna orange yang baik untuk mata?", "answer": "wortel", "voice": "wortel segar"},
        {"question": "Sayur hijau yang sering dijus?", "answer": "bayam", "voice": "bayam sehat"}
    ],
    "negara": [
        {"question": "Negara dengan menara Eiffel?", "answer": "perancis", "voice": "bonjour"},
        {"question": "Negara terbesar di dunia?", "answer": "rusia", "voice": "vodka"}
    ]
}

@bot.message_handler(commands=['cuttrivia'])
def start_trivia(message):
    """Start trivia game with voice hints"""
    try:
        category = random.choice(list(TRIVIA_DB.keys()))
        question = random.choice(TRIVIA_DB[category])
        
        # Send voice hint
        if "voice" in question:
            try:
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as fp:
                    tts = gTTS(question["voice"], lang='id')
                    tts.save(fp.name)
                    bot.send_voice(message.chat.id, open(fp.name, 'rb'))
            except Exception as e:
                print(f"Voice error: {e}")

        # Initialize score if not exists
        chat_id = message.chat.id
        user_id = message.from_user.id
        if chat_id not in TRIVIA_SCORES:
            TRIVIA_SCORES[chat_id] = {}
        if user_id not in TRIVIA_SCORES[chat_id]:
            TRIVIA_SCORES[chat_id][user_id] = 0
            
        msg = bot.reply_to(message, f"🎲 *TRIVIA*: {question['question']}")
        bot.register_next_step_handler(msg, check_trivia_answer, question["answer"])
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

def check_trivia_answer(message, correct_answer):
    """Check trivia answer and update score"""
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        if message.text.lower() == correct_answer.lower():
            TRIVIA_SCORES[chat_id][user_id] += 1
            reply = f"✅ *Benar!* Skor: {TRIVIA_SCORES[chat_id][user_id]}"
        else:
            reply = f"❌ Salah! Jawabannya: *{correct_answer.capitalize()}*"
            
        bot.reply_to(message, reply)
        send_next_trivia_question(chat_id)
        
    except Exception as e:
        print(f"Trivia error: {e}")
        bot.reply_to(message, "Waktu habis!")

def send_next_trivia_question(chat_id):
    """Send next trivia question automatically"""
    time.sleep(1)
    start_trivia(bot.send_message(chat_id, "Lanjut ke soal berikutnya..."))

# ===== 4. XOX GAME =====
@bot.message_handler(commands=['cutxox'])
def start_xox_game(message):
    """Start Tic-Tac-Toe game"""
    try:
        chat_id = message.chat.id
        GAME_DATA[chat_id] = {
            'board': [' ']*9,
            'players': [message.from_user.id, None],
            'current_player': 0
        }
        
        markup = InlineKeyboardMarkup()
        for i in range(0, 9, 3):
            markup.row(
                *[InlineKeyboardButton(" ", callback_data=f"xox_{i+j}") for j in range(3)]
            )
        
        bot.send_message(chat_id, "❌⭕ *Game XOX* ❌⭕\nPlayer 1: X", reply_markup=markup)
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('xox_'))
def handle_xox_move(call):
    """Handle XOX game moves"""
    try:
        chat_id = call.message.chat.id
        pos = int(call.data.split('_')[1])
        game = GAME_DATA.get(chat_id)
        
        if not game or call.from_user.id != game['players'][game['current_player']]:
            bot.answer_callback_query(call.id, "Bukan giliranmu!")
            return
            
        symbol = '❌' if game['current_player'] == 0 else '⭕'
        game['board'][pos] = symbol
        
        # Update board
        markup = InlineKeyboardMarkup()
        for i in range(0, 9, 3):
            markup.row(
                *[InlineKeyboardButton(game['board'][i+j], callback_data=f"xox_{i+j}") for j in range(3)]
            )
        
        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
        
        # Check winner
        winner = check_xox_winner(game['board'])
        if winner:
            bot.send_message(chat_id, f"🎉 *Player {winner} menang!*")
            del GAME_DATA[chat_id]
        else:
            game['current_player'] = 1 - game['current_player']
            bot.answer_callback_query(call.id, f"Giliran Player {'⭕' if game['current_player'] else '❌'}")
            
    except Exception as e:
        print(f"XOX error: {e}")

def check_xox_winner(board):
    """Check XOX game winner"""
    win_conditions = [
        [0,1,2], [3,4,5], [6,7,8],  # rows
        [0,3,6], [1,4,7], [2,5,8],   # columns
        [0,4,8], [2,4,6]              # diagonals
    ]
    for condition in win_conditions:
        if board[condition[0]] == board[condition[1]] == board[condition[2]] != ' ':
            return board[condition[0]]
    return None

# ===== 5. MATH GAME =====
@bot.message_handler(commands=['cutmath'])
def start_math_game(message):
    """Start math quiz game"""
    try:
        a, b = random.randint(1, 20), random.randint(1, 20)
        answer = a + b
        
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        if chat_id not in MATH_SCORES:
            MATH_SCORES[chat_id] = {}
        if user_id not in MATH_SCORES[chat_id]:
            MATH_SCORES[chat_id][user_id] = 0
            
        GAME_DATA[chat_id] = {
            'answer': answer,
            'user_id': user_id
        }
        
        bot.reply_to(message, f"🧮 *Berapa {a} + {b}?* (10 detik)")
        
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(func=lambda msg: msg.chat.id in GAME_DATA and 'answer' in GAME_DATA[msg.chat.id])
def check_math_answer(message):
    """Check math answer"""
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id
        game = GAME_DATA[chat_id]
        
        if user_id != game['user_id']:
            return
            
        if int(message.text) == game['answer']:
            MATH_SCORES[chat_id][user_id] += 1
            reply = f"✅ *Benar!* Skor: {MATH_SCORES[chat_id][user_id]}"
        else:
            reply = f"❌ Salah! Jawabannya: *{game['answer']}*"
            
        bot.reply_to(message, reply)
        del GAME_DATA[chat_id]
        
    except ValueError:
        bot.reply_to(message, "Harap jawab dengan angka!")
    except Exception as e:
        print(f"Math error: {e}")

# ===== 6. STICKER REPLY =====
@bot.message_handler(content_types=['sticker'])
def reply_sticker(message):
    """Reply with same sticker"""
    try:
        bot.send_sticker(message.chat.id, message.sticker.file_id)
    except Exception as e:
        print(f"Sticker error: {e}")

# ===== 7. VOICE MESSAGE =====
@bot.message_handler(commands=['cutvoice'])
def voice_message(message):
    """Convert text to voice"""
    try:
        text = message.text.replace('/cutvoice', '').strip()
        if not text:
            return bot.reply_to(message, "Contoh: /cutvoice Hai aku Cut")
            
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as fp:
            tts = gTTS(text, lang='id')
            tts.save(fp.name)
            bot.send_voice(
                message.chat.id, 
                open(fp.name, 'rb'),
                caption=f"🔊 *Cut bilang*: {text[:50]}..."
            )
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# ===== 8. ADMIN COMMANDS =====
@bot.message_handler(commands=['cutclear'])
def clear_cache(message):
    """Clear bot cache (admin only)"""
    if message.from_user.id not in ADMINS:
        return
        
    global MUSIC_QUEUE, GAME_DATA
    MUSIC_QUEUE = {}
    GAME_DATA = {}
    
    bot.reply_to(message, "♻️ *Cache dibersihkan!*")

# ===== 9. RUN BOT =====
def run_bot():
    """Run bot with error handling"""
    while True:
        try:
            print("🤖 Cut Bot is running...")
            bot.infinity_polling(timeout=30, long_polling_timeout=60)
        except ReadTimeout:
            print("⚠️ Timeout, restarting...")
            time.sleep(10)
        except Exception as e:
            print(f"⚠️ Critical error: {e}")
            time.sleep(30)

if __name__ == '__main__':
    # Initialize files
    if not os.path.exists(BLACKLIST_FILE):
        with open(BLACKLIST_FILE, 'w') as f:
            json.dump({"users": [], "groups": []}, f)
    
    print("""
    🚀 *Cut Bot Activated!*
    Fitur:
    - /cuttrivia : Kuis dengan petunjuk suara
    - /cutxox : Game XOX
    - /cutmath : Kuis matematika
    - /cutvoice : Ubah teks jadi suara
    - Reply sticker otomatis
    - /cutclear : Bersihkan cache (admin)
    """)
    
    run_bot()