import sqlite3

SUPER_ADMIN_ID = 7686687044

def get_db():
    conn = sqlite3.connect("uzprof.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        INSERT INTO users (telegram_id, username, full_name, role)
        VALUES (?, 'uzemn', 'Super Admin', 'superadmin')
        ON CONFLICT(telegram_id) DO UPDATE SET role='superadmin'
    """, (SUPER_ADMIN_ID,))

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            icon TEXT
        )
    """)
    
    default_cats = [
        ("📱 Elektronika", "phone"),
        ("👔 Kiyim-kechak", "shirt"), 
        ("🛠️ Xizmatlar", "tools"),
        ("💻 Dasturlash", "code"),
        ("🏠 Uy va Ro'zg'or", "home")
    ]
    cursor.executemany("INSERT OR IGNORE INTO categories (name, icon) VALUES (?, ?)", default_cats)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            old_price REAL DEFAULT 0,
            image_path TEXT NOT NULL,
            owner_id INTEGER NOT NULL,
            owner_username TEXT,
            views INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users (telegram_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            user_id INTEGER,
            product_id INTEGER,
            PRIMARY KEY (user_id, product_id)
        )
    """)

    conn.commit()
    conn.close()

def is_admin(user_id: int) -> bool:
    if user_id == SUPER_ADMIN_ID:
        return True
    conn = get_db()
    res = conn.execute("SELECT role FROM users WHERE telegram_id = ?", (user_id,)).fetchone()
    conn.close()
    return res is not None and res["role"] in ["admin", "superadmin"]

if __name__ == "__main__":
    init_db()
