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

async def generate_section(section_prompt: str, section_name: str, min_words: int = 1000, max_tokens: int = 4000, retry_count: int = 2) -> str:
    """Bir bo'limni yaratish - retry logic bilan"""
    
    for attempt in range(retry_count):
        try:
            if attempt > 0:
                logger.info(f"{section_name} qayta yaratilmoqda (urinish {attempt + 1}/{retry_count})...")
                section_prompt += f"\n\nMUHIM: Oldingi urinish juda qisqa chiqdi. Iltimos, JUDA BATAFSIL va UZUN yozing - KAMIDA {min_words} SO'Z!"
            
            response = openai.chat.completions.create(
                model="gpt-5-nano",
                messages=[
                    {"role": "system", "content": "Siz professional akademik yozuvchi siz. JUDA BATAFSIL, UZUN va chuqur akademik matn yarating. Har bir fikrni to'liq ochib bering. Ko'proq so'z ishlatishingiz kerak - kamida kerakli so'zlar sonidan ko'p yozing. Har bir paragraf batafsil va keng yoritilgan bo'lishi shart. QISQA JAVOB BERMANG!"},
                    {"role": "user", "content": section_prompt}
                ],
                temperature=0.7,
                max_tokens=max_tokens,
                timeout=180.0,
                reasoning_effort="high"
            )
            
            content = response.choices[0].message.content or ""
            word_count = len(content.split())
            
            if word_count >= min_words:
                logger.info(f"{section_name} yaratildi: {word_count} so'z, {len(content)} belgi")
                return content
            else:
                logger.warning(f"{section_name} juda qisqa: {word_count} so'z (kerak: {min_words}+ so'z)")
                if attempt < retry_count - 1:
                    continue
                else:
                    logger.error(f"{section_name} {retry_count} marta urinishdan keyin ham qisqa: {word_count} so'z")
                    return content
        
        except Exception as e:
            logger.error(f"{section_name} yaratishda xatolik (urinish {attempt + 1}): {e}")
            if attempt < retry_count - 1:
                continue
            else:
                raise
    
    raise Exception(f"{section_name} yaratib bo'lmadi")

async def generate_kurs_ishi_full(topic: str, subject: str, fish: str, university: str, course_number: int) -> dict:
    """OpenAI orqali to'liq kurs ishi yaratish - har bir bob alohida"""
    try:
        logger.info(f"Kurs ishi yaratish boshlandi: {topic}")
        
        kirish_prompt = f"""Quyidagi mavzu bo'yicha KIRISH qismini JUDA BATAFSIL yozing.

Mavzu: {topic}
Fan: {subject}
O'quv yurti: {university}

MUHIM: Bu KIRISH bo'limi KAMIDA 1500-1800 SO'Z bo'lishi SHART (3-4 bet). Har bir qismni to'liq va batafsil yozing.

KIRISH qismida quyidagi bo'limlar BO'LISHI KERAK:

1. MAVZUNING DOLZARBLIGI VA ZAMONAVIY AHAMIYATI (400-500 so'z):
   - Ushbu mavzuning hozirgi zamon uchun nima uchun muhimligini keng yoritib bering
   - Dunyo va O'zbekiston miqyosida bu sohaning rivojlanish holatini tahlil qiling
   - Zamonaviy tendensiyalar va yangi yondashuvlarni batafsil bayon eting
   - Ushbu sohadagi dolzarb muammolarni to'liq ko'rsating
   - Konkret statistik ma'lumotlar va faktlar keltiring

2. TADQIQOTNING MAQSADI VA VAZIFALARI (300-350 so'z):
   - Tadqiqotning asosiy maqsadini aniq belgilang
   - Kamida 4-5 ta aniq vazifalarni batafsil tavsiflang
   - Har bir vazifani alohida paragrafda yoritib bering
   - Vazifalarning ahamiyatini tushuntiring

3. TADQIQOT OBYEKTI VA PREDMETI (250-300 so'z):
   - Tadqiqot obyektini to'liq va aniq belgilang
   - Tadqiqot predmetini keng qamrovda tahlil qiling
   - Obyekt va predmet o'rtasidagi bog'liqlikni tushuntiring
   - Nega aynan shu obyekt tanlanganini asoslang

4. QO'LLANILADIGAN TADQIQOT METODLARI (300-350 so'z):
   - Ilmiy tadqiqot metodlarini batafsil sanab bering
   - Har bir metodning qo'llanilish sabablarini tushuntiring
   - Nazariy metodlar (tahlil, sintez, induksiya, deduksiya va boshqalar)
   - Amaliy metodlar (kuzatish, taqqoslash, statistik tahlil va boshqalar)
   - Maxsus metodlar (agar mavzuga oid bo'lsa)

5. ISHNING TUZILMASI VA QISQACHA MAZMUNI (250-300 so'z):
   - Har bir bobning qisqacha mazmunini bering
   - Boblar orasidagi mantiqiy bog'lanishni ko'rsating
   - Ishning umumiy tuzilmasini tushuntiring

ESDA TUTING: Bu bo'lim KAMIDA 1500 SO'Z bo'lishi kerak. Har bir paragraf chuqur, ilmiy va batafsil yozilishi shart!"""

        bob1_prompt = f"""Quyidagi mavzu bo'yicha I BOB. NAZARIY ASOSLAR qismini JUDA BATAFSIL yozing.

Mavzu: {topic}
Fan: {subject}

MUHIM: Bu bob KAMIDA 3000-3500 SO'Z bo'lishi SHART (8-10 bet). Har bir qismni ilmiy va chuqur yoritib bering.

I BOB. NAZARIY ASOSLAR

1.1. ASOSIY TUSHUNCHALAR VA TA'RIFLAR (700-800 so'z):
   - Mavzuga oid barcha asosiy tushunchalarni batafsil ta'riflang
   - Har bir atamaning mohiyatini to'liq ochib bering
   - Turli olimlarning ta'riflarini taqqoslang
   - Tushunchalar orasidagi farq va o'xshashliklarni ko'rsating
   - Klassifikatsiya va tasniflarni keltiring
   - Konkret misollar va illyustratsiyalar bering

1.2. NAZARIY YONDASHUVLAR VA KONSEPSIYALAR (750-900 so'z):
   - Mavzuga oid asosiy nazariyalarni chuqur tahlil qiling
   - Har bir nazariyaning asosiy g'oyalarini batafsil bayon eting
   - Nazariyalar yaratilish tarixi va evolyutsiyasini ko'rsating
   - Turli yondashuvlarning afzalliklari va kamchiliklarini taqqoslang
   - Zamonaviy konsepsiyalar va yangi qarashlarni yoritib bering
   - Nazariyalarning amaliy qo'llanilishini tushuntiring

1.3. XORIJIY VA MAHALLIY TAJRIBALAR TAHLILI (800-900 so'z):
   - Ilg'or xorijiy mamlakatlar tajribasini batafsil o'rganing
   - Har bir davlatning yondashuvini alohida tahlil qiling
   - O'zbekistondagi holat va tajribalarni keng yoritib bering
   - Milliy xususiyatlar va o'ziga xosliklarni ko'rsating
   - Qiyosiy tahlil o'tkazing va xulosalar chiqaring
   - Qo'llash mumkin bo'lgan eng yaxshi tajribalarni aniqlang

1.4. ILMIY ADABIYOTLAR SHARHI (750-900 so'z):
   - O'zbek, rus va xorijiy olimlarn asarlarini tahlil qiling
   - Har bir manbaning qo'shgan hissasini baholang
   - Ilmiy maktablar va yo'nalishlarni taqqoslang
   - Tadqiqotlar tarixini kronologik tartibda ko'rsating
   - Zamonaviy tadqiqotlarning eng muhim natijalarini yoritib bering
   - Mavzuga oid ilmiy diskussiyalar va bahs-munozaralarni keltiring

ESDA TUTING: Har bir bo'lim chuqur akademik tahlilga ega bo'lishi kerak. Umumiy bo'lim hajmi KAMIDA 3000 SO'Z!"""

        bob2_prompt = f"""Quyidagi mavzu bo'yicha II BOB. AMALIY TAHLIL qismini JUDA BATAFSIL yozing.

Mavzu: {topic}
Fan: {subject}

MUHIM: Bu bob KAMIDA 3500-4000 SO'Z bo'lishi SHART (10-12 bet). Konkret raqamlar, jadvallar va amaliy tahlillar bilan boyiting.

II BOB. AMALIY TAHLIL

2.1. JORIY HOLAT TAHLILI (900-1000 so'z):
   - Hozirgi paytdagi holatni to'liq tahlil qiling
   - Statistik ma'lumotlar va raqamlarni keltiring
   - Asosiy ko'rsatkichlarni batafsil tahlil eting
   - Dinamikani ko'rsatuvchi jadvallar va grafiklar tavsifini bering
   - O'zbekiston va dunyo amaliyotini taqqoslang
   - Hozirgi tendensiyalar va yo'nalishlarni aniqlang
   - Kuchli va zaif tomonlarni baholang

2.2. MUAMMOLAR VA ULARNING SABABLARI (900-1000 so'z):
   - Mavjud muammolarni sistemali tahlil qiling
   - Har bir muammoni alohida va batafsil yoritib bering
   - Muammolarning asosiy sabablarini aniqlang
   - Ichki va tashqi omillarni ajrating
   - Muammolarning ta'sir darajasini baholang
   - Bir-biri bilan bog'liqliklarni ko'rsating
   - Konkret faktlar va misollar keltiring

2.3. RAQAMLI MA'LUMOTLAR VA STATISTIK TAHLIL (850-1000 so'z):
   - So'nggi yillardagi statistik ma'lumotlarni taqdim eting
   - Jadvallar va diagrammalar tavsifini batafsil bering
   - Trend tahlilini o'tkazing
   - Qiyosiy ko'rsatkichlarni keltiring
   - Dinamik o'zgarishlarni tahlil qiling
   - Prognoz va bashoratlar bering
   - Ma'lumotlarning ishonchliligini asoslang

2.4. AMALIY MISOLLAR VA KEIS-TADQIQOTLAR (850-1000 so'z):
   - Konkret amaliy misollarni batafsil tahlil qiling
   - Muvaffaqiyatli tajribalarni ko'rsating
   - Muvaffaqiyatsiz tajribalardan saboqlar chiqaring
   - Turli kompaniya/tashkilotlar tajribasini taqqoslang
   - Best practice'larni aniqlang
   - O'quv yurti/korxona/tashkilot misolida tahlil qiling
   - Amaliy tavsiyalar bering

ESDA TUTING: Bu eng katta bob bo'lib, KAMIDA 3500 SO'Z hajmida bo'lishi kerak. Ko'proq raqamlar, jadvallar va konkret faktlar!"""

        bob3_prompt = f"""Quyidagi mavzu bo'yicha III BOB. TAKLIFLAR VA YECHIMLAR qismini JUDA BATAFSIL yozing.

Mavzu: {topic}
Fan: {subject}

MUHIM: Bu bob KAMIDA 3000-3500 SO'Z bo'lishi SHART (8-10 bet). Konkret, amalga oshiriladigan takliflar bering.

III BOB. TAKLIFLAR VA YECHIMLAR

3.1. MUAMMOLARNI HAL QILISH YO'LLARI (800-900 so'z):
   - Har bir aniqlangan muammoga yechim taklif qiling
   - Qisqa muddatli va uzoq muddatli yechimlarni ajrating
   - Har bir yechimning mohiyatini batafsil tushuntiring
   - Yechimlarning ilmiy asoslanganligini ko'rsating
   - Amalga oshirish bosqichlarini belgilang
   - Resurslar va imkoniyatlarni baholang
   - Xalqaro tajribaga asoslaning

3.2. TAKOMILLASHTIRILGAN YECHIMLAR (750-900 so'z):
   - Innovatsion yondashuvlarni taklif qiling
   - Zamonaviy texnologiyalar va metodlarni qo'llashni ko'rsating
   - Raqamlashtirish imkoniyatlarini baholang
   - Avtomatlashtirish yo'llarini taklif qiling
   - Samaradorlikni oshirish choralarini batafsil yoritib bering
   - Xarajatlarni kamaytirish usullarini ko'rsating
   - Sifatni oshirish takliflarini bering

3.3. AMALGA OSHIRISH MEXANIZMLARI (750-900 so'z):
   - Takliflarni amalga oshirish bosqichlarini belgilang
   - Har bir bosqichning vazifalarini aniq ko'rsating
   - Javobgar shaxslar va tuzilmalarni aniqlang
   - Zarur resurslarni (moliyaviy, kadriy, texnik) hisoblang
   - Vaqt jadvalini tuzing
   - Monitoring va nazorat tizimini ishlab chiqing
   - Xavf va to'siqlarni bashorat qiling

3.4. KUTILAYOTGAN NATIJALAR VA SAMARADORLIK (700-800 so'z):
   - Takliflarning ijobiy natijalarini bashorat qiling
   - Miqdoriy ko'rsatkichlarni (KPI) belgilang
   - Iqtisodiy samaradorlikni hisoblang
   - Ijtimoiy ta'sirni baholang
   - Qisqa va uzoq muddatli natijalarni ajrating
   - Xavf omillarini hisobga oling
   - Monitoring va baholash mezonlarini ko'rsating

ESDA TUTING: Bu bob amaliy taklif va yechimlar bilan to'ldirilgan bo'lishi kerak. KAMIDA 3000 SO'Z!"""

        xulosa_prompt = f"""Quyidagi mavzu bo'yicha XULOSA VA TAKLIFLAR qismini BATAFSIL yozing.

Mavzu: {topic}
Fan: {subject}

MUHIM: Bu bo'lim KAMIDA 1500-1800 SO'Z bo'lishi SHART (3-4 bet). Aniq va to'liq xulosalar bering.

XULOSA VA TAKLIFLAR

1. OLINGAN ASOSIY XULOSALAR (600-700 so'z):
   - Tadqiqotning asosiy natijalarini umumlashtiring
   - Har bir bob bo'yicha qisqacha xulosalar bering
   - Tadqiqot maqsadiga erishilganini ko'rsating
   - Barcha vazifalarga javob topilganini tasdiqlang
   - Nazariy va amaliy natijalarni ajrating
   - Eng muhim topilmalarni ta'kidlang
   - Ilmiy va amaliy ahamiyatini baholang

2. AMALIY TAVSIYALAR (500-600 so'z):
   - Konkret amaliy tavsiyalar bering
   - Kimga, nima uchun tavsiya etilayotganini aniq ko'rsating
   - Davlat organlari uchun tavsiyalar
   - Korxonalar va tashkilotlar uchun tavsiyalar
   - Ta'lim muassasalari uchun tavsiyalar
   - Amalga oshirish yo'llarini qisqacha ko'rsating
   - Kutilayotgan samaradorlikni eslatib o'ting

3. KELGUSI RIVOJLANISH ISTIQBOLLARI (400-500 so'z):
   - Kelajakda tadqiq etish mumkin bo'lgan yo'nalishlarni ko'rsating
   - Yangi texnologiyalar va imkoniyatlarni bashorat qiling
   - Rivojlanish tendensiyalarini aniqlang
   - Keyingi tadqiqotlar uchun takliflar bering
   - Dolzarb yo'nalishlarni belgilang
   - Kelajak istiqbollarini ilmiy asoslang

ESDA TUTING: XULOSA kurs ishining eng muhim qismi. KAMIDA 1500 SO'Z bo'lishi shart!"""

        adabiyotlar_prompt = f"""Quyidagi mavzu bo'yicha FOYDALANILGAN ADABIYOTLAR RO'YXATI yarating.

Mavzu: {topic}
Fan: {subject}

MUHIM: KAMIDA 25-30 TA MANBA bo'lishi SHART. Har bir manbani to'g'ri bibliografik formatda yozing.

ADABIYOTLAR RO'YXATI TARKIBI:

1. O'ZBEK TILIDA KITOBLAR (8-10 ta):
   - Asosiy darsliklar va o'quv qo'llanmalar
   - Monografiyalar
   - To'plamlar va konferensiya materiallari
   - To'g'ri format: Muallif. Kitob nomi. - Toshkent: Nashriyot, 2020. - 250 b.

2. RUS TILIDA KITOBLAR (6-8 ta):
   - Asosiy darsliklar
   - Monografiyalar va ilmiy asarlar
   - To'g'ri format: Автор. Название. - М.: Издательство, 2019. - 300 с.

3. INGLIZ VA BOSHQA XORIJIY KITOBLAR (4-6 ta):
   - Xalqaro miqyosdagi asarlar
   - Tarjima kitoblar
   - To'g'ri format: Author. Book Title. - New York: Publisher, 2021. - 400 p.

4. ILMIY MAQOLALAR (5-7 ta):
   - Ilmiy jurnallardagi maqolalar
   - Konferensiya materiallari
   - To'g'ri format: Muallif. Maqola nomi // Jurnal nomi. - 2022. - №3. - B. 45-52.

5. INTERNET MANBALAR (3-5 ta):
   - Rasmiy saytlar (stat.uz, lex.uz, va boshqalar)
   - Elektron kutubxonalar
   - To'g'ri format: www.sayt.uz (murojaat sanasi: 15.10.2025)

ESDA TUTING: Hamma manbalar REAL va mavzuga mos bo'lishi kerak. KAMIDA 25 TA MANBA!"""

        logger.info("Kurs ishining barcha qismlari yaratilmoqda...")
        
        kirish = await generate_section(kirish_prompt, "KIRISH", min_words=1200, max_tokens=4000, retry_count=3)
        bob1 = await generate_section(bob1_prompt, "I BOB", min_words=2500, max_tokens=6000, retry_count=2)
        bob2 = await generate_section(bob2_prompt, "II BOB", min_words=3000, max_tokens=7000, retry_count=2)
        bob3 = await generate_section(bob3_prompt, "III BOB", min_words=2500, max_tokens=6000, retry_count=2)
        xulosa = await generate_section(xulosa_prompt, "XULOSA", min_words=1200, max_tokens=4000, retry_count=2)
        adabiyotlar = await generate_section(adabiyotlar_prompt, "ADABIYOTLAR", min_words=400, max_tokens=3000, retry_count=2)
        
        ilovalar_prompt = f"""Quyidagi mavzu bo'yicha ILOVALAR qismini yarating.

Mavzu: {topic}
Fan: {subject}

MUHIM: KAMIDA 500-600 SO'Z hajmida bo'lishi kerak.

ILOVALAR

ILOVA 1. JADVALLAR VA STATISTIK MA'LUMOTLAR (150-200 so'z):
   - Asosiy statistik jadvallar tavsifi
   - Dinamika jadvallari
   - Qiyosiy jadvallar
   - So'rovnoma natijalari (agar mavzuga mos bo'lsa)
   - Jadval: [nomi], manbasi, tahlili

ILOVA 2. GRAFIKLAR VA DIAGRAMMALAR (150-200 so'z):
   - Dinamik grafiklar tavsifi
   - Tuzilma diagrammalari
   - Qiyosiy grafiklar
   - Prognoz grafiklari
   - Grafik: [nomi], tahlili

ILOVA 3. SXEMALAR VA MODELLAR (100-150 so'z):
   - Jarayon sxemalari
   - Tuzilma sxemalari
   - Boshqaruv modellari
   - Algoritm sxemalari

ILOVA 4. QO'SHIMCHA MATERIALLAR (100-150 so'z):
   - Hujjatlar namunasi
   - So'rovnoma shakllari
   - Hisob-kitoblar
   - Formulalar va tenglamalar

ESDA TUTING: Har bir ilova aniq tavsif va tushuntirishga ega bo'lishi kerak. KAMIDA 500 SO'Z!"""

        ilovalar = await generate_section(ilovalar_prompt, "ILOVALAR", min_words=400, max_tokens=3000, retry_count=2)
        
        full_content = f"{kirish}\n\n{bob1}\n\n{bob2}\n\n{bob3}\n\n{xulosa}\n\n{adabiyotlar}\n\n{ilovalar}"
        
        word_count = len(full_content.split())
        
        if word_count < 10000:
            logger.warning(
                f"Kurs ishi qisqaroq chiqdi: {word_count} so'z (optimal: 11,000-14,000)\n"
                f"Lekin yetarli hajmda - davom etamiz."
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
            model="gpt-5-nano",
            messages=[
                {"role": "system", "content": "Siz professional maqola muallifi siz."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000,
            timeout=120.0,
            reasoning_effort="high"
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
