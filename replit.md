# Telegram Bot - Kurs Ishi va Maqola Tayyorlash

## Loyiha haqida

Bu Telegram bot foydalanuvchilarga AI (OpenAI GPT-4) yordamida kurs ishi va ilmiy maqola tayyorlashda yordam beradi. Bot balans tizimi, referal dasturi va promokod imkoniyatlariga ega.

## Arxitektura

### Fayl tuzilmasi

```
.
├── main.py                 # Asosiy bot fayli
├── config.py              # Konfiguratsiya sozlamalari
├── database.py            # SQLite database handler
├── keyboards.py           # Telegram klaviaturalar
├── handlers/
│   ├── user_handlers.py   # Foydalanuvchi handlarlari
│   └── admin_handlers.py  # Admin handlarlari
├── utils/
│   ├── openai_handler.py  # OpenAI integratsiyasi
│   └── docx_creator.py    # DOCX yaratish
└── .env                   # Environment o'zgaruvchilar
```

### Texnologiyalar

- **Aiogram 3.x**: Telegram Bot API uchun Python framework
- **OpenAI API**: Kurs ishi va maqola yaratish
- **SQLite**: Ma'lumotlar bazasi
- **python-docx**: DOCX fayllarni yaratish

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

- [ ] Telegram Payment API integratsiyasi (Click, Payme)
- [ ] Avtomatik backup tizimi
- [ ] Ko'proq AI modellari (GPT-4o, Claude)
- [ ] Foydalanuvchi fikr-mulohazalari tizimi
- [ ] Statistika va hisobotlar eksporti

## Muallif

Yaratilgan Replit Agent yordamida.
