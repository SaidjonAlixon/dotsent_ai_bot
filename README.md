# Telegram Bot - Kurs Ishi va Maqola Tayyorlash

Bu bot foydalanuvchilarga AI yordamida kurs ishi va maqola tayyorlashda yordam beradi.

## Asosiy imkoniyatlar

### Foydalanuvchi uchun:
- 🧾 Kurs ishi yozish (AI orqali avtomatik yaratiladi)
- 📰 Maqola yozish (ilmiy maqola tayyorlash)
- 💰 Balans tizimi (to'lov va chegirmalar)
- 💵 Referal tizimi (do'stlarni taklif qilish orqali pul ishlash)
- 🎁 Promokod tizimi (chegirmalar)
- 👤 Profil (shaxsiy ma'lumotlar)

### Admin uchun:
- 📢 Ommaviy xabar yuborish
- 💬 ID orqali xabar yuborish
- 💳 Balans boshqarish
- 📊 Statistika
- 🤝 Referal sozlamalari
- 💸 Narxlarni boshqarish
- 🎟 Promokod yaratish
- ✅ To'lovlarni tasdiqlash

## O'rnatish va sozlash

### 1. Environment o'zgaruvchilarni sozlash

`.env` fayl yarating va quyidagi ma'lumotlarni kiriting:

```env
BOT_TOKEN=sizning_bot_tokeningiz
OPENAI_API_KEY=sizning_openai_api_keyingiz
ADMIN_ID=sizning_telegram_id_ingiz
KURS_ISHLARI_CHANNEL_ID=-100xxxxxxxxx
MAQOLALAR_CHANNEL_ID=-100xxxxxxxxx
TOLOV_TASDIQLASH_CHANNEL_ID=-100xxxxxxxxx
```

### 2. Kanallarni yaratish

1. **Kurs ishlari kanali** - tayyor kurs ishlari bu yerga yuboriladi
2. **Maqolalar kanali** - tayyor maqolalar bu yerga yuboriladi
3. **To'lov tasdiqlash kanali** - to'lov cheklari bu yerga yuboriladi

Har bir kanalga botni admin qilib qo'shing.

### 3. Kanal ID larini olish

Kanalga biror xabar yuboring, keyin quyidagi URLga kiring:
```
https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
```

Natijada kanal ID sini ko'rasiz (masalan: -1001234567890)

### 4. Admin ID ni olish

[@userinfobot](https://t.me/userinfobot) botiga `/start` yuboring va o'z ID ingizni oling.

### 5. Botni ishga tushirish

Botni ishga tushirish uchun quyidagi buyruqni bajaring:

```bash
python main.py
```

## Ma'lumotlar bazasi

Bot SQLite dan foydalanadi. Quyidagi jadvallar yaratiladi:

- `users` - foydalanuvchilar
- `orders` - buyurtmalar (kurs ishlari va maqolalar)
- `payments` - to'lovlar
- `promocodes` - promokodlar
- `settings` - sozlamalar

## Xususiyatlar

### AI integratsiyasi

Bot OpenAI GPT-4 modelidan foydalanib professional kurs ishlari va maqolalar yaratadi.

### DOCX formati

Barcha ishlar DOCX formatda tayyorlanadi va quyidagi formatga ega:
- Shrift: Times New Roman
- Hajmi: 14pt
- Interval: 1.5

### To'lov tizimi

Admin tomonidan qo'lda tasdiqlash orqali ishlaydi. Foydalanuvchi to'lov chekini yuboradi, admin tasdiqlaydi va balans avtomatik yangilanadi.

### Referal tizimi

Har bir foydalanuvchi o'zining referal havolasiga ega. Do'stlarni taklif qilganda bonus oladi.

## Texnik ma'lumotlar

- **Til**: Python 3.11
- **Framework**: Aiogram 3.x
- **AI**: OpenAI GPT-4
- **Database**: SQLite
- **Fayl formati**: DOCX (python-docx)

## Yordam

Muammolar yoki savollar bo'lsa, admin bilan bog'laning.
