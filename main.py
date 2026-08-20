import os
import shutil
import sqlite3
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# --- SOZLAMALAR ---
DB_PATH = "uzprof.db"
OWNER_ID = 7686687044

os.makedirs("static/uploads", exist_ok=True)

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
            price TEXT,
            old_price TEXT,
            contact_url TEXT,
            image_path TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            telegram_id INTEGER UNIQUE
        )
    """)
    conn.commit()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Uzprof.shop", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

HTML_CONTENT = """<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Uzprof.shop</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        :root {
            --bg-color: #f3f4f6;
            --card-bg: #ffffff;
            --primary: #6d28d9;
            --primary-hover: #5b21b6;
            --text-main: #111827;
            --text-muted: #6b7280;
            --border: #e5e7eb;
        }
        * { box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg-color); color: var(--text-main); margin: 0; padding: 12px; padding-bottom: 80px; }
        .container { max-width: 480px; margin: 0 auto; }
        
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .logo { font-size: 22px; font-weight: 900; color: var(--primary); }
        .badge { font-size: 10px; font-weight: 800; background: #e5e7eb; color: #374151; padding: 3px 8px; border-radius: 6px; }

        .search-box input { width: 100%; padding: 10px 14px; background: #ffffff; border: 1px solid var(--border); border-radius: 10px; font-size: 13px; color: var(--text-main); outline: none; margin-bottom: 12px; }
        
        .categories { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 6px; margin-bottom: 14px; scrollbar-width: none; }
        .categories::-webkit-scrollbar { display: none; }
        .cat-pill { background: #ffffff; border: 1px solid var(--border); color: #374151; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; white-space: nowrap; cursor: pointer; user-select: none; }
        .cat-pill.active { background: var(--primary); color: #ffffff; border-color: var(--primary); }

        .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
        .card { background: var(--card-bg); border-radius: 14px; overflow: hidden; border: 1px solid var(--border); display: flex; flex-direction: column; justify-content: space-between; }
        .card-img { width: 100%; height: 130px; object-fit: cover; background: #e5e7eb; }
        .card-body { padding: 10px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }
        .card-title { font-size: 13px; font-weight: 700; color: var(--text-main); margin-bottom: 6px; line-height: 1.2; }
        .price-box { margin-bottom: 8px; }
        .price { font-size: 13px; font-weight: 800; color: var(--primary); }
        .old-price { font-size: 10px; color: var(--text-muted); text-decoration: line-through; margin-left: 4px; }
        .btn-contact { width: 100%; background: var(--primary); color: white; border: none; padding: 8px 0; border-radius: 8px; font-size: 11px; font-weight: 700; cursor: pointer; text-decoration: none; display: flex; align-items: center; justify-content: center; }

        .form-card { background: white; padding: 16px; border-radius: 14px; border: 1px solid var(--border); margin-bottom: 12px; }
        .form-group { margin-bottom: 10px; }
        label { display: block; font-size: 11px; font-weight: 700; color: var(--text-muted); margin-bottom: 4px; }
        input, select, textarea { width: 100%; padding: 10px; background: #f9fafb; border: 1px solid var(--border); border-radius: 8px; font-size: 13px; outline: none; }
        .btn-submit { width: 100%; background: var(--primary); color: white; border: none; padding: 10px; border-radius: 8px; font-weight: 700; cursor: pointer; }

        .admin-item { display: flex; justify-content: space-between; align-items: center; background: #f9fafb; padding: 8px 12px; border-radius: 8px; border: 1px solid var(--border); margin-bottom: 6px; font-size: 12px; }
        .btn-del { background: #ef4444; color: white; border: none; padding: 6px 10px; border-radius: 6px; cursor: pointer; font-size: 11px; font-weight: bold; }

        .bottom-nav { position: fixed; bottom: 0; left: 0; right: 0; background: #ffffff; border-top: 1px solid var(--border); display: flex; justify-content: space-around; padding: 8px 0; max-width: 480px; margin: 0 auto; z-index: 999; }
        .nav-item { display: flex; flex-direction: column; align-items: center; font-size: 10px; color: var(--text-muted); cursor: pointer; border: none; background: transparent; width: 33.3%; }
        .nav-item.active { color: var(--primary); font-weight: 700; }
        .nav-item svg { width: 20px; height: 20px; margin-bottom: 2px; fill: currentColor; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">Uzprof.shop</div>
            <div class="badge" id="roleBadge">USER</div>
        </div>

        <!-- Feed Section -->
        <div id="secFeed">
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="Mahsulot yoki xizmatlarni qidirish..." oninput="filterProducts()">
            </div>
            <div class="categories">
                <div class="cat-pill active" onclick="setCat('Barchasi', this)">Barchasi</div>
                <div class="cat-pill" onclick="setCat('📱 Elektronika', this)">📱 Elektronika</div>
                <div class="cat-pill" onclick="setCat('👔 Kiyim-kechak', this)">👔 Kiyim-kechak</div>
                <div class="cat-pill" onclick="setCat('🤖 Telegram Bot', this)">🤖 Telegram Bot</div>
                <div class="cat-pill" onclick="setCat('📜 Skriptlar', this)">📜 Skriptlar</div>
            </div>
            <div class="grid" id="productGrid"></div>
        </div>

        <!-- Add Section -->
        <div id="secAdd" style="display:none;">
            <div class="form-card">
                <h4 style="margin:0 0 12px 0;">Yangi E'lon Berish</h4>
                <div class="form-group"><label>Kategoriya</label>
                    <select id="pCat">
                        <option value="🤖 Telegram Bot">🤖 Telegram Bot</option>
                        <option value="📜 Skriptlar">📜 Skriptlar</option>
                        <option value="📱 Elektronika">📱 Elektronika</option>
                        <option value="👔 Kiyim-kechak">👔 Kiyim-kechak</option>
                    </select>
                </div>
                <div class="form-group"><label>Sarlavha</label><input type="text" id="pTitle" placeholder="Masalan: Telegram bot xizmati"></div>
                <div class="form-group"><label>Tavsif</label><textarea id="pDesc" rows="3" placeholder="Batafsil ma'lumot..."></textarea></div>
                <div class="form-group"><label>Narxi</label><input type="text" id="pPrice" placeholder="30 000 UZS"></div>
                <div class="form-group"><label>Eski narxi (Ixtiyoriy)</label><input type="text" id="pOldPrice" placeholder="59 000 UZS"></div>
                <div class="form-group"><label>Aloqa uchun havola / Username</label><input type="text" id="pContact" placeholder="https://t.me/username"></div>
                <div class="form-group"><label>Rasm</label><input type="file" id="pImage" accept="image/*"></div>
                <button class="btn-submit" onclick="submitProduct()">E'lonni Joylash</button>
                <p id="addMsg" style="font-size:11px; text-align:center; margin-top:8px;"></p>
            </div>
        </div>

        <!-- Admin Section -->
        <div id="secAdmin" style="display:none;">
            <div class="form-card">
                <h4 style="margin:0 0 10px 0;">Admin Qo'shish</h4>
                <div class="form-group">
                    <label>Admin Username (@ bilan yoki usiz)</label>
                    <input type="text" id="adminUsername" placeholder="username">
                </div>
                <button class="btn-submit" onclick="addAdmin()">Admin Qilish</button>
                <p id="adminMsg" style="font-size:11px; text-align:center; margin-top:6px;"></p>
            </div>

            <div class="form-card">
                <h4 style="margin:0 0 10px 0;">E'lonlarni Boshqarish va O'chirish</h4>
                <div id="adminProdList"></div>
            </div>
        </div>
    </div>

    <!-- Bottom Nav -->
    <div class="bottom-nav">
        <button class="nav-item active" onclick="nav('feed')" id="navFeed">
            <svg viewBox="0 0 24 24"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>Bozor
        </button>
        <button class="nav-item" onclick="nav('add')" id="navAdd">
            <svg viewBox="0 0 24 24"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>E'lon Berish
        </button>
        <button class="nav-item" onclick="nav('admin')" id="navAdmin" style="display:none;">
            <svg viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-5.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8s0 0 0 0z"/></svg>Admin
        </button>
    </div>

    <script>
        const OWNER_ID = 7686687044;
        let userId = 0;
        let currentCat = 'Barchasi';
        let allProducts = [];

        // Telegram WebApp initialization
        try {
            if (window.Telegram && window.Telegram.WebApp) {
                const tg = window.Telegram.WebApp;
                tg.ready();
                tg.expand();
                if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
                    userId = tg.initDataUnsafe.user.id;
                }
            }
        } catch (e) {
            console.warn("WebApp init warning:", e);
        }

        // Test uchun URL parametridan ID olish
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('user_id')) {
            userId = parseInt(urlParams.get('user_id'));
        }

        // Agar brauzerda ochilsa, default qilib OWNER_ID beriladi
        if (!userId) userId = OWNER_ID;

        document.addEventListener("DOMContentLoaded", function () {
            if (userId === OWNER_ID) {
                const navAdmin = document.getElementById('navAdmin');
                const roleBadge = document.getElementById('roleBadge');
                if (navAdmin) navAdmin.style.display = 'flex';
                if (roleBadge) roleBadge.innerText = 'SUPERADMIN';
            }
            loadProducts();
        });

        function nav(tab) {
            const secFeed = document.getElementById('secFeed');
            const secAdd = document.getElementById('secAdd');
            const secAdmin = document.getElementById('secAdmin');

            if (secFeed) secFeed.style.display = tab === 'feed' ? 'block' : 'none';
            if (secAdd) secAdd.style.display = tab === 'add' ? 'block' : 'none';
            if (secAdmin) secAdmin.style.display = tab === 'admin' ? 'block' : 'none';

            const navFeed = document.getElementById('navFeed');
            const navAdd = document.getElementById('navAdd');
            const navAdmin = document.getElementById('navAdmin');

            if (navFeed) navFeed.classList.toggle('active', tab === 'feed');
            if (navAdd) navAdd.classList.toggle('active', tab === 'add');
            if (navAdmin) navAdmin.classList.toggle('active', tab === 'admin');

            if (tab === 'feed') loadProducts();
            if (tab === 'admin') loadAdminProducts();
        }

        async function loadProducts() {
            try {
                let res = await fetch('/api/products');
                allProducts = await res.json();
                renderProducts(allProducts);
            } catch (e) {
                console.error("Fetch error:", e);
            }
        }

        function renderProducts(products) {
            const grid = document.getElementById('productGrid');
            if (!grid) return;
            grid.innerHTML = '';

            const searchInput = document.getElementById('searchInput');
            const query = searchInput ? searchInput.value.toLowerCase().trim() : '';

            let filtered = products.filter(p => {
                let matchCat = (currentCat === 'Barchasi' || p.category === currentCat);
                let matchQuery = (p.title || '').toLowerCase().includes(query) || (p.description || '').toLowerCase().includes(query);
                return matchCat && matchQuery;
            });

            if (filtered.length === 0) {
                grid.innerHTML = '<p style="grid-column: span 2; text-align:center; font-size:12px; color:var(--text-muted); margin-top:20px;">Hozircha e\'lonlar mavjud emas.</p>';
                return;
            }

            filtered.forEach(p => {
                let card = document.createElement('div');
                card.className = 'card';
                let contactLink = p.contact_url || '#';
                if (contactLink && !contactLink.startsWith('http')) {
                    contactLink = 'https://t.me/' + contactLink.replace('@', '');
                }

                card.innerHTML = `
                    ${p.image_path ? `<img src="${p.image_path}" class="card-img" alt="img">` : ''}
                    <div class="card-body">
                        <div>
                            <div class="card-title">${p.title || ''}</div>
                            <div class="price-box">
                                <span class="price">${p.price || ''}</span>
                                ${p.old_price ? `<span class="old-price">${p.old_price}</span>` : ''}
                            </div>
                        </div>
                        <a href="${contactLink}" target="_blank" class="btn-contact">💬 Aloqaga Chiqish</a>
                    </div>
                `;
                grid.appendChild(card);
            });
        }

        function setCat(cat, el) {
            currentCat = cat;
            document.querySelectorAll('.cat-pill').forEach(c => c.classList.remove('active'));
            if (el) el.classList.add('active');
            renderProducts(allProducts);
        }

        function filterProducts() {
            renderProducts(allProducts);
        }

        async function submitProduct() {
            const title = document.getElementById('pTitle').value.trim();
            const desc = document.getElementById('pDesc').value.trim();
            const msg = document.getElementById('addMsg');

            if (!title || !desc) {
                msg.style.color = 'red';
                msg.innerText = 'Sarlavha va tavsifni to\'ldiring!';
                return;
            }

            let fd = new FormData();
            fd.append("user_id", userId);
            fd.append("category", document.getElementById('pCat').value);
            fd.append("title", title);
            fd.append("description", desc);
            fd.append("price", document.getElementById('pPrice').value);
            fd.append("old_price", document.getElementById('pOldPrice').value);
            fd.append("contact_url", document.getElementById('pContact').value);
            
            let imgInput = document.getElementById('pImage');
            if (imgInput && imgInput.files[0]) {
                fd.append("image", imgInput.files[0]);
            }

            msg.style.color = 'blue';
            msg.innerText = 'Joylanmoqda...';

            try {
                let res = await fetch('/api/add_product', { method: 'POST', body: fd });
                let data = await res.json();
                msg.style.color = data.success ? 'green' : 'red';
                msg.innerText = data.message;

                if (data.success) {
                    document.getElementById('pTitle').value = '';
                    document.getElementById('pDesc').value = '';
                    if (imgInput) imgInput.value = '';
                    document.getElementById('pPrice').value = '';
                    document.getElementById('pOldPrice').value = '';
                    document.getElementById('pContact').value = '';
                    setTimeout(() => nav('feed'), 800);
                }
            } catch (e) {
                msg.style.color = 'red';
                msg.innerText = 'Xatolik yuz berdi!';
            }
        }

        async function loadAdminProducts() {
            try {
                let res = await fetch('/api/products');
                let products = await res.json();
                const container = document.getElementById('adminProdList');
                if (!container) return;
                container.innerHTML = '';

                if (products.length === 0) {
                    container.innerHTML = '<p style="font-size:12px; color:var(--text-muted);">E\'lonlar yo\'q.</p>';
                    return;
                }

                products.forEach(p => {
                    let div = document.createElement('div');
                    div.className = 'admin-item';
                    div.innerHTML = `
                        <div>
                            <strong>${p.title}</strong><br>
                            <span style="color:var(--text-muted); font-size:10px;">${p.category} | ${p.price || ''}</span>
                        </div>
                        <button class="btn-del" onclick="deleteProduct(${p.id})">O'chirish</button>
                    `;
                    container.appendChild(div);
                });
            } catch (e) {
                console.error(e);
            }
        }

        async function deleteProduct(id) {
            if (!confirm("Ushbu e'lonni o'chirmoqchimisiz?")) return;
            let fd = new URLSearchParams();
            fd.append("product_id", id);
            fd.append("user_id", userId);

            let res = await fetch('/api/delete_product', { method: 'POST', body: fd });
            let data = await res.json();
            if (data.success) {
                loadAdminProducts();
            } else {
                alert(data.message);
            }
        }

        async function addAdmin() {
            const unameInput = document.getElementById('adminUsername');
            const uname = unameInput ? unameInput.value.trim() : '';
            const msg = document.getElementById('adminMsg');

            if (!uname) {
                msg.style.color = 'red';
                msg.innerText = 'Usernameni kiriting!';
                return;
            }

            let fd = new URLSearchParams();
            fd.append("username", uname);
            fd.append("user_id", userId);

            let res = await fetch('/api/add_admin', { method: 'POST', body: fd });
            let data = await res.json();
            msg.style.color = data.success ? 'green' : 'red';
            msg.innerText = data.message;
            if (data.success && unameInput) unameInput.value = '';
        }
    </script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=HTML_CONTENT)

@app.get("/api/products")
async def get_products():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, user_id, category, title, description, price, old_price, contact_url, image_path FROM products ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    return [{
        "id": r[0], "user_id": r[1], "category": r[2], "title": r[3],
        "description": r[4], "price": r[5], "old_price": r[6],
        "contact_url": r[7], "image_path": r[8]
    } for r in rows]

@app.post("/api/add_product")
async def add_product(
    user_id: int = Form(...),
    category: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    price: str = Form(""),
    old_price: str = Form(""),
    contact_url: str = Form(""),
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
    c.execute("""
        INSERT INTO products (user_id, category, title, description, price, old_price, contact_url, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, category, title, description, price, old_price, contact_url, image_url))
    conn.commit()
    conn.close()

    return {"success": True, "message": "E'lon muvaffaqiyatli qo'shildi!"}

@app.post("/api/delete_product")
async def delete_product(product_id: int = Form(...), user_id: int = Form(...)):
    if user_id != OWNER_ID:
        return {"success": False, "message": "Faqat Owner o'chira oladi!"}

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return {"success": True}

@app.post("/api/add_admin")
async def add_admin(username: str = Form(...), user_id: int = Form(...)):
    if user_id != OWNER_ID:
        return {"success": False, "message": "Faqat Owner admin qo'shishi mumkin!"}

    clean_username = username.replace("@", "").strip().lower()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO admins (username) VALUES (?)", (clean_username,))
        conn.commit()
        conn.close()
        return {"success": True, "message": f"@{clean_username} saqlandi!"}
    except sqlite3.IntegrityError:
        conn.close()
        return {"success": False, "message": "Bu foydalanuvchi allaqachon mavjud!"}
