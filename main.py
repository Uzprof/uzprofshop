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

# --- PAPKA VA FAYLLARNI AVTOMATIK YARATISH (XATOLIKNI OLDINI OLISH) ---
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

index_html_path = os.path.join("templates", "index.html")
if not os.path.exists(index_html_path):
    with open(index_html_path, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Uzprof.shop</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f4f4f9; color: #333; }
        .container { max-width: 500px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h2 { color: #2ea44f; }
        button { width: 100%; padding: 12px; background: #2ea44f; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; margin-top: 10px; }
        button:hover { background: #2c974b; }
        input { width: 100%; padding: 10px; margin-top: 5px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🛍️ Uzprof.shop Panel</h2>
        <p>Telegram ID: <span id="user-id" style="font-weight:bold; color:#0088cc;">Aniqlanmoqda...</span></p>
        
        <h3>Admin boshqaruvi</h3>
        <button onclick="addAdmin()">⭐️ Admin bo'lish</button>
        
        <h3>Yangi e'lon berish</h3>
        <input type="text" id="title" placeholder="Mahsulot nomi">
        <input type="text" id="desc" placeholder="Tavsifi">
        <button onclick="addProduct()">📦 E'lonni yuborish</button>
        
        <p id="status-msg" style="margin-top: 15px; font-weight: bold; text-align: center; color: #d9534f;"></p>
    </div>
    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        let userId = tg.initDataUnsafe && tg.initDataUnsafe.user ? tg.initDataUnsafe.user.id : null;
        
        if (!userId) {
            document.getElementById('user-id').innerText = "Topilmadi (Botdan kiring)";
        } else {
            document.getElementById('user-id').innerText = userId;
        }

        function addAdmin() {
            if (!userId) { alert("Telegram ID topilmadi!"); return; }
            let formData = new URLSearchParams();
            formData.append("telegram_id", userId);
            fetch('/add_admin', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => { document.getElementById('status-msg').style.color = data.success ? 'green' : 'red'; document.getElementById('status-msg').innerText = data.message; });
        }

        function addProduct() {
            if (!userId) { alert("Telegram ID topilmadi!"); return; }
            let title = document.getElementById('title').value;
            let desc = document.getElementById('desc').value;
            if(!title || !desc) { alert("Barcha maydonlarni to'ldiring!"); return; }
            
            let formData = new URLSearchParams();
            formData.append("user_id", userId);
            formData.append("title", title);
            formData.append("description", desc);
            
            fetch('/add_product', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => { document.getElementById('status-msg').style.color = data.success ? 'green' : 'red'; document.getElementById('status-msg').innerText = data.message; });
        }
    </script>
</body>
</html>""")

# --- BAZANI YARATISH ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            full_name TEXT,
            is_admin INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            telegram_id INTEGER PRIMARY KEY
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            description TEXT,
            status TEXT DEFAULT 'pending'
        )
    """)
    conn.commit()
    conn.close()

def check_is_admin(telegram_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM admins WHERE telegram_id = ?", (telegram_id,))
        if cursor.fetchone():
            return True
        cursor.execute("SELECT is_admin FROM users WHERE telegram_id = ?", (telegram_id,))
        row = cursor.fetchone()
        if row and row[0] == 1:
            return True
    except Exception as e:
        print(f"Adminlikni tekshirish xatosi: {e}")
    finally:
        conn.close()
    return False

# --- WEBHOOK BILAN ISHGA TUSHISH (LIFESPAN) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    webhook_url = f"{DOMAIN}/webhook"
    try:
        await bot.set_webhook(webhook_url)
        print(f"Webhook o'rnatildi: {webhook_url}")
    except Exception as e:
        print(f"Webhook o'rnatishda xato: {e}")
    
    yield
    
    try:
        await bot.delete_webhook()
    except:
        pass
    await bot.session.close()

app = FastAPI(title="Uzprof.shop API", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- TELEGRAM WEBHOOK QULOG'I ---
@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        json_data = await request.json()
        update = types.Update(**json_data)
        await dp.feed_update(bot, update)
        return {"status": "ok"}
    except Exception as e:
        print(f"Webhook xatosi: {e}")
        return {"status": "error", "message": str(e)}

# --- WEB APP YO'LLARI ---
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/add_admin")
async def add_admin_endpoint(telegram_id: int = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO admins (telegram_id) VALUES (?)", (telegram_id,))
        cursor.execute("INSERT OR IGNORE INTO users (telegram_id, is_admin) VALUES (?, 1)", (telegram_id,))
        cursor.execute("UPDATE users SET is_admin = 1 WHERE telegram_id = ?", (telegram_id,))
        conn.commit()
        return JSONResponse({"success": True, "message": "Admin muvaffaqiyatli qo'shildi!"})
    except Exception as e:
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)
    finally:
        conn.close()

@app.post("/add_product")
async def add_product(user_id: int = Form(...), title: str = Form(...), description: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO products (user_id, title, description, status) VALUES (?, ?, ?, 'pending')", 
                       (user_id, title, description))
        conn.commit()
        return JSONResponse({"success": True, "message": "E'lon yuborildi! Admin tasdiqlashidan so'ng chiqadi."})
    except Exception as e:
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)
    finally:
        conn.close()

@app.post("/approve_product")
async def approve_product(product_id: int = Form(...), admin_id: int = Form(...)):
    if not check_is_admin(admin_id):
        return JSONResponse({"success": False, "message": "Sizda admin huquqi yo'q!"}, status_code=403)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE products SET status = 'approved' WHERE id = ?", (product_id,))
        conn.commit()
        return JSONResponse({"success": True, "message": "E'lon muvaffaqiyatli tasdiqlandi!"})
    except Exception as e:
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)
    finally:
        conn.close()

@app.post("/delete_product")
async def delete_product(product_id: int = Form(...), user_id: int = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        if not row:
            return JSONResponse({"success": False, "message": "E'lon topilmadi!"}, status_code=404)
        
        owner_id = row[0]
        if owner_id == user_id or check_is_admin(user_id):
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            return JSONResponse({"success":` True, "message": "E'lon o'chirildi!"})
        else:
            return JSONResponse({"success": False, "message": "Huquqingiz yo'q!"}, status_code=403)
    except Exception as e:
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)
    finally:
        conn.close()

# --- TELEGRAM BOT BUYRUQLARI ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if check_is_admin(user_id):
        await message.answer("⭐️ **Assalomu alaykum, Hurmatli Admin!**\nSiz tizimda admin sifatida turgansiz.")
    else:
        await message.answer("Assalomu alaykum! Uzprof.shop botiga xush kelibsiz. Veb-ilovadan foydalanishingiz mumkin.")
