# Telegram Bot - Kurs Ishi va Maqola Tayyorlash

## Loyiha haqida

Bu Telegram bot (@Dotsent_ai_bot) foydalanuvchilarga AI (OpenAI GPT-4) yordamida professional kurs ishi va ilmiy maqola tayyorlashda yordam beradi. Bot balans tizimi, referal dasturi va promokod imkoniyatlariga ega.

## Oxirgi O'zgarishlar (2025-10-19)

### Bosqichma-bosqich promokod yaratish tizimi ✅
- Admin panel → "🎟 Promokod yaratish" tugmasini bosganda:
  1. **Ish turi so'raladi**: "🧾 Kurs ishi" yoki "📰 Maqola" tugmalari
  2. **Promokod so'zi kiritiladi**: Masalan: YANGI2025, CHEGIRMA50
  3. **Chegirma foizi**: 1 dan 100 gacha raqam
  4. **Foydalanish turi**:
     - 🔄 1 martalik (faqat 1 ta foydalanuvchi)
     - 👥 Har bir foydalanuvchi uchun 1 marta
     - ♾️ Cheksiz foydalanish
- Database yangilandi: `usage_type` va `used_by` ustunlari qo'shildi
- Har bir bosqichda "❌ Bekor qilish" tugmasi mavjud
- Yaratilgandan keyin batafsil ma'lumot ko'rsatiladi

### Promokodlar ro'yxati va boshqarish tizimi ✅
- Admin panel → "📋 Promokodlar ro'yxati" tugmasi
- Barcha yaratilgan promokodlar ro'yxati:
  - Kod nomi, ish turi, chegirma foizi
  - Foydalanish turi va status (Faol/O'chirilgan)
- Har bir promokod uchun "🗑 O'chirish" tugmasi
- O'chirilgan promokod **darhol amal qilmaydi**
- O'chirishdan keyin ro'yxat avtomatik yangilanadi
- Database: `delete_promocode()` funksiyasi qo'shildi

### Xizmat narxi, ma'lumot va balans tekshiruvi tizimi ✅
- "🧾 Kurs ishi yozish" va "📰 Maqola yozish" tugmalari yangilandi
- Tugma bosilganda:
  1. **Xizmat ma'lumoti** ko'rsatiladi (narx, muddat, tafsilotlar)
  2. **"📄 Namunani ko'rish"** tugmasi - **URL tugma, havolaga o'tadi** (ENV: `KURS_ISHI_SAMPLE_URL`, `MAQOLA_SAMPLE_URL`)
  3. **"✅ Roziman"** tugmasi - xizmatni qabul qilish
  4. **"🔙 Orqaga"** tugmasi - bekor qilish
- "Roziman" bosganda:
  - **Balans yetarli** bo'lsa → FSM boshlaydi (F.I.Sh, Mavzu...)
  - **Balans yetarli emas** bo'lsa → balans to'ldirish oynasi:
    - Hozirgi balans va yetmayotgan summa
    - "💵 Balansni to'ldirish" tugmasi
- Balans to'ldirilgandan keyin, foydalanuvchi qayta tugmani bosishi kerak

### Yordam bo'limi va qo'llab-quvvatlash guruhi ✅
- "❓ Yordam" tugmasi yangilandi
- Yordam matnida inline tugma qo'shildi:
  - **"👥 Qo'llab-quvvatlash guruhi"** - URL tugma (ENV: `SUPPORT_GROUP_URL`)
  - Bosganda foydalanuvchi qo'llab-quvvatlash guruhiga yo'naltiriladi
  - **"🔙 Orqaga"** tugmasi - asosiy menyuga qaytish

### PDF konvertatsiya tizimi ✅
- Kurs ishi va maqola tayyor bo'lganda **"📄 Word faylni PDF qilish"** tugmasi ko'rsatiladi
- Fayl haqida batafsil ma'lumot:
  - DOCX formatda - kompyuterda o'zgartirish mumkin
  - Telefonda ochilmasa, PDF qilish kerak
- **PDF konvertatsiya:**
  - LibreOffice CLI orqali DOCX → PDF
  - Tugma bosilganda avtomatik PDF yaratiladi va yuboriladi
  - PDF fayldan keyin o'chiriladi (joy tejash uchun)
- Xatolik bo'lsa, foydalanuvchiga qo'lda PDF qilish ko'rsatmasi beriladi

### Foydalanuvchilarni cheklash tizimi (Ban/Unban) ✅
- Admin panel → **"🚫 Foydalanuvchini cheklash"** va **"✅ Cheklovni olib tashlash"** tugmalari
- **Cheklash jarayoni:**
  1. Admin "🚫 Foydalanuvchini cheklash" tugmasini bosadi
  2. Foydalanuvchi Telegram ID sini kiritadi
  3. Tasdiqlanadi va foydalanuvchi cheklanadi
- **Cheklangan foydalanuvchi:**
  - Botdan **umuman foydalana olmaydi**
  - `/start` bossa: "Sizning botdan foydalanish huquqingiz yo'q" xabari
  - Qo'llab-quvvatlash guruhiga yo'naltirish tugmasi ko'rsatiladi
- **Cheklovni olib tashlash:**
  1. Admin "✅ Cheklovni olib tashlash" tugmasini bosadi
  2. Foydalanuvchi ID sini kiritadi
  3. Cheklov olib tashlanadi, foydalanuvchi qaytadan botdan foydalanishi mumkin
- **Xususiyatlar:**
  - Admin o'zini cheklay olmaydi
  - Allaqachon cheklangan/cheklanmagan foydalanuvchi haqida ogohlantirish
  - Database: `is_blocked` ustuni, `ban_user()`, `unban_user()`, `is_user_banned()` funksiyalari

## O'zgarishlar (2025-10-19)

### 3. Asenkron (Parallel) ishlov berish tizimi ✅
- Bot endi bir paytda bir nechta foydalanuvchiga xizmat ko'rsatadi
- Har bir kurs ishi/maqola yaratish **background task** da ishlaydi
- Foydalanuvchi so'rov yuborgach, darhol javob oladi va boshqa funksiyalardan foydalanishi mumkin
- Tayyor bo'lgach, foydalanuvchiga avtomatik yuboriladi
- Bot hech qachon to'xtamaydi, barcha foydalanuvchilar parallel foydalanishi mumkin
- `asyncio.create_task()` yordamida background ishlov berish
- **MUHIM**: Barcha OpenAI API chaqiruvlari `loop.run_in_executor()` orqali alohida thread'da ishga tushiriladi
- Bu event loop'ni blocking qilmaslik uchun zarur (synchronous OpenAI SDK ishlatilgan)

## Oxirgi O'zgarishlar (2025-10-19)

### YANGI: AI orqali mavzuga asoslangan REJA, MUNDARIJA va ADABIYOTLAR yaratish
- **REJA** endi mavzu va fanga qarab GPT-4o Mini orqali yaratiladi
- Har bir bob va band sarlavhasi mavzuga to'liq mos keladi
- **BOB SARLAVHALARI** REJA dan avtomatik olinadi va DOCX da ishlatiladi
- **BAND SARLAVHALARI** (1.1, 1.2, 2.1...) ham REJA dan olinadi va qalín (bold) formatda yoziladi
- **MUNDARIJA** ham REJA kabi dinamik - AI yaratgan REJA asosida tuziladi
- **ADABIYOTLAR** ro'yxati ham mavzuga asoslangan - AI orqali mavzuga mos 25+ manba yaratiladi
- Dinamik va professional reja tuzilishi
- Agar xatolik bo'lsa, standart reja qaytariladi

## O'zgarishlar (2025-10-19)

### 0. GPT-4o Mini modeliga o'tish
- `gpt-4o` dan `gpt-4o-mini` modeliga o'tildi (eng yangi va samarali mini model)
- **ARZONROQ**: $0.15/1M input tokens, $0.60/1M output tokens
- Tez va samarali
- Katta context window (128K tokens)
- Yuqori sifat va ishonchli natijalar
- Yangi OpenAI API kalit qo'shildi

### 1. FSM (Finite State Machine) orqali to'liq ma'lumot yig'ish
- Kurs ishi yaratishdan oldin quyidagi ma'lumotlar so'raladi:
  - F.I.Sh (to'liq ism)
  - O'quv yurti nomi
  - Fan nomi
  - Kurs ishi mavzusi
  - Kurs raqami (1, 2, 3, 4)

### 2. Professional kurs ishi yaratish (35-40 bet) - GPT-4o Mini bilan
- Har bir bob alohida OpenAI so'rovi orqali yaratiladi (7 ta so'rov):
  - KIRISH (1500+ so'z, 3-4 bet) - 4,000 tokens
  - I BOB - Nazariy asoslar (3000+ so'z, 8-10 bet) - 6,000 tokens
  - II BOB - Amaliy tahlil (3500+ so'z, 10-12 bet) - 7,000 tokens
  - III BOB - Takliflar va yechimlar (3000+ so'z, 8-10 bet) - 6,000 tokens
  - XULOSA (1500+ so'z, 3-4 bet) - 4,000 tokens
  - ADABIYOTLAR (500+ so'z, kamida 25 manba) - 3,000 tokens
  - ILOVALAR (500+ so'z) - 3,000 tokens
- **Jami: 13,000-15,000 so'z (~40-45 bet)**
- **Token sarfi: ~33,000 tokens** (GPT-4o Mini uchun optimallashtirilgan)
- **Narx**: ~$5 per kurs ishi (GPT-4o da $16.50 edi - 3x arzon!)
- Har bir bo'lim uchun batafsil prompt va uzunlik validatsiyasi mavjud
- System prompt: "JUDA BATAFSIL, UZUN va chuqur akademik matn yaratish"
- **Bob sarlavhalari**: KATTA HARFLAR bilan, markazda, qalin (bold)

### 3. Professional DOCX formatlash (O'zbekiston standartlari)
- **1. Titul varaq** (O'quv yurti, talaba ma'lumotlari, fan, mavzu, kurs)
- **2. Reja** (barcha boblar ro'yxati)
- **3. Kirish, 3 Bob, Xulosa**
- **4. Adabiyotlar** (kamida 25 manba)
- **5. Ilovalar** (jadvallar, grafiklar)
- **6. Mundarija** (sahifa raqamlari bilan, oxirida)
- To'g'ri hoshiyalar: Chap 30mm, O'ng 15mm, Yuqori/Pastki 20mm
- Times New Roman 14pt, 1.5 qator oralig'i
- Har bir bob alohida sahifada
- A4 format

## Arxitektura

### Fayl tuzilmasi

```
.
├── main.py                          # Asosiy bot fayli
├── config.py                       # Konfiguratsiya sozlamalari
├── database.py                     # SQLite database handler
├── keyboards.py                    # Telegram klaviaturalar
├── handlers/
│   ├── user_handlers.py            # Foydalanuvchi handlarlari (FSM)
│   └── admin_handlers.py           # Admin handlarlari
├── utils/
│   ├── course_writer.py            # OpenAI orqali kurs ishi yaratish (GPT-4o Mini)
│   └── document_generator.py       # Professional DOCX yaratish
├── generated_files/                # Yaratilgan fayllar
└── .env                            # Environment o'zgaruvchilar
```

### Texnologiyalar

- **Aiogram 3.x**: Telegram Bot API uchun Python framework
- **OpenAI API (GPT-4o Mini)**: Kurs ishi va maqola yaratish
  - Multi-section generation: 7 alohida so'rov (KIRISH, 3 BOB, XULOSA, ADABIYOTLAR, ILOVALAR)
  - Token sarfi: ~33,000 tokens (GPT-4o Mini uchun optimallashtirilgan)
  - Word count validation: 13,000-15,000 so'z (40-45 bet)
  - Har bir bo'lim uchun batafsil prompt va individual max_tokens sozlamalari
  - System prompt: JUDA BATAFSIL va UZUN matn yaratish uchun sozlangan
  - Retry logic: Agar bo'lim qisqa chiqsa, avtomatik qayta yozadi
  - **Arzon**: $0.15/1M input tokens, $0.60/1M output tokens
  - **Narx per kurs ishi**: ~$5 (GPT-4o da $16.50 edi)
- **SQLite**: Ma'lumotlar bazasi
- **python-docx**: Professional DOCX fayllarni yaratish
  - Custom margins, fonts, spacing
  - Structured sections (title page, TOC, chapters)
- **docx2pdf**: PDF konvertatsiyasi (kelajakda)

### Ma'lumotlar bazasi

SQLite database 5 ta jadvaldan iborat:
- `users`: Foydalanuvchi ma'lumotlari, balans, referal
- `orders`: Kurs ishlari va maqolalar tarixi
- `payments`: To'lovlar va statuslari
- `promocodes`: Promokod va chegirmalar
- `settings`: Tizim sozlamalari

## Asosiy xususiyatlar

### Foydalanuvchi imkoniyatlari

1. **Kurs ishi yaratish**: AI orqali mavzu bo'yicha to'liq kurs ishi
2. **Maqola yaratish**: Ilmiy maqola tayyorlash
3. **Balans tizimi**: To'lov cheki yuborish orqali balansni to'ldirish
4. **Referal tizimi**: Do'stlarni taklif qilish orqali bonus
5. **Promokod**: Chegirmalardan foydalanish

### Admin panel

1. **Ommaviy xabar**: Barcha foydalanuvchilarga xabar
2. **Balans boshqarish**: Foydalanuvchi balansini o'zgartirish
3. **Statistika**: Foydalanuvchilar va buyurtmalar statistikasi
4. **Sozlamalar**: Narxlar, referal bonus, promokodlar
5. **To'lov tasdiqlash**: Chekni tasdiqlash/rad etish

## Sozlash

### Kerakli environment o'zgaruvchilar

```
BOT_TOKEN - Telegram bot tokeni (@BotFather dan)
OPENAI_API_KEY - OpenAI API kaliti
ADMIN_ID - Admin foydalanuvchi ID si
KURS_ISHLARI_CHANNEL_ID - Kurs ishlari kanali ID si
MAQOLALAR_CHANNEL_ID - Maqolalar kanali ID si
TOLOV_TASDIQLASH_CHANNEL_ID - To'lov tasdiqlash kanali ID si
```

## Maqola yaratish funksiyasi (2025-10-19)

### Yangi xususiyat: Ilmiy maqola yaratish

Bot endi professional ilmiy maqola ham yarata oladi!

**FSM (Ketma-ket so'rovlar):**
1. 📝 Maqola mavzusi
2. 👤 Muallif ism va familiyasi
3. 📚 Soha va lavozim (masalan: Matematika, Katta o'qituvchi)
4. 👨‍🏫 Ustoz ism va familiyasi (⏭ O'tkazib yuborish tugmasi bilan)

**Format:**
- A4 sahifa, 20mm margin (barcha tomondan)
- Times New Roman 14pt
- 1.5 qator oralig'i
- 1.25 sm xat boshi
- 7-10 sahifa

**Tarkib:**
1. **1-sahifa**: Sarlavha (qalin, markazda) va mualliflar ma'lumoti:
   - Muallif ism familiyasi
   - Soha va lavozim
   - Ustoz ism familiyasi (agar kiritilgan bo'lsa, "Ilmiy rahbar" deb)
2. **Annotatsiya** (3 tilda: O'zbek, Ingliz, Rus) - har biri 40-50 so'z
3. **Kalit so'zlar** (5-8 ta, har bir tilda, qalin)
4. **KIRISH** (qalin sarlavha, uzluksiz matn)
5. **TADQIQOT USLUBLARI** (qalin sarlavha, uzluksiz matn)
6. **NATIJALAR VA MUHOKAMA** (qalin sarlavha, uzluksiz matn)
7. **XULOSA** (qalin sarlavha, uzluksiz matn)
8. **FOYDALANILGAN ADABIYOTLAR** (APA format, 15-20 manba)

**AI generation:**
- Har bir bo'lim alohida GPT-4o Mini orqali yaratiladi
- Professional ilmiy uslub
- Mavzuga mos annotatsiyalar (3 tilda, 40-50 so'z)
- Matnlar uzluksiz, bitta oqimda (enter qo'yilmaydi)
- Barcha bo'lim sarlavhalari qalin (bold)
- APA formatda adabiyotlar (15-20 ta manba)

**Fayllar:**
- `utils/article_writer.py` - Maqola kontenti yaratish
- `utils/article_document_generator.py` - DOCX formatlash
- Har bir bo'lim yangi sahifadan boshlanadi

## Keyingi qadamlar

- [x] FSM orqali to'liq ma'lumot yig'ish (F.I.Sh, O'quv yurti, Fan, Kurs)
- [x] Multi-section OpenAI generation (7 bo'lim, 16,000-17,000 so'z)
- [x] Token optimizatsiyasi (26,000 tokens - quota xatoligini bartaraf qilish)
- [x] Professional DOCX formatlash (titul, reja, mundarija, ilovalar)
- [x] O'zbekiston standartlariga moslashtirilgan format
- [x] Ilmiy maqola yaratish (3 tilda annotatsiya, APA format)
- [x] Asenkron (parallel) ishlov berish - bir paytda ko'p foydalanuvchi
- [x] Non-blocking OpenAI API chaqiruvlari (run_in_executor)
- [x] Xat boshi (1.25 sm) - O'zbekiston standartlari
- [x] Statistikada blok qilgan foydalanuvchilar soni
- [x] Ommaviy xabar yuborishda blok qilganlar hisobi
- [x] Namuna fayllarni ko'rish (URL tugmalar)
- [x] Qo'llab-quvvatlash guruhi (URL tugma)
- [x] PDF export funksiyasi (LibreOffice CLI)
- [x] Annotatsiyalardan keyin bo'sh sahifa muammosi hal qilindi
- [ ] "Yana yozish" va "Asosiy menyu" tugmalari
- [ ] Telegram Payment API integratsiyasi (Click, Payme)
- [ ] Ko'p tillilik (🇺🇿 O'zbek, 🇷🇺 Rus)
- [ ] Avtomatik backup tizimi
- [ ] Ko'proq AI modellari (GPT-4o, Claude, o1)
- [ ] Foydalanuvchi fikr-mulohazalari tizimi
- [ ] Plagiarism checker integratsiyasi

## Muallif

Yaratilgan Replit Agent yordamida.
