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

async def generate_section(section_prompt: str, section_name: str, min_words: int = 1000, max_tokens: int = 4000) -> str:
    """Bir bo'limni yaratish"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Siz professional akademik yozuvchi siz. Batafsil, ilmiy va yuqori sifatli matn yarating."},
                {"role": "user", "content": section_prompt}
            ],
            temperature=0.7,
            max_tokens=max_tokens,
            timeout=180.0
        )
        
        content = response.choices[0].message.content or ""
        word_count = len(content.split())
        
        if not content or word_count < min_words:
            raise ValueError(f"{section_name} juda qisqa: {word_count} so'z (kerak: {min_words}+ so'z)")
        
        logger.info(f"{section_name} yaratildi: {word_count} so'z, {len(content)} belgi")
        return content
    
    except Exception as e:
        logger.error(f"{section_name} yaratishda xatolik: {e}")
        raise

async def generate_kurs_ishi_full(topic: str, subject: str, fish: str, university: str, course_number: int) -> dict:
    """OpenAI orqali to'liq kurs ishi yaratish - har bir bob alohida"""
    try:
        logger.info(f"Kurs ishi yaratish boshlandi: {topic}")
        
        kirish_prompt = f"""Quyidagi mavzu bo'yicha KIRISH qismini yozing (3-4 bet, ~1500 so'z):

Mavzu: {topic}
Fan: {subject}
O'quv yurti: {university}

KIRISH qismida quyidagilar bo'lishi kerak:
1. Mavzuning dolzarbligi va zamonaviy ahamiyati (1 bet)
2. Tadqiqotning maqsadi va vazifalari (0.5 bet)
3. Tadqiqot obyekti va predmeti (0.5 bet)
4. Qo'llaniladigan tadqiqot metodlari (0.5 bet)
5. Ishning tuzilmasi va qisqacha mazmuni (0.5-1 bet)

Professional, ilmiy tilda, batafsil yozing."""

        bob1_prompt = f"""Quyidagi mavzu bo'yicha I BOB. NAZARIY ASOSLAR qismini yozing (8-10 bet, ~3000 so'z):

Mavzu: {topic}
Fan: {subject}

I BOB da quyidagilar bo'lishi kerak:
1.1. Asosiy tushunchalar va ta'riflar (2-3 bet)
1.2. Nazariy yondashuvlar va konsepsiyalar (2-3 bet)
1.3. Xorijiy va mahalliy tajribalar tahlili (2-3 bet)
1.4. Ilmiy adabiyotlar sharhi (2 bet)

Har bir bo'limda konkret misollar, nazariy asoslar va ilmiy manbalardan kelinma dalillar bering. Professional, akademik tilda yozing."""

        bob2_prompt = f"""Quyidagi mavzu bo'yicha II BOB. AMALIY TAHLIL qismini yozing (10-12 bet, ~3500 so'z):

Mavzu: {topic}
Fan: {subject}

II BOB da quyidagilar bo'lishi kerak:
2.1. Joriy holat tahlili (3-4 bet)
2.2. Muammolar va ularning sabablari (3-4 bet)
2.3. Raqamli ma'lumotlar va statistik tahlil (2-3 bet)
2.4. Amaliy misollar va keis-tadqiqotlar (2-3 bet)

Konkret raqamlar, jadvallar, tahlillar va amaliy misollar bilan boyiting. Professional akademik tilda yozing."""

        bob3_prompt = f"""Quyidagi mavzu bo'yicha III BOB. TAKLIFLAR VA YECHIMLAR qismini yozing (8-10 bet, ~3000 so'z):

Mavzu: {topic}
Fan: {subject}

III BOB da quyidagilar bo'lishi kerak:
3.1. Muammolarni hal qilish yo'llari (3-4 bet)
3.2. Takomillashtirilgan yechimlar (2-3 bet)
3.3. Amalga oshirish mexanizmlari (2-3 bet)
3.4. Kutilayotgan natijalar va samaradorlik (1-2 bet)

Konkret, amaliy va amalga oshiriladigan yechimlar taqdim eting. Professional akademik tilda yozing."""

        xulosa_prompt = f"""Quyidagi mavzu bo'yicha XULOSA VA TAKLIFLAR qismini yozing (3-4 bet, ~1500 so'z):

Mavzu: {topic}
Fan: {subject}

XULOSA qismida:
1. Olingan asosiy xulosalar (1.5-2 bet)
2. Amaliy tavsiyalar (1 bet)
3. Kelgusi rivojlanish istiqbollari (0.5-1 bet)

Aniq, ixcham va professional tilda yozing."""

        adabiyotlar_prompt = f"""Quyidagi mavzu bo'yicha FOYDALANILGAN ADABIYOTLAR RO'YXATI yarating (kamida 25 ta manba):

Mavzu: {topic}
Fan: {subject}

Adabiyotlar ro'yxati quyidagilardan iborat bo'lishi kerak:
- O'zbek va rus tillaridagi kitoblar (10-12 ta)
- Xorijiy manbalar va tarjima kitoblar (5-7 ta)
- Ilmiy maqolalar va jurnallar (5-7 ta)
- Internet manbalar va rasmiy saytlar (3-5 ta)

Har bir manbani to'g'ri bibliografik formatda yozing."""

        logger.info("Kurs ishining barcha qismlari yaratilmoqda...")
        
        kirish = await generate_section(kirish_prompt, "KIRISH", min_words=1200, max_tokens=3000)
        bob1 = await generate_section(bob1_prompt, "I BOB", min_words=2500, max_tokens=5000)
        bob2 = await generate_section(bob2_prompt, "II BOB", min_words=3000, max_tokens=6000)
        bob3 = await generate_section(bob3_prompt, "III BOB", min_words=2500, max_tokens=5000)
        xulosa = await generate_section(xulosa_prompt, "XULOSA", min_words=1200, max_tokens=3000)
        adabiyotlar = await generate_section(adabiyotlar_prompt, "ADABIYOTLAR", min_words=400, max_tokens=2000)
        
        ilovalar_prompt = f"""Quyidagi mavzu bo'yicha ILOVALAR qismini yarating (~500 so'z):

Mavzu: {topic}
Fan: {subject}

ILOVALAR qismida:
- Jadvallar, grafiklar, diagrammalar tavsifi
- Qo'shimcha hujjatlar
- Statistik ma'lumotlar
- Amaliy materiallar

Professional tarzda yozing."""

        ilovalar = await generate_section(ilovalar_prompt, "ILOVALAR", min_words=300, max_tokens=2000)
        
        full_content = f"{kirish}\n\n{bob1}\n\n{bob2}\n\n{bob3}\n\n{xulosa}\n\n{adabiyotlar}\n\n{ilovalar}"
        
        word_count = len(full_content.split())
        
        if word_count < 11000:
            raise ValueError(
                f"Kurs ishi kerakli hajmga yetmadi!\n"
                f"Yaratildi: {word_count} so'z\n"
                f"Kerak: 11,000-14,000 so'z (35-40 bet)\n\n"
                f"Iltimos, qaytadan urinib ko'ring."
            )
        
        if word_count > 16000:
            logger.warning(f"Kurs ishi juda uzun: {word_count} so'z (optimal: 11,000-14,000)")
        
        result = {
            "kirish": kirish,
            "bob1": bob1,
            "bob2": bob2,
            "bob3": bob3,
            "xulosa": xulosa,
            "adabiyotlar": adabiyotlar,
            "ilovalar": ilovalar,
            "full_content": full_content,
            "word_count": word_count
        }
        
        logger.info(f"To'liq kurs ishi yaratildi: {word_count} so'z (~{word_count // 300} bet)")
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
            model="gpt-4-turbo",
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
