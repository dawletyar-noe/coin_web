from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

import config
import models as db

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

db.init_db()


# ===== YORDAMCHI FUNKSIYALAR =====

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return wrapper


def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return db.get_user_by_id(uid)


@app.context_processor
def inject_globals():
    return {
        "current_user": current_user(),
        "GAMES": config.GAMES,
        "COIN_RATE": config.COIN_RATE,
        "PAYMENT_CARD_NUMBER": config.PAYMENT_CARD_NUMBER,
        "PAYMENT_CARD_OWNER": config.PAYMENT_CARD_OWNER,
    }


# ===== ASOSIY DO'KON =====

@app.route("/")
def store():
    return render_template("store.html")


# ===== RO'YXATDAN O'TISH / KIRISH =====

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if len(username) < 3 or len(password) < 4:
            flash("Login kamida 3, parol kamida 4 belgidan iborat bo'lishi kerak.", "error")
            return render_template("register.html")

        if db.get_user_by_username(username):
            flash("Bu login band. Boshqasini tanlang.", "error")
            return render_template("register.html")

        user_id = db.create_user(username, generate_password_hash(password))
        session["user_id"] = user_id
        flash("Xush kelibsiz! Ro'yxatdan muvaffaqiyatli o'tdingiz.", "success")
        return redirect(url_for("store"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = db.get_user_by_username(username)

        if not user or not check_password_hash(user["password_hash"], password):
            flash("Login yoki parol noto'g'ri.", "error")
            return render_template("login.html")

        session["user_id"] = user["id"]
        return redirect(url_for("store"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("store"))


# ===== HISOBNI TO'LDIRISH =====

@app.route("/wallet", methods=["GET", "POST"])
@login_required
def wallet():
    user = current_user()

    if request.method == "POST":
        try:
            amount = int(request.form.get("amount", "0"))
        except ValueError:
            amount = 0

        if amount < 1000:
            flash("Minimal to'ldirish miqdori 1 000 so'm.", "error")
            return redirect(url_for("wallet"))

        coins = amount // config.COIN_RATE
        db.create_topup_request(user["id"], amount, coins)
        flash("So'rovingiz qabul qilindi! Admin tasdiqlagach, coinlar hisobingizga tushadi.", "success")
        return redirect(url_for("wallet"))

    topups = db.get_user_topups(user["id"])
    return render_template("wallet.html", topups=topups)


# ===== DONAT SOTIB OLISH =====

@app.route("/buy/<game_code>/<package_code>", methods=["POST"])
@login_required
def buy(game_code, package_code):
    user = current_user()
    game = config.GAMES.get(game_code)
    if not game:
        flash("O'yin topilmadi.", "error")
        return redirect(url_for("store"))

    package = next((p for p in game["packages"] if p["code"] == package_code), None)
    if not package:
        flash("Paket topilmadi.", "error")
        return redirect(url_for("store"))

    account_id = request.form.get("account_id", "").strip()
    if len(account_id) < 3:
        flash("Iltimos, to'g'ri ID kiriting.", "error")
        return redirect(url_for("store"))

    coins_price = package["price"] // config.COIN_RATE
    fresh_user = db.get_user_by_id(user["id"])
    if fresh_user["coins"] < coins_price:
        flash("Hisobingizda coin yetarli emas. Avval hisobni to'ldiring.", "error")
        return redirect(url_for("wallet"))

    db.deduct_coins(user["id"], coins_price)
    order_id = db.create_order(
        user_id=user["id"],
        game_code=game_code,
        game_title=game["title"],
        package_title=package["title"],
        coins_price=coins_price,
        game_account_id=account_id,
    )
    flash(f"✅ Buyurtma #{order_id} qabul qilindi! Tez orada bajariladi.", "success")
    return redirect(url_for("orders"))


@app.route("/orders")
@login_required
def orders():
    user = current_user()
    user_orders = db.get_user_orders(user["id"])
    return render_template("orders.html", orders=user_orders)


# ===== ADMIN =====

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        admin = db.get_admin(username)

        if not admin or not check_password_hash(admin["password_hash"], password):
            flash("Login yoki parol noto'g'ri.", "error")
            return render_template("admin_login.html")

        session["is_admin"] = True
        session["admin_username"] = username
        return redirect(url_for("admin_dashboard"))

    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    session.pop("admin_username", None)
    return redirect(url_for("admin_login"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    stats = db.get_stats()
    pending_topups = db.get_pending_topups()
    pending_orders = db.get_pending_orders()
    return render_template(
        "admin_dashboard.html",
        stats=stats,
        pending_topups=pending_topups,
        pending_orders=pending_orders,
    )


@app.route("/admin/topup/<int:req_id>/<action>")
@admin_required
def admin_topup_action(req_id, action):
    req = db.get_topup(req_id)
    if not req or req["status"] != "pending":
        return redirect(url_for("admin_dashboard"))

    if action == "approve":
        db.add_coins(req["user_id"], req["coins"])
        db.update_topup_status(req_id, "approved")
    elif action == "reject":
        db.update_topup_status(req_id, "rejected")

    return redirect(url_for("admin_dashboard"))


@app.route("/admin/order/<int:order_id>/<action>")
@admin_required
def admin_order_action(order_id, action):
    order = db.get_order(order_id)
    if not order or order["status"] != "pending":
        return redirect(url_for("admin_dashboard"))

    if action == "complete":
        db.update_order_status(order_id, "completed")
    elif action == "cancel":
        db.update_order_status(order_id, "cancelled")
        db.add_coins(order["user_id"], order["coins_price"])  # coinlarni qaytarish

    return redirect(url_for("admin_dashboard"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
