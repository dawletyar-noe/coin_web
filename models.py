import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

from config import DB_PATH, ADMIN_USERNAME, ADMIN_PASSWORD


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            coins INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS topup_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount_uzs INTEGER NOT NULL,
            coins INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            game_code TEXT NOT NULL,
            game_title TEXT NOT NULL,
            package_title TEXT NOT NULL,
            coins_price INTEGER NOT NULL,
            game_account_id TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    # Admin hisobini config.py dagi ma'lumotlar bilan sinxronlash
    cur.execute("SELECT * FROM admin WHERE username = ?", (ADMIN_USERNAME,))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO admin (username, password_hash) VALUES (?, ?)",
            (ADMIN_USERNAME, generate_password_hash(ADMIN_PASSWORD)),
        )

    conn.commit()
    conn.close()


def now():
    return datetime.utcnow().isoformat()


# ===== FOYDALANUVCHILAR =====

def create_user(username, password_hash):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, password_hash, coins, created_at) VALUES (?, ?, 0, ?)",
        (username, password_hash, now()),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id


def get_user_by_username(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def add_coins(user_id, amount):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET coins = coins + ? WHERE id = ?", (amount, user_id))
    conn.commit()
    conn.close()


def deduct_coins(user_id, amount):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET coins = coins - ? WHERE id = ?", (amount, user_id))
    conn.commit()
    conn.close()


# ===== TO'LDIRISH SO'ROVLARI =====

def create_topup_request(user_id, amount_uzs, coins):
    conn = get_connection()
    cur = conn.cursor()
    n = now()
    cur.execute(
        "INSERT INTO topup_requests (user_id, amount_uzs, coins, status, created_at, updated_at) VALUES (?, ?, ?, 'pending', ?, ?)",
        (user_id, amount_uzs, coins, n, n),
    )
    conn.commit()
    req_id = cur.lastrowid
    conn.close()
    return req_id


def get_pending_topups():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT t.*, u.username FROM topup_requests t
        JOIN users u ON u.id = t.user_id
        WHERE t.status = 'pending'
        ORDER BY t.id ASC
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_topup(req_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM topup_requests WHERE id = ?", (req_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_topup_status(req_id, status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE topup_requests SET status = ?, updated_at = ? WHERE id = ?",
        (status, now(), req_id),
    )
    conn.commit()
    conn.close()


def get_user_topups(user_id, limit=10):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM topup_requests WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ===== BUYURTMALAR =====

def create_order(user_id, game_code, game_title, package_title, coins_price, game_account_id):
    conn = get_connection()
    cur = conn.cursor()
    n = now()
    cur.execute("""
        INSERT INTO orders (user_id, game_code, game_title, package_title, coins_price, game_account_id, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?)
    """, (user_id, game_code, game_title, package_title, coins_price, game_account_id, n, n))
    conn.commit()
    order_id = cur.lastrowid
    conn.close()
    return order_id


def get_user_orders(user_id, limit=15):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_pending_orders():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT o.*, u.username FROM orders o
        JOIN users u ON u.id = o.user_id
        WHERE o.status = 'pending'
        ORDER BY o.id ASC
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_order_status(order_id, status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE orders SET status = ?, updated_at = ? WHERE id = ?",
        (status, now(), order_id),
    )
    conn.commit()
    conn.close()


def get_order(order_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


# ===== ADMIN =====

def get_admin(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM admin WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


# ===== STATISTIKA (admin panel uchun) =====

def get_stats():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS c FROM users")
    total_users = cur.fetchone()["c"]

    cur.execute("SELECT COALESCE(SUM(amount_uzs), 0) AS s FROM topup_requests WHERE status = 'approved'")
    total_revenue = cur.fetchone()["s"]

    cur.execute("SELECT COUNT(*) AS c FROM orders")
    total_orders = cur.fetchone()["c"]

    cur.execute("SELECT COUNT(*) AS c FROM topup_requests WHERE status = 'pending'")
    pending_topups_count = cur.fetchone()["c"]

    cur.execute("SELECT COUNT(*) AS c FROM orders WHERE status = 'pending'")
    pending_orders_count = cur.fetchone()["c"]

    cur.execute("""
        SELECT game_title, COUNT(*) AS orders_count, COALESCE(SUM(coins_price), 0) AS coins_total
        FROM orders
        GROUP BY game_title
        ORDER BY orders_count DESC
    """)
    per_game = [dict(r) for r in cur.fetchall()]

    conn.close()
    return {
        "total_users": total_users,
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "pending_topups_count": pending_topups_count,
        "pending_orders_count": pending_orders_count,
        "per_game": per_game,
    }
