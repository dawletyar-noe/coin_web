# GameTop — to'liq sayt (hisob, coin, admin panel)

Bu — Telegram'dan mustaqil, to'liq mustaqil **veb-sayt**. Nima ishlaydi:

- Foydalanuvchi ro'yxatdan o'tadi / kiradi
- Hisobini "coin" bilan to'ldiradi (pul o'tkazgach, siz admin panelda tasdiqlaysiz)
- Coinlar bilan o'yinlarga donat sotib oladi
- Siz (admin) alohida `/admin` sahifasida login/parol bilan kirasiz va: jami tushum, foydalanuvchilar soni, har bir o'yin bo'yicha buyurtmalar sonini ko'rasiz, to'ldirish so'rovlarini tasdiqlaysiz/rad etasiz, buyurtmalarni bajarilgan deb belgilaysiz

## Bu sizga qanday tayyor bo'ldi

Barcha fayllar test qilindi (ro'yxatdan o'tish → to'ldirish → tasdiqlash → sotib olish → admin ko'rinishi) — hammasi ishlaydi.

## 1-qadam: kompyuteringizda sinab ko'rish (ixtiyoriy, lekin tavsiya etiladi)

Barcha fayllarni bitta papkaga (masalan `website`) joylashtiring — `templates` va `static`
papkalarini ham o'z ichiga olgan holda, xuddi qanday tuzilgan bo'lsa shunday.

Terminalda:
```
cd website
pip install -r requirements.txt
python app.py
```
Brauzerda oching: `http://localhost:5000`

## 2-qadam: internetga chiqarish (Render.com, bepul)

Bu safar GitHub Pages ishlamaydi (u faqat statik saytlar uchun), chunki bu
saytda **server** (Flask) va **ma'lumotlar bazasi** bor. Shuning uchun
Render.com dan foydalanamiz — bepul, va Python loyihalarini to'g'ridan-to'g'ri
GitHub orqali joylashtirish imkonini beradi.

### 2.1. GitHub'ga yuklang
- Yangi repository yarating (masalan `game-donate-site`)
- Barcha fayllarni (papkalar bilan birga: `templates/`, `static/`, `app.py`,
  `config.py`, `models.py`, `requirements.txt`, `Procfile`) yuklang
  ("Add file" → "Upload files" — bir nechta faylni birga tashlash mumkin,
  papkalarni ham saqlagan holda)

### 2.2. Render.com'da akkaunt oching
[render.com](https://render.com) saytiga kiring, GitHub akkauntingiz orqali
ro'yxatdan o'ting (eng oson yo'l).

### 2.3. Yangi Web Service yarating
- Dashboard'da **"New +"** → **"Web Service"**
- GitHub repository'ingizni tanlang (`game-donate-site`)
- Sozlamalar:
  - **Name:** istalgan nom
  - **Runtime:** Python 3
  - **Build Command:** `pip install -r requirements.txt`
  - **Start Command:** `gunicorn app:app`
  - **Instance Type:** Free

### 2.4. Muhim: maxfiy sozlamalarni kiriting
"Environment Variables" bo'limida quyidagilarni qo'shing (bu — parolingizni
kodning ichida ochiq saqlamaslik uchun):

| Key | Value |
|---|---|
| `ADMIN_USERNAME` | o'zingiz xohlagan admin login |
| `ADMIN_PASSWORD` | kuchli parol o'ylab toping |
| `SECRET_KEY` | tasodifiy uzun matn (masalan 30 ta random harf-raqam) |
| `PAYMENT_CARD_NUMBER` | to'lov qabul qiladigan karta raqamingiz |
| `PAYMENT_CARD_OWNER` | karta egasining F.I.Sh. |

### 2.5. Deploy qiling
**"Create Web Service"** tugmasini bosing. Bir necha daqiqadan so'ng sizga
`https://sizning-nomingiz.onrender.com` shaklida manzil beriladi — bu sizning
saytingiz!

## 3-qadam: sinab ko'ring

1. Saytga kiring, ro'yxatdan o'ting
2. "Hisobni to'ldirish" orqali so'rov yuboring
3. `https://sizning-manzil.onrender.com/admin` sahifasiga o'ting, admin login/parol bilan kiring
4. So'rovni "Tasdiqlash" bosing — coinlar hisobingizga tushishi kerak
5. Bosh sahifaga qaytib, biror o'yin uchun donat sotib ko'ring

## Muhim eslatmalar

- **Bepul Render rejasi** ma'lum vaqt faoliyatsiz qolsa "uxlab qoladi" va
  birinchi so'rovda 30-50 soniya sekinroq ochiladi — bu normal, pullik rejaga
  o'tsangiz yo'qoladi.
- **Ma'lumotlar bazasi** (`site.db`) — Render'ning bepul rejasida har safar
  qayta deploy qilinganda tozalanishi mumkin. Uzoq muddatli saqlash uchun
  keyinchalik "Render Disk" yoki tashqi bazaga (masalan PostgreSQL) o'tish
  kerak bo'ladi — hozircha sinov va boshlang'ich foydalanish uchun yetarli.
- **To'lov hozircha qo'lda tasdiqlanadi** (siz kartaga tushgan pulni ko'rib,
  admin panelda "Tasdiqlash" bosasiz). Kelajakda Payme/Click API bilan
  avtomatlashtirish mumkin.
- Ranglar/matnni o'zgartirish uchun `static/style.css` va `templates/`
  ichidagi fayllarni tahrirlang.
