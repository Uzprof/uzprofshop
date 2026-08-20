import os
import sqlite3
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# --- SOZLAMALAR ---
BOT_TOKEN = "8784665419:AAFeTyDY1eiA9jWuG_smi4Ag2wGA3VSDiQ"
DOMAIN = "https://uzprofshop.onrender.com"
DB_PATH = "uzprof.db"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- BAZANI AVTOMATIK INITSIALIZATSIYA QILISH ---
def init_db():
    """Ma'lumotlar bazasi va jadvallarni yaratish"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Foydalanuvchilar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            full_name TEXT,
            is_admin INTEGER DEFAULT 0
        )
    """)
    # Alohida adminlar jadvali (zaxira uchun)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            telegram_id INTEGER PRIMARY KEY
        )
    """)
    conn.commit()
    conn.close()

def check_is_admin(telegram_id: int) -> bool:
    """Foydalanuvchi admin ekanligini tekshirish"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # 1. Adminlar jadvalidan qidirish
        cursor.execute("SELECT 1 FROM admins WHERE telegram_id = ?", (telegram_id,))
        if cursor.fetchone():
            return True
            
        # 2. Users jadvalidagi is_admin ustunidan qidirish
        cursor.execute("SELECT is_admin FROM users WHERE telegram_id = ?", (telegram_id,))
        row = cursor.fetchone()
        if row and row[0] == 1:
            return True
    except Exception as e:
        print(f"Adminlikni tekshirishda xatolik: {e}")
    finally:
        conn.close()
    return False

# --- FASTAPI LIFESPAN (SERVER VA BOTNI BIRGA BOSHQARISH) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Server ishga tushganda bazani tekshiramiz va botni fonda yoqamiz
    init_db()
    polling_task = asyncio.create_task(dp.start_polling(bot))
    yield
    # Server to'xtaganda botni ham to'xtatamiz
    polling_task.cancel()
    try:
        await polling_task
    except asyncio.CancelledError:
        pass
    await bot.session.close()

app = FastAPI(title="Uzprof.shop API", lifespan=lifespan)

# Statik fayllar va shablonlarni ulash
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- WEB APP YO'LLARI ---
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/add_admin")
async def add_admin_endpoint(telegram_id: int = Form(...)):
    """Veb-ilovadan kelgan IDni bazaga admin sifatida yozish"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Ikkala jadvalga ham yozamiz (xatolik chiqmasligi uchun)
        cursor.execute("INSERT OR IGNORE INTO admins (telegram_id) VALUES (?)", (telegram_id,))
        
        cursor.execute("INSERT OR IGNORE INTO users (telegram_id, is_admin) VALUES (?, 1)", (telegram_id,))
        cursor.execute("UPDATE users SET is_admin = 1 WHERE telegram_id = ?", (telegram_id,))
        
        conn.commit()
        return JSONResponse({"success": True, "message": "Admin muvaffaqiyatli qo'shildi!"})
    except Exception as e:
        print(f"Admin qo'shishda xatolik: {e}")
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)
    finally:
        conn.close()

# --- TELEGRAM BOT BUYRUQLARI ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if check_is_admin(user_id):
        await message.answer("⭐️ **Assalomu alaykum, Hurmatli Admin!**\nSiz tizimda admin huquqiga egasiz.")
    else:
        await message.answer("Assalomu alaykum! Uzprof.shop botiga xush kelibsiz. Veb-ilovadan foydalanishingiz mumkin.")
