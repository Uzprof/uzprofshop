import os
import shutil
import sqlite3
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# --- SOZLAMALAR ---
# DIQQAT: Agar pastdagi token xato bo'lsa, @BotFather dan yangi token olib shu yerga yozing!
BOT_TOKEN = "8784665419:AAE6BxyKjSffJnxnUBLEei76E-uP2dR2SgU" 
DOMAIN = "https://uzprofshop.onrender.com"
DB_PATH = "uzprof.db"
OWNER_ID = 7686687044
ADMIN_ID = 8564001612

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- PAPKALARNI YARATISH ---
os.makedirs("static", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)

# --- UZUM MARKET USLUBIDAGI PROFESSIONAL INTERFAYS (KO'K RANG) ---
HTML_CONTENT = """<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Uzprof.shop - Xizmatlar va Mahsulotlar Bozori</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        :root {
            --primary-blue: #007bff;
            --primary-hover: #0056b3;
            --bg-color: #f4f7f6;
            --card-bg: #ffffff;
            --text-main: #333333;
            --text-secondary: #666666;
        }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg-color); color: var(--text-main); margin: 0; padding: 15px; }
        .container { max-width: 500px; margin: auto; background: var(--card-bg); padding: 25px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #eef2f5; padding-bottom: 12px; margin-bottom: 20px; }
        .header h2 { margin: 0; color: var(--primary-blue); font-size: 22px; }
        .user-id-badge { background: #e7f1ff; color: var(--primary-blue); padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; }
        
        .form-group { margin-bottom: 15px; }
        label { display: block; font-size: 13px; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px; }
        input[type="text"], select, textarea, input[type="file"] { width: 100%; padding: 12px; border: 1.5px solid #dfe3e8; border-radius: 10px; box-sizing: border-box; font-size: 14px; background: #fafbfc; transition: border-color 0.2s; }
        input:focus, select:focus, textarea:focus { border-color: var(--primary-blue); outline: none; background: #fff; }
        
        .btn { width: 100%; padding: 14px; background: var(--primary-blue); color: white; border: none; border-radius: 10px; font-size: 16px; font-weight: bold; cursor: pointer; transition: background 0.2s; margin-top: 5px; }
        .btn:hover { background: var(--primary-hover); }
        .btn-admin { background: #ffc107; color: #333; margin-top: 15px; }
        .btn-admin:hover { background: #e0a800; }
        
        #status-msg { margin-top: 15px; font-weight: 600; text-align: center; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🛍️ Uzprof.shop</h2>
            <div class="user-id-badge" id="badge-id">ID: Aniqlanmoqda...</div>
        </div>
        
        <div class="form-group">
            <label>Kategoriya</label>
            <select id="category">
                <option value="Dasturlash va Botlar">💻 Dasturlash va Botlar</option>
                <option value="Telegram Stars">⭐ Telegram Stars</option>
                <option value="Sovg'alar va Giftlar">🎁 Sovg'alar va Giftlar</option>
                <option value="Professional Xizmatlar">🛠️ Professional Xizmatlar</option>
            </select>
        </div>

        <div class="form-group">
            <label>Xizmat yoki mahsulot nomi</label>
            <input type="text" id="title" placeholder="Masalan: Web sayt yasash">
        </div>

        <div class="form-group">
            <label>Batafsil tavsif va narxi</label>
            <textarea id="description" rows="3" placeholder="Narxi, bajarish muddati va shartlari..."></textarea>
        </div>

        <div class="form-group">
            <label>Mahsulot/Xizmat rasmi</label>
            <input type="file" id="image" accept="image/*">
        </div>

        <button class="btn" onclick="submitProduct()">🚀 E'lonni joylash</button>
        <button class="btn btn-admin" onclick="addAdmin()">⭐️ Admin huquqini olish</button>

        <p id="status-msg"></p>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        let userId = tg.initDataUnsafe && tg.initDataUnsafe.user ? tg.initDataUnsafe.user.id : null;
        
        if (!userId) {
            document.getElementById('badge-id').innerText = "ID topilmadi (Botdan kiring)";
        } else {
            document.getElementById('badge-id').innerText = "ID: " + userId;
        }

        function addAdmin() {
            if (!userId) { alert("Telegram ID topilmadi!"); return; }
            let formData = new URLSearchParams();
            formData.append("telegram_id", userId);
            fetch('/add_admin', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => { 
                let msg = document.getElementById('status-msg');
                msg.style.color = data.success ? 'green' : 'red';
                msg.innerText = data.message;
            });
        }

        async function submitProduct() {
            if (!userId) { alert("Iltimos, ilovani Telegram bot orqali oching!"); return; }
            let category = document.getElementById('category').value;
            let title = document.getElementById('title').value;
            let description = document.getElementById('description').value;
            let imageFile = document.getElementById('image').files[0];

            if (!title || !description) {
                alert("Iltimos, sarlavha va tavsifni to'ldiring!");
                return;
            }

            let formData = new FormData();
            formData.append("user_id", userId);
            formData.append("category", category);
            formData.append("title", title);
            formData.append("description", description);
            if (imageFile) {
                formData.append("image", imageFile);
            }

            let res = await fetch('/add_product', { method: 'POST', body: formData });
            let data = await res.json();
            
            let msg = document.getElementById('status-msg');
            msg.style.color = data.success ? 'blue' : 'red';
            msg.innerText = data.message;
            
            if (data.success) {
                document.getElementById('title').value = '';
                document.getElementById('description').value = '';
                document.getElementById('image').value = '';
            }
        }
    </script>
</body>
</html>"""

# --- BAZANI INITSIALIZATSIYA QILISH ---
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
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

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
            image_path TEXT,
            status TEXT DEFAULT 'pending'
        )
    """)
    # Owner va Adminlarni bazaga kiritish
    cursor.execute("INSERT OR IGNORE INTO admins (telegram_id) VALUES (?)", (OWNER_ID,))
    cursor.execute("INSERT OR IGNORE INTO admins (telegram_id) VALUES (?)", (ADMIN_ID,))
    cursor.execute("INSERT OR IGNORE INTO users (telegram_id, is_admin) VALUES (?, 1)", (OWNER_ID,))
    cursor.execute("INSERT OR IGNORE INTO users (telegram_id, is_admin) VALUES (?, 1)", (ADMIN_ID,))
    conn.commit()
    conn.close()

def check_is_admin(telegram_id: int) -> bool:
    if telegram_id in [OWNER_ID, ADMIN_ID]:
        return True
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM admins WHERE telegram_id = ?", (telegram_id,))
        if cursor.fetchone():
            return True
    except:
        pass
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
        print(f"Webhook xatosi: {e}")
    
    yield
    
    try:
        await bot.delete_webhook()
    except:
        pass
    await bot.session.close()

app = FastAPI(title="Uzprof.shop API", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- WEBHOOK ENDPOINT ---
@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        json_data = await request.json()
        update = types.Update(**json_data)
        await dp.feed_update(bot, update)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- WEB APP ROUTELARI ---
@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=HTML_CONTENT)

@app.post("/add_admin")
async def add_admin_endpoint(telegram_id: int = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO admins (telegram_id) VALUES (?)", (telegram_id,))
        cursor.execute("UPDATE users SET is_admin = 1 WHERE telegram_id = ?", (telegram_id,))
        conn.commit()
        return JSONResponse({"success": True, "message": "Tabriklaymiz! Sizga admin huquqi berildi."})
    except Exception as e:
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)
    finally:
        conn.close()

@app.post("/add_product")
async def add_product(
    user_id: int = Form(...),
    category: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(None)
):
    image_url = None
    if image and image.filename:
        file_extension = image.filename.split(".")[-1]
        file_name = f"{user_id}_{asyncio.get_event_loop().time()}_{os.urandom(4).hex()}.{file_extension}"
        file_path = os.path.join("static", "uploads", file_name)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_url = f"/static/uploads/{file_name}"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO products (user_id, category, title, description, image_path, status) VALUES (?, ?, ?, ?, ?, 'pending')",
            (user_id, category, title, description, image_url)
        )
        conn.commit()
        
        # Adminlarga xabar yuborish
        notif_text = f"📦 **Yangi e'lon keldi!**\n\n🏷️ Kategoriya: {category}\n📝 Nomi: {title}\n📄 Tavsif: {description}\n👤 Foydalanuvchi ID: {user_id}"
        for admin in [OWNER_ID, ADMIN_ID]:
            try:
                if image_url:
                    await bot.send_photo(admin, photo=types.URLInputFile(f"{DOMAIN}{image_url}"), caption=notif_text)
                else:
                    await bot.send_message(admin, notif_text)
            except:
                pass

        return JSONResponse({"success": True, "message": "✅ E'loningiz rasm bilan birga muvaffaqiyatli yuborildi!"})
    except Exception as e:
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)
    finally:
        conn.close()

# --- TELEGRAM BOT BUYRUQLARI ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if check_is_admin(user_id):
        await message.answer("⭐️ **Assalomu alaykum, Hurmatli Admin/Owner!**\nSiz Uzprof.shop tizimida ma'muriy huquqqa egasiz.")
    else:
        await message.answer("🛍️ **Uzprof.shop** — Raqamli xizmatlar, dasturlash, Stars va sovg'alar bozoriga xush kelibsiz!\n\nVeb-ilovaga kirib o'z xizmatingizni rasm bilan joylashingiz mumkin.")
