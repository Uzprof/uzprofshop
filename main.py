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
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- SOZLAMALAR VA ID'LAR ---
BOT_TOKEN = "8784665419:AAE8dF85EpYIA4vWX_5CTP30jzumqIUfREg"  # Tokeningiz
DOMAIN = "https://uzprofshop.onrender.com"
DB_PATH = "uzprof.db"

OWNER_ID = 7686687044
ADMIN_ID = 7875662532

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

os.makedirs("static/uploads", exist_ok=True)

# --- ZAMONAVIY VA KAFOLATLANGAN DIZAYN ---
HTML_CONTENT = """<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Uzprof.shop - Raqamli Bozor</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        :root {
            --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            --card-bg: rgba(255, 255, 255, 0.07);
            --border-glass: rgba(255, 255, 255, 0.12);
            --primary: #6366f1;
            --primary-hover: #4f46e5;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
        }
        body { font-family: 'Inter', system-ui, sans-serif; background: var(--bg-gradient); color: var(--text-main); min-height: 100vh; margin: 0; padding: 16px; }
        .app-container { max-width: 480px; margin: 0 auto; padding-bottom: 80px; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; background: var(--card-bg); backdrop-filter: blur(12px); border: 1px solid var(--border-glass); padding: 14px 18px; border-radius: 16px; }
        .logo { font-size: 18px; font-weight: 800; background: linear-gradient(90deg, #818cf8, #38bdf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .user-badge { font-size: 11px; background: rgba(99, 102, 241, 0.2); color: #818cf8; padding: 4px 10px; border-radius: 20px; border: 1px solid rgba(99, 102, 241, 0.3); }
        
        .search-box { position: relative; margin-bottom: 15px; }
        .search-box input { width: 100%; padding: 12px 16px 12px 42px; background: var(--card-bg); border: 1px solid var(--border-glass); border-radius: 12px; color: #fff; font-size: 14px; outline: none; box-sizing: border-box; }
        .search-icon { position: absolute; left: 14px; top: 14px; color: var(--text-muted); }

        .menu-scroll { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 5px; margin-bottom: 20px; scrollbar-width: none; }
        .menu-scroll::-webkit-scrollbar { display: none; }
        .menu-pill { background: var(--card-bg); border: 1px solid var(--border-glass); color: var(--text-muted); padding: 8px 14px; border-radius: 20px; font-size: 12px; font-weight: 500; white-space: nowrap; cursor: pointer; }
        .menu-pill.active { background: var(--primary); color: #fff; border-color: var(--primary); }

        .nav-tabs { display: flex; background: var(--card-bg); backdrop-filter: blur(12px); border: 1px solid var(--border-glass); padding: 6px; border-radius: 14px; margin-bottom: 20px; }
        .tab-btn { flex: 1; background: transparent; border: none; color: var(--text-muted); padding: 10px; font-size: 13px; font-weight: 600; border-radius: 10px; cursor: pointer; text-align: center; }
        .tab-btn.active { background: rgba(255, 255, 255, 0.1); color: #fff; }

        .product-grid { display: grid; grid-template-columns: 1fr; gap: 16px; }
        .card { background: var(--card-bg); backdrop-filter: blur(12px); border: 1px solid var(--border-glass); border-radius: 16px; overflow: hidden; }
        .card img { width: 100%; height: 180px; object-fit: cover; background: #1e293b; }
        .card-body { padding: 16px; }
        .card-cat { font-size: 11px; color: var(--accent); text-transform: uppercase; font-weight: 700; margin-bottom: 6px; }
        .card-title { font-size: 16px; font-weight: 700; margin: 0 0 8px 0; color: #fff; }
        .card-desc { font-size: 13px; color: var(--text-muted); margin: 0; line-height: 1.4; }

        .form-card { background: var(--card-bg); backdrop-filter: blur(12px); border: 1px solid var(--border-glass); padding: 20px; border-radius: 16px; }
        .form-group { margin-bottom: 14px; }
        label { display: block; font-size: 12px; font-weight: 600; color: var(--text-muted); margin-bottom: 6px; }
        input, select, textarea { width: 100%; padding: 12px; background: rgba(15, 23, 42, 0.6); border: 1px solid var(--border-glass); border-radius: 10px; color: #fff; font-size: 14px; box-sizing: border-box; outline: none; }
        .btn-submit { width: 100%; background: var(--primary); color: white; border: none; padding: 14px; border-radius: 10px; font-weight: 700; font-size: 14px; cursor: pointer; }
        .admin-item { display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.2); padding: 10px 14px; border-radius: 10px; margin-bottom: 8px; font-size: 13px; }
        .delete-btn { background: #ef4444; color: white; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 11px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="header">
            <div class="logo">⚡ Uzprof.shop</div>
            <div class="user-badge" id="userBadge">ID aniqlanmoqda...</div>
        </div>

        <div class="nav-tabs">
            <button class="tab-btn active" onclick="switchTab('feed')" id="tabFeed">📦 E'lonlar</button>
            <button class="tab-btn" onclick="switchTab('add')" id="tabAdd">➕ E'lon berish</button>
            <button class="tab-btn" onclick="switchTab('admin')" id="tabAdmin" style="display:none;">⚙️ Admin Panel</button>
        </div>

        <div id="sectionFeed">
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" id="searchInput" placeholder="Xizmat yoki mahsulotlarni qidirish..." oninput="filterProducts()">
            </div>
            <div class="menu-scroll">
                <div class="menu-pill active" onclick="selectCategory('Barchasi', this)">🔥 Barchasi</div>
                <div class="menu-pill" onclick="selectCategory('Telegram Botlar', this)">🤖 Telegram Botlar</div>
                <div class="menu-pill" onclick="selectCategory('Web Dasturlash', this)">💻 Web Dasturlash</div>
                <div class="menu-pill" onclick="selectCategory('Skriptlar va Kodlar', this)">📜 Skriptlar</div>
                <div class="menu-pill" onclick="selectCategory('Dizayn va Grafika', this)">🎨 Dizayn</div>
            </div>
            <div class="product-grid" id="productGrid"></div>
        </div>

        <div id="sectionAdd" style="display:none;">
            <div class="form-card">
                <h3 style="margin-top:0; color:#fff;">Yangi E'lon Qo'shish</h3>
                <div class="form-group">
                    <label>Kategoriya</label>
                    <select id="pCat">
                        <option value="Telegram Botlar">🤖 Telegram Botlar</option>
                        <option value="Web Dasturlash">💻 Web Dasturlash</option>
                        <option value="Skriptlar va Kodlar">📜 Skriptlar va Kodlar</option>
                        <option value="Dizayn va Grafika">🎨 Dizayn va Grafika</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Sarlavha (Nomi)</label>
                    <input type="text" id="pTitle" placeholder="Masalan: Professional Telegram bot">
                </div>
                <div class="form-group">
                    <label>Batafsil tavsif va narxi</label>
                    <textarea id="pDesc" rows="3" placeholder="Narxi, imkoniyatlari va shartlari..."></textarea>
                </div>
                <div class="form-group">
                    <label>Mahsulot/Xizmat rasmi</label>
                    <input type="file" id="pImage" accept="image/*">
                </div>
                <button class="btn-submit" onclick="submitProduct()">🚀 E'lonni Jo'natish</button>
                <p id="formMsg" style="text-align:center; font-size:13px; margin-top:10px; font-weight:600;"></p>
            </div>
        </div>

        <div id="sectionAdmin" style="display:none;">
            <div class="form-card">
                <h3 style="margin-top:0; color:#fff;">Admin Boshqaruvi</h3>
                <p style="font-size:12px; color:var(--text-muted);">Barcha e'lonlarni boshqarish va o'chirish.</p>
                <div id="adminProductList"></div>
            </div>
        </div>
    </div>

    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        
        // Telegram ID ni aniqlash (Agar brauzerdan ochilsa URL parametridan oladi)
        const urlParams = new URLSearchParams(window.location.search);
        let urlUserId = urlParams.get('user_id');

        let userId = (tg.initDataUnsafe && tg.initDataUnsafe.user) ? tg.initDataUnsafe.user.id : (urlUserId ? parseInt(urlUserId) : 7686687044);
        
        document.getElementById('userBadge').innerText = `ID: ${userId}`;

        // Adminlar ro'yxati
        const ADMINS = [7686687044, 7875662532];
        if (ADMINS.includes(userId)) {
            document.getElementById('tabAdmin').style.display = 'block';
        }

        let currentCategory = 'Barchasi';
        let allProducts = [];

        function switchTab(tab) {
            document.getElementById('sectionFeed').style.display = tab === 'feed' ? 'block' : 'none';
            document.getElementById('sectionAdd').style.display = tab === 'add' ? 'block' : 'none';
            document.getElementById('sectionAdmin').style.display = tab === 'admin' ? 'block' : 'none';
            
            document.getElementById('tabFeed').classList.toggle('active', tab === 'feed');
            document.getElementById('tabAdd').classList.toggle('active', tab === 'add');
            document.getElementById('tabAdmin').classList.toggle('active', tab === 'admin');

            if (tab === 'feed') loadProducts();
            if (tab === 'admin') loadAdminProducts();
        }

        async function loadProducts() {
            let res = await fetch('/api/products');
            allProducts = await res.json();
            renderProducts(allProducts);
        }

        function renderProducts(products) {
            let grid = document.getElementById('productGrid');
            grid.innerHTML = '';
            let query = document.getElementById('searchInput').value.toLowerCase();
            
            let filtered = products.filter(p => {
                let matchesCat = (currentCategory === 'Barchasi' || p.category === currentCategory);
                let matchesSearch = p.title.toLowerCase().includes(query) || p.description.toLowerCase().includes(query);
                return matchesCat && matchesSearch;
            });

            if (filtered.length === 0) {
                grid.innerHTML = '<p style="text-align:center; color:var(--text-muted); font-size:13px;">E\'lonlar topilmadi.</p>';
                return;
            }

            filtered.forEach(p => {
                let card = document.createElement('div');
                card.className = 'card';
                card.innerHTML = `
                    ${p.image_path ? `<img src="${p.image_path}" alt="img">` : ''}
                    <div class="card-body">
                        <div class="card-cat">${p.category}</div>
                        <div class="card-title">${p.title}</div>
                        <div class="card-desc">${p.description}</div>
                    </div>
                `;
                grid.appendChild(card);
            });
        }

        function selectCategory(cat, el) {
            currentCategory = cat;
            document.querySelectorAll('.menu-pill').forEach(p => p.classList.remove('active'));
            el.classList.add('active');
            renderProducts(allProducts);
        }

        function filterProducts() { renderProducts(allProducts); }

        async function submitProduct() {
            let fd = new FormData();
            fd.append("user_id", userId);
            fd.append("category", document.getElementById('pCat').value);
            fd.append("title", document.getElementById('pTitle').value);
            fd.append("description", document.getElementById('pDesc').value);
            let img = document.getElementById('pImage').files[0];
            if (img) fd.append("image", img);

            let res = await fetch('/api/add_product', { method: 'POST', body: fd });
            let data = await res.json();
            let msg = document.getElementById('formMsg');
            msg.style.color = data.success ? '#38bdf8' : '#ef4444';
            msg.innerText = data.message;

            if (data.success) {
                document.getElementById('pTitle').value = '';
                document.getElementById('pDesc').value = '';
                document.getElementById('pImage').value = '';
                setTimeout(() => switchTab('feed'), 1200);
            }
        }

        async function loadAdminProducts() {
            let res = await fetch('/api/products');
            let products = await res.json();
            let container = document.getElementById('adminProductList');
            container.innerHTML = '';

            if (products.length === 0) {
                container.innerHTML = '<p style="color:var(--text-muted); font-size:13px;">Hozircha e\'lonlar yo\'q.</p>';
                return;
            }

            products.forEach(p => {
                let item = document.createElement('div');
                item.className = 'admin-item';
                item.innerHTML = `
                    <div>
                        <strong style="color:#fff;">${p.title}</strong><br>
                        <span style="font-size:11px; color:var(--text-muted);">${p.category}</span>
                    </div>
                    <button class="delete-btn" onclick="deleteProduct(${p.id})">O'chirish</button>
                `;
                container.appendChild(item);
            });
        }

        async function deleteProduct(id) {
            if (!confirm("Rostdan ham bu e'lonni o'chirmoqchimisiz?")) return;
            let fd = new URLSearchParams();
            fd.append("product_id", id);
            fd.append("user_id", userId);
            let res = await fetch('/api/delete_product', { method: 'POST', body: fd });
            let data = await res.json();
            if (data.success) loadAdminProducts();
        }

        loadProducts();
    </script>
</body>
</html>"""

# --- BAZA VA SERVER ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT,
            title TEXT,
            description TEXT,
            image_path TEXT
        )
    """)
    conn.commit()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    try:
        await bot.set_webhook(f"{DOMAIN}/webhook")
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
async def get_products():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, user_id, category, title, description, image_path FROM products ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "user_id": r[1], "category": r[2], "title": r[3], "description": r[4], "image_path": r[5]} for r in rows]

@app.post("/api/add_product")
async def add_product(user_id: int = Form(...), category: str = Form(...), title: str = Form(...), description: str = Form(...), image: UploadFile = File(None)):
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
    c.execute("INSERT INTO products (user_id, category, title, description, image_path) VALUES (?, ?, ?, ?, ?)", (user_id, category, title, description, image_url))
    conn.commit()
    conn.close()

    notif = f"📦 **Yangi e'lon!**\n\n🏷️ Kategoriya: {category}\n📝 Nomi: {title}\n📄 Tavsif: {description}"
    for admin in [OWNER_ID, ADMIN_ID]:
        try:
            if image_url:
                await bot.send_photo(admin, photo=types.URLInputFile(f"{DOMAIN}{image_url}"), caption=notif)
            else:
                await bot.send_message(admin, notif)
        except:
            pass

    return {"success": True, "message": "✅ E'loningiz muvaffaqiyatli joylandi!"}

@app.post("/api/delete_product")
async def delete_product(product_id: int = Form(...), user_id: int = Form(...)):
    if user_id not in [OWNER_ID, ADMIN_ID]:
        return {"success": False, "message": "Sizda bu huquq yo'q!"}
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return {"success": True}

@app.post("/webhook")
async def webhook(req: Request):
    await dp.feed_update(bot, types.Update(**await req.json()))
    return {"ok": True}

# --- BOT BUYRUQLARI (WEB-APP TUGMA BILAN) ---
@dp.message(Command("start"))
async def start(msg: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Uzprof.shop ni ochish", web_app=types.WebAppInfo(url=f"{DOMAIN}/?user_id={msg.from_user.id}"))
    await msg.answer("⚡ **Uzprof.shop** — Raqamli xizmatlar bozori!\n\nPastdagi tugmani bosing:", reply_markup=kb.as_markup())
