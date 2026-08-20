import os
import sqlite3
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# --- SOZLAMALAR ---
BOT_TOKEN = "8784665419:AAFeTyDY1eiA9jWuG_smi4Ag2wGA3VSDiQ"
DOMAIN = "https://uzprofshop.onrender.com"
DB_PATH = "uzprof.db"
ADMINS = [7686687044, 8564001612] # Owner va Admin IDlar

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- PROFESSIONAL UZUM-STYLE HTML ---
HTML_CONTENT = """<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <title>Uzprof Market</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        :root { --blue: #007bff; --bg: #f8f9fa; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); margin: 0; padding: 20px; }
        .container { max-width: 500px; margin: auto; background: white; padding: 25px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h2 { color: var(--blue); text-align: center; }
        .input-field { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }
        .btn { width: 100%; padding: 14px; background: var(--blue); color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }
        .card { border: 1px solid #eee; padding: 15px; margin-top: 15px; border-radius: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🛍️ Uzprof Market</h2>
        <input type="text" id="name" class="input-field" placeholder="Ismingiz">
        <select id="cat" class="input-field">
            <option>💻 Dasturlash</option>
            <option>⭐ Telegram Stars</option>
            <option>🎁 Sovg'alar</option>
            <option>🛠️ Professional Xizmatlar</option>
        </select>
        <input type="text" id="title" class="input-field" placeholder="Xizmat nomi">
        <textarea id="desc" class="input-field" placeholder="Batafsil ma'lumot va narx..."></textarea>
        <button class="btn" onclick="submit()">Xizmatni qo'shish</button>
        <div id="status" style="text-align:center; margin-top:15px; font-weight:bold;"></div>
    </div>
    <script>
        let tg = window.Telegram.WebApp;
        async function submit() {
            let fd = new FormData();
            fd.append("user_id", tg.initDataUnsafe.user.id);
            fd.append("name", document.getElementById('name').value);
            fd.append("cat", document.getElementById('cat').value);
            fd.append("title", document.getElementById('title').value);
            fd.append("desc", document.getElementById('desc').value);
            let res = await fetch('/add', {method:'POST', body:fd});
            let data = await res.json();
            document.getElementById('status').innerText = data.msg;
        }
    </script>
</body>
</html>"""

# --- BAZA FUNKSIYALARI ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS services (id INTEGER PRIMARY KEY, user_id INTEGER, name TEXT, cat TEXT, title TEXT, desc TEXT, status TEXT)")
    conn.commit()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    await bot.set_webhook(f"{DOMAIN}/webhook")
    yield
    await bot.session.close()

app = FastAPI(lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
async def index(): return HTMLResponse(HTML_CONTENT)

@app.post("/add")
async def add(user_id: int = Form(...), name: str = Form(...), cat: str = Form(...), title: str = Form(...), desc: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO services (user_id, name, cat, title, desc, status) VALUES (?,?,?,?,?,?)", 
                 (user_id, name, cat, title, desc, 'pending'))
    conn.commit()
    conn.close()
    
    # Adminlarga xabar yuborish
    for admin_id in ADMINS:
        await bot.send_message(admin_id, f"📦 **Yangi e'lon!**\n\n👤 Foydalanuvchi: {name}\n🏷️ Kategoriya: {cat}\n📝 Nomi: {title}\n💰 Tavsif: {desc}")
    return {"msg": "✅ Xizmatingiz moderatorga yuborildi!"}

@app.post("/webhook")
async def wh(req: Request):
    await dp.feed_update(bot, await req.json())
    return {"ok": True}

@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("Assalomu alaykum! Uzprof Marketga xush kelibsiz. Veb-ilovadan o'z xizmatingizni joylashingiz mumkin.")
