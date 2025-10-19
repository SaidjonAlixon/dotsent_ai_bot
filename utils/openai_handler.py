import openai
import logging
from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

openai.api_key = OPENAI_API_KEY

KURS_ISH_FULL_PROMPT = """Siz professional akademik yozuvchi sifatida ishlaysiz.

Quyidagi ma'lumotlar asosida TO'LIQ KURS ISHI tayyorlang:

Talaba: {fish}
O'quv yurti: {university}
Fan: {subject}
Mavzu: {topic}
Kurs: {course_number}

KURS ISHI QUYIDAGI TUZILMAGA EGA BO'LISHI KERAK (35-40 bet):

KIRISH (3-4 bet):
- Mavzuning dolzarbligi va ahamiyati
- Tadqiqotning maqsadi va vazifalari
- Tadqiqot obyekti va predmeti
- Tadqiqot metodlari
- Ishning tuzilmasi

I BOB. NAZARIY ASOSLAR (8-10 bet):
- Asosiy tushunchalar va ta'riflar
- Nazariy yondashuvlar
- Xorijiy va mahalliy tajribalar tahlili
- Ilmiy adabiyotlar sharhi

II BOB. AMALIY TAHLIL (10-12 bet):
- Joriy holat tahlili
- Muammolar va ularning sabablari
- Raqamli ma'lumotlar va statistik tahlil
- Amaliy misollar va keis-tadqiqotlar

III BOB. TAKLIFLAR VA YECHIMLAR (8-10 bet):
- Muammolarni hal qilish yo'llari
- Takomillashtirilgan yechimlar
- Amalga oshirish mexanizmlari
- Kutilayotgan natijalar

XULOSA VA TAKLIFLAR (3-4 bet):
- Asosiy xulosalar
- Amaliy tavsiyalar
- Kelgusi rivojlanish istiqbollari

FOYDALANILGAN ADABIYOTLAR RO'YXATI (kamida 20 ta manba)

KURS ISHI QUYIDAGI TALABLARGA JAVOB BERISHI KERAK:
- Ilmiy-akademik uslubda yozilgan
- Har bir bob chuqur tahlil qilingan
- Konkret misollar va ma'lumotlar berilgan
- Professional terminologiya ishlatilgan
- Mantiqiy ketma-ketlik saqlangan
- Har bir bob o'z xulosalariga ega

MUHIM: Kurs ishini to'liq, batafsil va professional darajada yozing. Har bir bob kamida 3000 so'zdan iborat bo'lsin."""

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

async def generate_kurs_ishi_full(topic: str, subject: str, fish: str, university: str, course_number: int) -> dict:
    """OpenAI orqali to'liq kurs ishi yaratish"""
    try:
        prompt = KURS_ISH_FULL_PROMPT.format(
            topic=topic,
            subject=subject,
            fish=fish,
            university=university,
            course_number=course_number
        )
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Siz professional akademik yozuvchi siz. To'liq, batafsil va yuqori sifatli kurs ishi yarating."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=8000,
            timeout=180.0
        )
        
        content = response.choices[0].message.content or ""
        
        if not content or len(content) < 1000:
            raise ValueError("AI javob juda qisqa. Iltimos, qaytadan urinib ko'ring.")
        
        result = {
            "kirish": "",
            "bob1": "",
            "bob2": "",
            "bob3": "",
            "xulosa": "",
            "adabiyotlar": "",
            "full_content": content
        }
        
        logger.info(f"To'liq kurs ishi muvaffaqiyatli yaratildi: {topic}")
        return result
    
    except openai.APIError as e:
        logger.error(f"OpenAI API xatolik: {e}")
        raise Exception("AI xizmati bilan bog'lanishda xatolik. Iltimos, keyinroq urinib ko'ring.")
    except openai.RateLimitError:
        logger.error("OpenAI rate limit exceeded")
        raise Exception("Juda ko'p so'rov. Iltimos, biroz kuting va qaytadan urinib ko'ring.")
    except Exception as e:
        logger.error(f"Kurs ishi yaratishda xatolik: {e}")
        raise

async def generate_maqola(topic: str) -> str:
    """OpenAI orqali maqola yaratish"""
    try:
        prompt = MAQOLA_PROMPT.format(topic=topic)
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Siz professional maqola muallifi siz."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000,
            timeout=120.0
        )
        
        content = response.choices[0].message.content or ""
        
        if not content or len(content) < 100:
            raise ValueError("AI javob juda qisqa yoki bo'sh")
        
        logger.info(f"Maqola muvaffaqiyatli yaratildi: {topic}")
        return content
    
    except openai.APIError as e:
        logger.error(f"OpenAI API xatolik: {e}")
        raise Exception("AI xizmati bilan bog'lanishda xatolik. Iltimos, keyinroq urinib ko'ring.")
    except openai.RateLimitError:
        logger.error("OpenAI rate limit exceeded")
        raise Exception("Juda ko'p so'rov. Iltimos, biroz kuting va qaytadan urinib ko'ring.")
    except Exception as e:
        logger.error(f"Maqola yaratishda xatolik: {e}")
        raise
