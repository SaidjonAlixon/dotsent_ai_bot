import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
KURS_ISHLARI_CHANNEL_ID = os.getenv("KURS_ISHLARI_CHANNEL_ID", "")
MAQOLALAR_CHANNEL_ID = os.getenv("MAQOLALAR_CHANNEL_ID", "")
TOLOV_TASDIQLASH_CHANNEL_ID = os.getenv("TOLOV_TASDIQLASH_CHANNEL_ID", "")

DEFAULT_KURS_ISH_PRICE = 25000
DEFAULT_MAQOLA_PRICE = 20000
DEFAULT_REFERAL_BONUS = 5000

KURS_ISH_PROMPT = """Siz professional akademik yozuvchi sifatida ishlaysiz. 
Quyidagi mavzu bo'yicha to'liq, professional kurs ishi tayyorlang:

Mavzu: {topic}

Kurs ishi quyidagi talablarga javob berishi kerak:
1. Kirish qismi (mavzuning dolzarbligi, maqsadi va vazifalari)
2. Asosiy qism (nazariy va amaliy material, 3-4 bob)
3. Xulosa (olingan natijalar va xulosalar)
4. Foydalanilgan adabiyotlar ro'yxati

Kurs ishi kamida 15-20 bet hajmda bo'lishi kerak.
Professional, ilmiy uslubda yozing."""

MAQOLA_PROMPT = """Siz professional maqola muallifi sifatida ishlaysiz.
Quyidagi mavzu bo'yicha ilmiy maqola tayyorlang:

Mavzu: {topic}

Maqola quyidagi tuzilmaga ega bo'lishi kerak:
1. Annotatsiya (150-200 so'z)
2. Kalit so'zlar
3. Kirish
4. Tadqiqot metodologiyasi
5. Asosiy qism (natijalar va muhokama)
6. Xulosa
7. Adabiyotlar

Maqola ilmiy uslubda, professional tilda yozilishi kerak."""
