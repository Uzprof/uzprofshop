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

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- STATIC PAPKANI YARATISH ---
os.makedirs("static", exist_ok=True)

# --- UZUM MARKET USLUBIDAGI ZAMONAVIY DIZAYN ---
HTML_CONTENT = """<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Uzprof.shop - Raqamli Xizmatlar Bozori</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        :root {
            --primary: #7000ff;
            --primary-hover: #5b00d1;
            --bg-color: #f4f5f7;
            --card-bg: #ffffff;
            --text-main: #1f2022;
            --text-secondary: #8b8e99;
        }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 16px; background: var(--bg-color); color: var(--text-main); margin: 0; }
        .container { max-width: 600px; margin: auto; background: var(--card-bg); padding: 20px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); }
        .header { display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #f0f0f5; padding-bottom: 12px; margin-bottom: 20px; }
        .header h2 { margin: 0; color: var(--primary); font-size: 22px; display: flex; align-items: center; gap: 8px; }
        .user-badge { background: #f0ebff; color: var(--primary); padding: 6px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; }
        
        .section-title { font-size: 16px; font-weight: 700; margin: 20px 0 10px 0; color: var(--text-main); }
        
        .form-group { margin-bottom: 14px; }
        label { display: block; font-size: 13px; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px; }
        input, select, textarea { width: 100%; padding: 12px; border: 1.5px solid #e0e0eb; border-radius: 10px; box-sizing: border-box; font-size: 15px; background: #fafafa; transition: border-color 0.2s; }
        input:focus, select:focus, textarea:focus { border-color: var(--primary); outline: none; background: #fff; }
        
        .btn { width: 100%; padding: 14px; background: var(--primary); color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: 600; cursor: pointer; transition: background 0.2s; margin-top: 10px; }
        .btn:hover { background: var(--primary-hover); }
        .btn-admin { background: #ff7000; }
        .btn-admin:hover { background: #e06300; }
        
        #status-msg { margin-top: 15px; font-weight: 600; text-align: center; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🛒 Uzprof.shop</h2>
            <div class="user-badge" id="user-id">ID: Yuklanmoqda...</div>
        </div>
        
        <div class="form-group">
            <label>Kategoriya tanlang</label>
            <select id="category">
                <option value="Dasturlash va Botlar">💻 Dasturlash va Botlar</option>
                <option value="Telegram Stars">⭐ Telegram Stars (Yulduzlar)</option>
                <option value="Sovg'alar va Giftlar">🎁 Sovg'alar va Giftlar</option>
                <option value="Professional Xizmatlar">🛠️ Professional Xizmatlar</option>
            </select>
        </div>

        <div class="form-group">
            <label>Xizmat yoki mahsulot nomi</label>
            <input type="text" id="title" placeholder="Masalan: Telegram bot yaratish">
        </div>

        <div class="form-group">
            <label>Tavsif va narxi</label>
            <textarea id="desc" rows="3" placeholder="Batafsil ma'lumot va narxini kiriting..."></textarea>
        </div>

        <button class="btn" onclick="addProduct()">📦 E'lonni joylash</button>
        
        <div style="margin-top: 25px; border-top: 1px solid #f0f0f5; padding-top: 15px;">
            <button class="btn btn-admin" onclick="addAdmin()">⭐️ Admin huquqini olish</button>
        </div>

        <p id="status-msg"></p>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        let userId = tg.initDataUnsafe && tg.initDataUnsafe.user ? tg.initDataUnsafe.user.id : null;
        
        if (!userId) {
            document.getElementById('user-id').innerText = "ID topilmadi";
        } else {
            document.getElementById('user-id').innerText = "ID: " + userId;
        }

        function addAdmin() {
            if (!userId) { alert("Telegram ID topilmadi!"); return; }
            let formData = new URLSearchParams();
            formData.append("telegram_id", userId);
            fetch('/add_admin', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => { 
                let msg = document.getElementById('status-msg');
                msg.style.color = data.success ? '#7000ff' : 'red'; 
                msg.innerText = data.message; 
            });
        }

        function addProduct() {
            if (!userId) { alert("Telegram ID topilmadi! Botdan qaytadan kiring."); return; }
            let category = document.getElementById('category').value;
            let title = document.getElementById('title').value;
            let desc = document.getElementById('desc').value;
            
            if(!title || !desc) { alert("Barcha maydonlarni to'ldiring!"); return; }
            
            let formData = new URLSearchParams();
            formData.append("user_id", userId);
            formData.append("category", category);
            formData.append("title", title);
            formData.append("description", desc);
            
            fetch('/add_product', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => { 
                let msg = document.getElementById('status-msg');
                msg.style.color = data.success ? '#2ea44f' : 'red'; 
                msg.innerText = data.message;
                if(data.success) {
                    document.getElementById('title').value = '';
                    document.getElementById('desc').value = '';
                }
            });
        }
    </script>
</body>
</html>"""

# --- BAZANI XAVFSIZ YARATISH VA MIGRATION ---
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
    # Eski bazalarda is_admin ustuni yo'q bo'lsa xatolik bermasligi uchun xavfsiz qo'shish:
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # Ustun allaqachon mavjud bo'lsa o'tkazib yuboradi

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            telegram_id INTEGER PRIMARY KEY
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT,
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

# --- LIFESPAN ---
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

# --- WEBHOOK QULOG'I ---
@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        json_data = await request.json()
        update = types.Update(**json_data)
        await dp.feed_update(bot, update)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- WEB APP ROUTE ---
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return HTMLResponse(content=HTML_CONTENT)

@app.post("/add_admin")
async def add_admin_endpoint(telegram_id: int = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO admins (telegram_id) VALUES (?)", (telegram_id,))
        cursor.execute("INSERT OR IGNORE INTO users (telegram_id, is_admin) VALUES (?, 1)", (telegram_id,))
        cursor.execute("UPDATE users SET is_admin = 1 WHERE telegram_id = ?", (telegram_id,))
        conn.commit()
        return JSONResponse({"success": True, "message": "Tabriklaymiz! Siz admin bo'ldingiz."})
    except Exception as e:
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)
    finally:
        conn.close()

@app.post("/add_product")
async def add_product(user_id: int = Form(...), category: str = Form(...), title: str = Form(...), description: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO products (user_id, category, title, description, status) VALUES (?, ?, ?, ?, 'pending')", 
                       (user_id, category, title, description))
        conn.commit()
        return JSONResponse({"success": True, "message": "E'loningiz qabul qilindi! Admin tasdiqlashidan so'ng chiqadi."})
    except Exception as e:
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)
    finally:
        conn.close()

# --- TELEGRAM BOT ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if check_is_admin(user_id):
        await message.answer("⭐️ **Assalomu alaykum, Hurmatli Admin!**\nSiz tizimda admin sifatida faoliyat yurityapsiz.")
    else:
        await message.answer("🛍️ **Uzprof.shop** — Raqamli xizmatlar, dasturlash, Telegram Stars va sovg'alar bozoriga xush kelibsiz!\n\nVeb-ilovadan foydalanib o'z xizmatingizni joylashingiz mumkin.")
