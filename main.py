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
BOT_TOKEN = "8784665419:AAFeTyDY1eiA9jWuG_smi4Ag2wGA3VSDiQ"  # O'z tokeningizni yozing
DOMAIN = "https://uzprofshop.onrender.com"
DB_PATH = "uzprof.db"
OWNER_ID = 7686687044
ADMIN_ID = 8564001612

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

os.makedirs("static/uploads", exist_ok=True)

# --- UZUM MARKET 1:1 USLUBIDAGI PROFESSIONAL INTERFAYS ---
HTML_CONTENT = """<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Uzprof.shop - Onlayn Bozor</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        :root {
            --uzum-blue: #007bff;
            --uzum-blue-hover: #0056b3;
            --bg-light: #f4f5f7;
            --text-main: #1f2022;
            --text-secondary: #8b8e98;
            --border-color: #e0e0e0;
        }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg-light); color: var(--text-main); margin: 0; padding: 0; }
        
        /* Top Navigation Bar */
        .top-nav { background: #fff; border-bottom: 1px solid var(--border-color); padding: 8px 16px; display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: var(--text-secondary); }
        .top-nav-left { display: flex; gap: 15px; }
        
        /* Main Header */
        .main-header { background: #fff; padding: 12px 16px; display: flex; align-items: center; gap: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); position: sticky; top: 0; z-index: 100; }
        .logo { font-size: 20px; font-weight: 800; color: var(--uzum-blue); text-decoration: none; display: flex; align-items: center; gap: 6px; }
        .catalog-btn { background: #eef2ff; color: var(--uzum-blue); border: none; padding: 10px 16px; border-radius: 8px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; }
        .search-bar { flex: 1; display: flex; border: 2px solid var(--uzum-blue); border-radius: 10px; overflow: hidden; background: #fff; }
        .search-bar input { flex: 1; border: none; padding: 10px 14px; outline: none; font-size: 14px; }
        .search-bar button { background: var(--uzum-blue); color: #fff; border: none; padding: 0 16px; cursor: pointer; font-weight: bold; }
        
        /* Categories Ribbon */
        .categories-ribbon { background: #fff; padding: 10px 16px; display: flex; gap: 10px; overflow-x: auto; border-bottom: 1px solid var(--border-color); white-space: nowrap; }
        .cat-pill { background: #f4f5f7; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 500; cursor: pointer; color: var(--text-main); transition: 0.2s; }
        .cat-pill:hover, .cat-pill.active { background: var(--uzum-blue); color: #fff; }

        /* Container & Tabs */
        .container { max-width: 1200px; margin: 20px auto; padding: 0 16px; }
        .nav-tabs { display: flex; gap: 10px; margin-bottom: 20px; }
        .tab-btn { background: #fff; border: 1px solid var(--border-color); padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: 600; color: var(--text-secondary); }
        .tab-btn.active { background: var(--uzum-blue); color: #fff; border-color: var(--uzum-blue); }

        /* Product Grid */
        .product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }
        .product-card { background: #fff; border-radius: 12px; padding: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); display: flex; flex-direction: column; position: relative; }
        .product-card img { width: 100%; height: 160px; object-fit: cover; border-radius: 8px; background: #eee; }
        .product-title { font-size: 14px; font-weight: 600; margin: 10px 0 5px 0; color: var(--text-main); }
        .product-desc { font-size: 12px; color: var(--text-secondary); flex: 1; margin-bottom: 10px; }
        .product-price { font-size: 16px; font-weight: bold; color: var(--uzum-blue); }
        
        /* Forms & Admin Panel */
        .form-box, .admin-box { background: #fff; padding: 25px; border-radius: 12px; max-width: 600px; margin: 0 auto; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .form-group { margin-bottom: 15px; }
        label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 6px; }
        input, select, textarea { width: 100%; padding: 12px; border: 1px solid var(--border-color); border-radius: 8px; box-sizing: border-box; font-size: 14px; }
        .btn-primary { width: 100%; background: var(--uzum-blue); color: #fff; border: none; padding: 14px; border-radius: 8px; font-size: 15px; font-weight: bold; cursor: pointer; }
        .btn-primary:hover { background: var(--uzum-blue-hover); }
        
        .admin-list-item { display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #eee; align-items: center; }
        .badge { background: #eef2ff; color: var(--uzum-blue); padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: bold; }
    </style>
</head>
<body>

    <!-- Top Navigation -->
    <div class="top-nav">
        <div class="top-nav-left">
            <span>📍 Toshkent</span>
            <span>Topshirish punktlari</span>
            <span>Sotuvchi bo'lish</span>
        </div>
        <div id="user-info-badge" style="font-weight: bold; color: var(--uzum-blue);">ID aniqlanmoqda...</div>
    </div>

    <!-- Main Header -->
    <div class="main-header">
        <a href="#" class="logo">🛍️ Uzprof.shop</a>
        <button class="catalog-btn">☰ Katalog</button>
        <div class="search-bar">
            <input type="text" id="searchInput" placeholder="Mahsulotlar va xizmatlarni izlash...">
            <button>Qidirish</button>
        </div>
    </div>

    <!-- Categories Ribbon -->
    <div class="categories-ribbon">
        <div class="cat-pill active" onclick="filterCat('Barchasi')">🔥 Barchasi</div>
        <div class="cat-pill" onclick="filterCat('Dasturlash va Botlar')">💻 Dasturlash va Botlar</div>
        <div class="cat-pill" onclick="filterCat('Telegram Stars')">⭐ Telegram Stars</div>
        <div class="cat-pill" onclick="filterCat('Sovgora va Giftlar')">🎁 Sovg'alar</div>
        <div class="cat-pill" onclick="filterCat('Professional Xizmatlar')">🛠️ Xizmatlar</div>
    </div>

    <div class="container">
        <!-- Navigation Tabs -->
        <div class="nav-tabs">
            <button class="tab-btn active" onclick="switchTab('market')" id="tabMarket">📦 Mahsulotlar</button>
            <button class="tab-btn" onclick="switchTab('add')" id="tabAdd">➕ E'lon berish</button>
            <button class="tab-btn" onclick="switchTab('admin')" id="tabAdmin" style="display:none;">⚙️ Admin Panel</button>
        </div>

        <!-- Marketplace View -->
        <div id="sectionMarket">
            <div class="product-grid" id="productGrid">
                <!-- Mahsulotlar shu yerga yuklanadi -->
            </div>
        </div>

        <!-- Add Product View -->
        <div id="sectionAdd" style="display:none;">
            <div class="form-box">
                <h2>Xizmat yoki Mahsulot Joylash</h2>
                <div class="form-group">
                    <label>Kategoriya</label>
                    <select id="prodCat">
                        <option value="Dasturlash va Botlar">💻 Dasturlash va Botlar</option>
                        <option value="Telegram Stars">⭐ Telegram Stars</option>
                        <option value="Sovgora va Giftlar">🎁 Sovg'alar va Giftlar</option>
                        <option value="Professional Xizmatlar">🛠️ Professional Xizmatlar</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Nomi</label>
                    <input type="text" id="prodTitle" placeholder="Masalan: Telegram bot yaratish">
                </div>
                <div class="form-group">
                    <label>Tavsif va Narxi</label>
                    <textarea id="prodDesc" rows="3" placeholder="Narxi, shartlari va batafsil..."></textarea>
                </div>
                <div class="form-group">
                    <label>Rasm yuklash</label>
                    <input type="file" id="prodImage" accept="image/*">
                </div>
                <button class="btn-primary" onclick="submitProduct()">E'lonni joylash</button>
                <p id="addMsg" style="text-align:center; margin-top:10px; font-weight:600;"></p>
            </div>
        </div>

        <!-- Admin Panel View -->
        <div id="sectionAdmin" style="display:none;">
            <div class="admin-box">
                <h2>Admin Boshqaruvi</h2>
                <p>Username orqali yangi admin qo'shish (masalan: <b>@username</b>)</p>
                <div class="form-group">
                    <input type="text" id="newAdminUsername" placeholder="@admin_username">
                </div>
                <button class="btn-primary" onclick="addNewAdmin()">Admin qo'shish</button>
                <p id="adminMsg" style="text-align:center; margin-top:10px; font-weight:600;"></p>
                
                <hr style="margin: 25px 0; border:0; border-top:1px solid #eee;">
                <h3>Mavjud Adminlar</h3>
                <div id="adminListContainer">
                    <!-- Adminlar ro'yxati -->
                </div>
            </div>
        </div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        let user = tg.initDataUnsafe && tg.initDataUnsafe.user ? tg.initDataUnsafe.user : {id: 7686687044, username: "owner"};
        
        document.getElementById('user-info-badge').innerText = `ID: ${user.id} (@${user.username || 'user'})`;

        // Tekshirish: Adminmi?
        checkAdminStatus();

        async function checkAdminStatus() {
            let res = await fetch(`/api/check_admin?user_id=${user.id}&username=${user.username || ''}`);
            let data = await res.json();
            if (data.is_admin) {
                document.getElementById('tabAdmin').style.display = 'block';
                loadAdminList();
            }
        }

        function switchTab(tab) {
            document.getElementById('sectionMarket').style.display = tab === 'market' ? 'block' : 'none';
            document.getElementById('sectionAdd').style.display = tab === 'add' ? 'block' : 'none';
            document.getElementById('sectionAdmin').style.display = tab === 'admin' ? 'block' : 'none';
            
            document.getElementById('tabMarket').classList.toggle('active', tab === 'market');
            document.getElementById('tabAdd').classList.toggle('active', tab === 'add');
            document.getElementById('tabAdmin').classList.toggle('active', tab === 'admin');

            if (tab === 'market') loadProducts();
        }

        async function loadProducts(category = 'Barchasi') {
            let res = await fetch(`/api/products?cat=${encodeURIComponent(category)}`);
            let products = await res.json();
            let grid = document.getElementById('productGrid');
            grid.innerHTML = '';
            
            if (products.length === 0) {
                grid.innerHTML = '<p style="grid-column: 1/-1; text-align:center; color:#8b8e98;">Hozircha e\'lonlar mavjud emas.</p>';
                return;
            }

            products.forEach(p => {
                let card = document.createElement('div');
                card.className = 'product-card';
                card.innerHTML = `
                    <img src="${p.image_path ? p.image_path : 'https://via.placeholder.com/200'}" alt="Product">
                    <div class="product-title">${p.title}</div>
                    <div class="product-desc">${p.description}</div>
                    <div class="product-price">${p.category}</div>
                `;
                grid.appendChild(card);
            });
        }

        function filterCat(cat) {
            document.querySelectorAll('.cat-pill').forEach(p => p.classList.remove('active'));
            event.target.classList.add('active');
            loadProducts(cat);
        }

        async function submitProduct() {
            let fd = new FormData();
            fd.append("user_id", user.id);
            fd.append("username", user.username || "");
            fd.append("category", document.getElementById('prodCat').value);
            fd.append("title", document.getElementById('prodTitle').value);
            fd.append("description", document.getElementById('prodDesc').value);
            let img = document.getElementById('prodImage').files[0];
            if (img) fd.append("image", img);

            let res = await fetch('/api/add_product', { method: 'POST', body: fd });
            let data = await res.json();
            let msg = document.getElementById('addMsg');
            msg.style.color = data.success ? 'green' : 'red';
            msg.innerText = data.message;
            if (data.success) {
                document.getElementById('prodTitle').value = '';
                document.getElementById('prodDesc').value = '';
                document.getElementById('prodImage').value = '';
                setTimeout(() => switchTab('market'), 1500);
            }
        }

        async function addNewAdmin() {
            let uname = document.getElementById('newAdminUsername').value.trim();
            if (!uname) { alert("Username kiriting!"); return; }
            
            let fd = new URLSearchParams();
            fd.append("username", uname);
            let res = await fetch('/api/add_admin', { method: 'POST', body: fd });
            let data = await res.json();
            
            let msg = document.getElementById('adminMsg');
            msg.style.color = data.success ? 'green' : 'red';
            msg.innerText = data.message;
            if (data.success) {
                document.getElementById('newAdminUsername').value = '';
                loadAdminList();
            }
        }

        async function loadAdminList() {
            let res = await fetch('/api/admins');
            let admins = await res.json();
            let container = document.getElementById('adminListContainer');
            container.innerHTML = '';
            admins.forEach(a => {
                let div = document.createElement('div');
                div.className = 'admin-list-item';
                div.innerHTML = `<span>@${a}</span> <span class="badge">Admin</span>`;
                container.appendChild(div);
            });
        }

        // Boshlang'ich yuklash
        loadProducts();
    </script>
</body>
</html>"""

# --- BAZA BILAN ISHLASH ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            username TEXT PRIMARY KEY
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            category TEXT,
            title TEXT,
            description TEXT,
            image_path TEXT,
            status TEXT DEFAULT 'approved'
        )
    """)
    # Owner va Admin username/ID larini kiritish
    c.execute("INSERT OR IGNORE INTO admins (username) VALUES ('owner_uzprof')")
    c.execute("INSERT OR IGNORE INTO admins (username) VALUES ('admin_uzprof')")
    conn.commit()
    conn.close()

def is_admin_user(user_id: int, username: str) -> bool:
    if user_id in [OWNER_ID, ADMIN_ID]:
        return True
    if not username:
        return False
    
    clean_uname = username.lstrip('@').lower()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM admins WHERE LOWER(username) = ?", (clean_uname,))
    res = c.fetchone()
    conn.close()
    return res is not None

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    webhook_url = f"{DOMAIN}/webhook"
    try:
        await bot.set_webhook(webhook_url)
    except:
        pass
    yield
    try:
        await bot.delete_webhook()
    except:
        pass
    await bot.session.close()

app = FastAPI(title="Uzprof.shop", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=HTML_CONTENT)

@app.get("/api/products")
async def get_products(cat: str = "Barchasi"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if cat == "Barchasi":
        c.execute("SELECT id, user_id, category, title, description, image_path FROM products ORDER BY id DESC")
    else:
        c.execute("SELECT id, user_id, category, title, description, image_path FROM products WHERE category = ? ORDER BY id DESC", (cat,))
    rows = c.fetchall()
    conn.close()
    
    products = []
    for r in rows:
        products.append({
            "id": r[0],
            "user_id": r[1],
            "category": r[2],
            "title": r[3],
            "description": r[4],
            "image_path": r[5]
        })
    return products

@app.post("/api/add_product")
async def add_product(
    user_id: int = Form(...),
    username: str = Form(""),
    category: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(None)
):
    image_url = None
    if image and image.filename:
        ext = image.filename.split(".")[-1]
        fname = f"{user_id}_{asyncio.get_event_loop().time()}_{os.urandom(3).hex()}.{ext}"
        fpath = os.path.join("static", "uploads", fname)
        with open(fpath, "wb") as f:
            shutil.copyfileobj(image.file, f)
        image_url = f"/static/uploads/{fname}"

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO products (user_id, username, category, title, description, image_path) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, username, category, title, description, image_url)
    )
    conn.commit()
    conn.close()

    # Adminlarga xabar yuborish
    notif = f"📦 **Yangi e'lon!**\n\n🏷️ Kategoriya: {category}\n📝 Nomi: {title}\n📄 Tavsif: {description}\n👤 Foydalanuvchi: @{username or 'Nomaʼlum'}"
    for admin in [OWNER_ID, ADMIN_ID]:
        try:
            if image_url:
                await bot.send_photo(admin, photo=types.URLInputFile(f"{DOMAIN}{image_url}"), caption=notif)
            else:
                await bot.send_message(admin, notif)
        except:
            pass

    return {"success": True, "message": "✅ E'loningiz muvaffaqiyatli qo'shildi!"}

@app.get("/api/check_admin")
async def check_admin(user_id: int, username: str = ""):
    is_adm = is_admin_user(user_id, username)
    return {"is_admin": is_adm}

@app.post("/api/add_admin")
async def add_admin(username: str = Form(...)):
    clean_uname = username.lstrip('@').lower()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT OR IGNORE INTO admins (username) VALUES (?)", (clean_uname,))
        conn.commit()
        return {"success": True, "message": f"@{clean_uname} muvaffaqiyatli admin qilindi!"}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

@app.get("/api/admins")
async def get_admins():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username FROM admins")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

@app.post("/webhook")
async def webhook(req: Request):
    await dp.feed_update(bot, types.Update(**await req.json()))
    return {"ok": True}

@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("🛍️ **Uzprof.shop** ga xush kelibsiz!\n\nVeb-ilovaga kirib o'z mahsulot va xizmatlaringizni joylashingiz mumkin.")
