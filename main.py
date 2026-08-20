import os
import sqlite3
import asyncio
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

BOT_TOKEN = "8784665419:AAFeTyDY1eiA9jWuG_smi4Ag2wGA3VSDiQ"
DOMAIN = "https://uzprofshop.onrender.com"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = FastAPI(title="Uzprof.shop API")

# Static va Templates papkalarini ulash
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- BAZA BILAN ISHLASH FUNKSIYALARI ---

def check_is_admin(telegram_id: int) -> bool:
    """Foydalanuvchi admin ekanligini bazadan tekshirish"""
    conn = sqlite3.connect("uzprof.db")
    cursor = conn.cursor()
    try:
        # 1-variant: users jadvalidagi is_admin ustunini tekshirish
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        if cursor.fetchone():
            cursor.execute("SELECT is_admin FROM users WHERE telegram_id = ?", (telegram_id,))
            row = cursor.fetchone()
            if row and row[0] == 1:
                return True

        # 2-variant: alohida admins jadvalidan tekshirish
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admins';")
        if cursor.fetchone():
            cursor.execute("SELECT * FROM admins WHERE telegram_id = ?", (telegram_id,))
            if cursor.fetchone():
                return True
                
    except Exception as e:
        print(f"Adminlikni tekshirishda xato: {e}")
    finally:
        conn.close()
    return False

# --- FASTAPI YO'LLARI (WEB APP) ---

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/add_admin")
async def add_admin_endpoint(telegram_id: int = Form(...)):
    """Veb-ilovadan kelgan IDni admin qilish"""
    conn = sqlite3.connect("uzprof.db")
    cursor = conn.cursor()
    try:
        # Xavfsizlik uchun ikkala jadvalga ham yozib qo'yamiz (xatolik oldini oladi)
        
        # 1. Admindar jadvalini yaratish va qo'shish
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                telegram_id INTEGER PRIMARY KEY
            )
        """)
        cursor.execute("INSERT OR IGNORE INTO admins (telegram_id) VALUES (?)", (telegram_id,))
        
        # 2. Agar users jadvali bo'lsa, uning ham is_admin qiymatini 1 qilish
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        if cursor.fetchone():
            cursor.execute("UPDATE users SET is_admin = 1 WHERE telegram_id = ?", (telegram_id,))
            
        conn.commit()
        return JSONResponse({"success": True, "message": "Admin muvaffaqiyatli qo'shildi!"})
    except Exception as e:
        print(f"Admin qo'shish xatoligi: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)
    finally:
        conn.close()

# --- AIOGRAM TELEGRAM BOT QISMI ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    
    # Bazadan adminligini tekshiramiz
    if check_is_admin(user_id):
        await message.answer("⭐️ **Assalomu alaykum, Hurmatli Admin!**\nSiz tizimda admin sifatida turgansiz.")
    else:
        await message.answer("Assalomu alaykum! Uzprof.shop botiga xush kelibsiz. Veb-ilovadan foydalanishingiz mumkin.")

# --- RENDER UCHUN BACKGROUND STARTUP ---

@app.on_event("startup")
async def startup_event():
    # Bot va FastAPI bir vaqtda 24/7 ishlashi uchun fon jarayoni
    asyncio.create_task(dp.start_polling(bot))
