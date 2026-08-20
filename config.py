import os

# === XAVFSIZLIK ===
SECRET_KEY = os.getenv("SECRET_KEY", "iltimos-buni-oz-maxfiy-kalitingizga-almashtiring")

# === ADMIN KIRISH MA'LUMOTLARI ===
# Diqqat: bularni albatta o'zgartiring! Parolni oddiy matn sifatida saqlamaslik
# uchun tizim uni ishga tushganda avtomatik "хеш" qiladi (models.py da).
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "danat2026admin")  # <-- BUNI O'ZGARTIRING!

DB_PATH = os.getenv("DB_PATH", "site.db")

# === COIN KURSI ===
# 1 coin = necha so'm. Foydalanuvchi pul to'ldirganda shu kurs bo'yicha
# coin hisoblanadi (masalan 50 000 so'm = 500 coin, agar kurs 100 bo'lsa).
COIN_RATE = int(os.getenv("COIN_RATE", "100"))

# === TO'LOV UCHUN KARTA MA'LUMOTI (hisobni to'ldirish sahifasida ko'rsatiladi) ===
PAYMENT_CARD_NUMBER = os.getenv("PAYMENT_CARD_NUMBER", "8600 xxxx xxxx xxxx")
PAYMENT_CARD_OWNER = os.getenv("PAYMENT_CARD_OWNER", "F.I.Sh.")

# === O'YINLAR VA PAKETLAR KATALOGI (narxlar so'mda, sahifada coin'ga aylantiriladi) ===
GAMES = {
    "freefire": {
        "title": "Free Fire", "icon": "🔥", "id_label": "Player ID",
        "packages": [
            {"code": "ff_100", "title": "100 Olmos", "price": 15000},
            {"code": "ff_310", "title": "310 Olmos", "price": 45000},
            {"code": "ff_520", "title": "520 Olmos", "price": 75000},
            {"code": "ff_1080", "title": "1080 Olmos", "price": 150000},
        ],
    },
    "pubg": {
        "title": "PUBG Mobile", "icon": "🎯", "id_label": "Character ID",
        "packages": [
            {"code": "pubg_60", "title": "60 UC", "price": 18000},
            {"code": "pubg_325", "title": "325 UC", "price": 90000},
            {"code": "pubg_660", "title": "660 UC", "price": 175000},
            {"code": "pubg_1800", "title": "1800 UC", "price": 450000},
        ],
    },
    "coc": {
        "title": "Clash of Clans", "icon": "🏰", "id_label": "Player Tag (#...)",
        "packages": [
            {"code": "coc_500", "title": "500 Gems", "price": 30000},
            {"code": "coc_1200", "title": "1200 Gems", "price": 65000},
            {"code": "coc_2500", "title": "2500 Gems", "price": 130000},
        ],
    },
    "standoff2": {
        "title": "Standoff 2", "icon": "🔫", "id_label": "Player ID",
        "packages": [
            {"code": "so2_100", "title": "100 Gold", "price": 12000},
            {"code": "so2_500", "title": "500 Gold", "price": 55000},
            {"code": "so2_1000", "title": "1000 Gold", "price": 105000},
        ],
    },
    "mlbb": {
        "title": "Mobile Legends", "icon": "⚔️", "id_label": "User ID (Zone bilan)",
        "packages": [
            {"code": "mlbb_86", "title": "86 Olmos", "price": 20000},
            {"code": "mlbb_172", "title": "172 Olmos", "price": 38000},
            {"code": "mlbb_257", "title": "257 Olmos", "price": 55000},
            {"code": "mlbb_706", "title": "706 Olmos", "price": 140000},
        ],
    },
}
