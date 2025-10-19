# Telegram Bot - Kurs Ishi va Maqola Tayyorlash

## Loyiha haqida

Bu Telegram bot (@Dotsent_ai_bot) foydalanuvchilarga AI (OpenAI GPT-4) yordamida professional kurs ishi va ilmiy maqola tayyorlashda yordam beradi. Bot balans tizimi, referal dasturi va promokod imkoniyatlariga ega.

## Oxirgi O'zgarishlar (2025-10-19)

### 0. GPT-4o modeliga o'tish
- `gpt-4` dan `gpt-4o` modeliga o'tildi (eng yangi va kuchli model)
- Tezroq, arzonroq va aqlliroq
- Katta context window (128K tokens)
- Multimodal imkoniyatlari (matn, rasm, audio)
- Yangi OpenAI API kalit qo'shildi

### 1. FSM (Finite State Machine) orqali to'liq ma'lumot yig'ish
- Kurs ishi yaratishdan oldin quyidagi ma'lumotlar so'raladi:
  - F.I.Sh (to'liq ism)
  - O'quv yurti nomi
  - Fan nomi
  - Kurs ishi mavzusi
  - Kurs raqami (1, 2, 3, 4)

### 2. Professional kurs ishi yaratish (35-40 bet)
- Har bir bob alohida OpenAI so'rovi orqali yaratiladi (7 ta so'rov):
  - KIRISH (1200+ so'z, 3-4 bet) - 3,000 tokens
  - I BOB - Nazariy asoslar (2500+ so'z, 8-10 bet) - 5,000 tokens
  - II BOB - Amaliy tahlil (3000+ so'z, 10-12 bet) - 6,000 tokens
  - III BOB - Takliflar va yechimlar (2500+ so'z, 8-10 bet) - 5,000 tokens
  - XULOSA (1200+ so'z, 3-4 bet) - 3,000 tokens
  - ADABIYOTLAR (400+ so'z, kamida 25 manba) - 2,000 tokens
  - ILOVALAR (300+ so'z) - 2,000 tokens
- **Jami: 11,000-14,000 so'z (~35-40 bet)**
- **Token sarfi: ~26,000 tokens** (quota xatoligini oldini olish uchun optimallashtirilgan)
- Har bir bo'lim uchun uzunlik validatsiyasi mavjud

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
│   ├── openai_handler.py           # OpenAI integratsiyasi (multi-section)
│   ├── docx_creator.py             # Oddiy DOCX yaratish
│   └── docx_creator_professional.py # Professional kurs ishi DOCX
├── generated_files/                # Yaratilgan fayllar
└── .env                            # Environment o'zgaruvchilar
```

### Texnologiyalar

- **Aiogram 3.x**: Telegram Bot API uchun Python framework
- **OpenAI API (GPT-4)**: Kurs ishi va maqola yaratish
  - Multi-section generation: 7 alohida so'rov (KIRISH, 3 BOB, XULOSA, ADABIYOTLAR, ILOVALAR)
  - Token sarfi optimizatsiyasi: ~26,000 tokens (quota xatoligini oldini olish)
  - Word count validation: 11,000-14,000 so'z (35-40 bet)
  - Har bir bo'lim uchun individual max_tokens sozlamalari
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

## Keyingi qadamlar

- [x] FSM orqali to'liq ma'lumot yig'ish (F.I.Sh, O'quv yurti, Fan, Kurs)
- [x] Multi-section OpenAI generation (7 bo'lim, 11,000-14,000 so'z)
- [x] Token optimizatsiyasi (26,000 tokens - quota xatoligini bartaraf qilish)
- [x] Professional DOCX formatlash (titul, reja, mundarija, ilovalar)
- [x] O'zbekiston standartlariga moslashtirilgan format
- [ ] "Yana yozish" va "Asosiy menyu" tugmalari
- [ ] "Namuna ishni ko'rish" funksiyasi
- [ ] PDF export funksiyasi (docx2pdf)
- [ ] Telegram Payment API integratsiyasi (Click, Payme)
- [ ] Ko'p tillilik (🇺🇿 O'zbek, 🇷🇺 Rus)
- [ ] Avtomatik backup tizimi
- [ ] Ko'proq AI modellari (GPT-4o, Claude, o1)
- [ ] Foydalanuvchi fikr-mulohazalari tizimi
- [ ] Plagiarism checker integratsiyasi

## Muallif

Yaratilgan Replit Agent yordamida.
