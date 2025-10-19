# Railway.app ga Deploy qilish qo'llanmasi

## 📋 Talab qilinadigan fayllar

Loyihada quyidagi fayllar mavjud:
- ✅ `main.py` - Botning asosiy fayli
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Railway uchun start command
- ✅ `.python-version` - Python versiyasi (3.11)
- ✅ `runtime.txt` - Python runtime
- ✅ `.gitignore` - Git ignore fayli

---

## 🚀 Railway ga deploy qilish

### 1-qadam: GitHub ga upload qilish

```bash
# Git repository yaratish
git init
git add .
git commit -m "Initial commit - Telegram Bot"
git branch -M main

# GitHub repository yaratib, unga push qilish
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2-qadam: Railway.app ga kirish

1. [Railway.app](https://railway.app) ga boring
2. **Sign up** yoki **Login** qiling (GitHub orqali)
3. **New Project** tugmasini bosing
4. **Deploy from GitHub repo** ni tanlang
5. Repository'ingizni tanlang

### 3-qadam: Environment Variables qo'shish

Railway dashboard → **Variables** → **+ New Variable**

Quyidagi barcha secret'larni qo'shing:

```bash
BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=your_openai_key_here
ADMIN_ID=your_telegram_id
KURS_ISHLARI_CHANNEL_ID=your_channel_id
MAQOLALAR_CHANNEL_ID=your_channel_id
TOLOV_TASDIQLASH_CHANNEL_ID=your_channel_id
KURS_ISHI_SAMPLE_URL=https://t.me/your_channel/123
MAQOLA_SAMPLE_URL=https://t.me/your_channel/456
SUPPORT_GROUP_URL=https://t.me/your_support_group
```

**Muhim:**
- Har bir qiymatni to'g'ri kiriting
- Channel ID'lar `-100` bilan boshlanishi kerak
- URL'lar to'liq havola bo'lishi kerak

### 4-qadam: Deploy qilish

1. Railway avtomatik deploy boshlaydi
2. **Deployments** tab'da build loglarini ko'ring
3. ✅ "Build successful" ko'rsatilsa - tayyor!

### 5-qadam: Botni tekshirish

1. Telegram'da botingizga boring
2. `/start` buyrug'ini yuboring
3. Barcha tugmalar ishlayotganini tekshiring

---

## 📊 Railway Monitoring

### Loglarni ko'rish:
Railway Dashboard → Your Project → **Deployments** → **View Logs**

### Bot qayta ishga tushirish:
Railway Dashboard → Your Project → **Settings** → **Restart**

### Bot to'xtatish:
Railway Dashboard → Your Project → **Settings** → **Delete Service**

---

## 💰 Narxlar (2024)

- **Hobby Plan**: $5/oyiga
  - Har oy $5 bepul kredit beriladi
  - Kichik botlar uchun yetarli
  - Cheksiz runtime
- To'lov kartasini qo'shish yoki $5 oldindan to'lash kerak

---

## 🔧 Muammolarni hal qilish

### Bot ishlamayapti?
1. Railway loglarini tekshiring
2. Environment variables to'g'ri kiritilganini tekshiring
3. Bot token hali ham faol ekanini tekshiring (@BotFather)

### Database xatoligi?
Railway `bot_database.db` ni avtomatik yaratadi, lekin...
- Agar PostgreSQL kerak bo'lsa: Railway → **+ New** → **Database** → **PostgreSQL**

### Fayl tizimi xatoligi?
Railway'da har bir deploy yangi container yaratadi, shuning uchun:
- ✅ Fayllar yuborilgandan keyin **avtomatik o'chiriladi** (kod ichida)
- ✅ SQLite database saqlanadi (Railway volume'da)

### Out of memory?
- Railway default: 512MB RAM
- Settings → **Resources** → ko'proq RAM ajratish (pullik)

---

## ✅ Deploy checklist

- [ ] GitHub'ga push qilindi
- [ ] Railway project yaratildi
- [ ] Barcha environment variables qo'shildi
- [ ] Deploy muvaffaqiyatli bo'ldi
- [ ] Bot Telegram'da ishlayapti
- [ ] Kurs ishi va maqola yaratish test qilindi
- [ ] PDF konvertatsiya ishlayapti
- [ ] Admin panel ishlayapti

---

## 🔗 Foydali havolalar

- **Railway Dashboard**: https://railway.app/dashboard
- **Railway Docs**: https://docs.railway.app
- **Telegram Bot API**: https://core.telegram.org/bots/api
- **OpenAI API**: https://platform.openai.com

---

## 🎉 Tayyor!

Botingiz endi Railway'da 24/7 ishlaydi!

Har qanday savol bo'lsa, qo'llab-quvvatlash guruhiga murojaat qiling.
