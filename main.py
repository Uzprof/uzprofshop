import os, sqlite3, shutil, asyncio
from typing import Optional
from fastapi import FastAPI, Request, Form, File, UploadFile, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

import database as db

BOT_TOKEN = "8784665419:AAFeTYdY1eiA9jWu_G_smi4Ag2wGA3VSDiQ"

# Terminalda SSH ishga tushgach, berilgan https://... havolani shu yerga qo'yasiz
DOMAIN = "https://uzprofshop.onrender.com" 

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = FastAPI(title="Uzprof.shop API")

os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    conn = db.get_db()
    conn.execute("""
        INSERT INTO users (telegram_id, username, full_name)
        VALUES (?, ?, ?) ON CONFLICT(telegram_id) DO UPDATE SET username=?, full_name=?
    """, (message.from_user.id, message.from_user.username, message.from_user.full_name,
          message.from_user.username, message.from_user.full_name))
    conn.commit()
    conn.close()

    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[[
            types.InlineKeyboardButton(text="🛍️ Uzprof.shop Bozoriga kirish", web_app=types.WebAppInfo(url=DOMAIN))
        ]]
    )
    await message.answer(f"Xush kelibsiz, {message.from_user.first_name}!\nUzprof.shop milliy bozorida xarid qiling yoki e'lon joylang.", reply_markup=kb)

@app.get("/", response_class=HTMLResponse)
async def get_webapp(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/categories")
async def get_categories():
    conn = db.get_db()
    cats = conn.execute("SELECT * FROM categories").fetchall()
    conn.close()
    return JSONResponse([dict(c) for c in cats])

@app.get("/api/products")
async def get_products(
    category: str = Query("all"),
    search: str = Query(""),
    sort: str = Query("new"),
    status: str = Query("approved"),
    user_id: Optional[int] = Query(None)
):
    conn = db.get_db()
    
    if status != "approved" and (not user_id or not db.is_admin(user_id)):
        return JSONResponse(status_code=403, content={"message": "Ruxsat berilmagan!"})

    query = "SELECT * FROM products WHERE status = ?"
    params = [status]

    if category != "all":
        query += " AND category = ?"
        params.append(category)

    if search:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    if sort == "cheap":
        query += " ORDER BY price ASC"
    elif sort == "expensive":
        query += " ORDER BY price DESC"
    else:
        query += " ORDER BY id DESC"

    products = [dict(row) for row in conn.execute(query, params).fetchall()]
    conn.close()
    return JSONResponse(products)

@app.post("/api/products/add")
async def add_product(
    title: str = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    old_price: float = Form(0),
    user_id: int = Form(...),
    username: str = Form(""),
    image: UploadFile = File(...)
):
    file_ext = image.filename.split(".")[-1]
    filename = f"{user_id}_{int(asyncio.get_event_loop().time())}.{file_ext}"
    path = os.path.join("static/uploads", filename)
    
    with open(path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    conn = db.get_db()
    conn.execute("""
        INSERT INTO products (title, category, description, price, old_price, image_path, owner_id, owner_username)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, category, description, price, old_price, f"/static/uploads/{filename}", user_id, username))
    conn.commit()
    conn.close()

    return JSONResponse({"success": True, "message": "E'lon qilindi! Admin tekshiruvidan so'ng bozorda ko'rinadi."})

@app.post("/api/admin/moderate")
async def moderate_product(product_id: int = Form(...), action: str = Form(...), user_id: int = Form(...)):
    if not db.is_admin(user_id):
        raise HTTPException(status_code=403, detail="Ruxsat yo'q!")
    
    new_status = "approved" if action == "approve" else "rejected"
    conn = db.get_db()
    conn.execute("UPDATE products SET status = ? WHERE id = ?", (new_status, product_id))
    conn.commit()
    conn.close()
    return JSONResponse({"success": True, "message": f"E'lon statusi {new_status} deb o'zgartirildi."})

@app.post("/api/admin/manage-role")
async def manage_role(target_id: int = Form(...), new_role: str = Form(...), requester_id: int = Form(...)):
    if requester_id != db.SUPER_ADMIN_ID:
        raise HTTPException(status_code=403, detail="Faqat Super Admin (ID: 7686687044) admin tayinlay oladi!")
    
    conn = db.get_db()
    conn.execute("UPDATE users SET role = ? WHERE telegram_id = ?", (new_role, target_id))
    conn.commit()
    conn.close()
    return JSONResponse({"success": True, "message": f"Foydalanuvchi {target_id} ga '{new_role}' roli berildi."})

@app.get("/api/user/me")
async def get_me(user_id: int = Query(...)):
    conn = db.get_db()
    user = conn.execute("SELECT * FROM users WHERE telegram_id = ?", (user_id,)).fetchone()
    conn.close()
    if not user:
        return JSONResponse({"role": "user", "is_superadmin": user_id == db.SUPER_ADMIN_ID, "is_admin": user_id == db.SUPER_ADMIN_ID})
    
    u_dict = dict(user)
    u_dict["is_superadmin"] = (user_id == db.SUPER_ADMIN_ID)
    u_dict["is_admin"] = db.is_admin(user_id)
    return JSONResponse(u_dict)

async def main():
    import uvicorn
    db.init_db()
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    await asyncio.gather(dp.start_polling(bot), server.serve())

if __name__ == "__main__":
    asyncio.run(main()) 
