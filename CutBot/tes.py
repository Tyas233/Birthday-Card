import os
import google.generativeai as genai
from dotenv import load_dotenv

# ===== 1. SETUP AWAL =====
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# [1] TAROH DI SINI - CEK MODEL YANG TERSEDIA
print("Daftar model yang tersedia:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"- {m.name}")

# [2] BARU BUAT MODEL
model = genai.GenerativeModel('gemini-1.0-pro')  # Ganti dengan model yang muncul di list