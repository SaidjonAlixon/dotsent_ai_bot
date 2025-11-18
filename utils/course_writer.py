import os
import re
import asyncio
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def parse_plan(plan_content):
    """REJA dan bob va band sarlavhalarini ajratib olish"""
    titles = {
        'chapter1': {'title': 'I BOB. NAZARIY ASOSLAR VA ADABIYOTLAR TAHLILI', 'subsections': []},
        'chapter2': {'title': 'II BOB. AMALIY TAHLIL VA TADQIQOT', 'subsections': []},
        'chapter3': {'title': 'III BOB. TAKOMILLASHTIRISH TAKLIFLARI VA YECHIMLAR', 'subsections': []}
    }
    
    lines = plan_content.split('\n')
    current_chapter = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # I BOB ni topish
        if line.startswith('I BOB'):
            titles['chapter1']['title'] = line
            current_chapter = 'chapter1'
        # II BOB ni topish
        elif line.startswith('II BOB'):
            titles['chapter2']['title'] = line
            current_chapter = 'chapter2'
        # III BOB ni topish
        elif line.startswith('III BOB'):
            titles['chapter3']['title'] = line
            current_chapter = 'chapter3'
        # 1.1, 1.2 kabi bandlarni topish
        elif current_chapter and re.match(r'^\d+\.\d+', line):
            # "1.1. Sarlavha" formatidan faqat sarlavhani olish
            parts = line.split('.', 2)  # "1", "1", " Sarlavha"
            if len(parts) >= 3:
                number = f"{parts[0]}.{parts[1]}"
                title = parts[2].strip()
                titles[current_chapter]['subsections'].append({
                    'number': number,
                    'title': title
                })
    
    return titles


async def generate_course_work(user_data):
    name = user_data['name']
    university = user_data['university']
    subject = user_data['subject']
    topic = user_data['topic']
    course = user_data['course']

    sections = []

    sections.append({
        'type':
        'title_page',
        'content':
        generate_title_page(name, university, subject, topic, course)
    })

    # REJA ni alohida thread'da yaratish (blocking'dan qochish)
    loop = asyncio.get_event_loop()
    plan_content = await loop.run_in_executor(None, generate_plan, subject, topic)
    sections.append({'type': 'plan', 'content': plan_content})
    
    # REJA dan sarlavhalarni ajratib olish
    plan_titles = parse_plan(plan_content)

    # ANNOTATSIYA ni 3 tilda yaratish (O'zbek, Ingliz, Rus)
    annotation_uzbek = await generate_section_with_ai(
        f"Kurs ishi uchun O'zbek tilida ANNOTATSIYA yozing. Fan: {subject}, Mavzu: {topic}. "
        f"Annotatsiya quyidagilarni o'z ichiga olishi kerak:\n"
        f"1. Tadqiqotning asosiy maqsadi va vazifalari\n"
        f"2. Tadqiqot metodologiyasi\n"
        f"3. Asosiy natijalar va xulosalar\n"
        f"4. Tadqiqotning ilmiy va amaliy ahamiyati\n\n"
        f"Annotatsiya qisqa, aniq va professional bo'lishi kerak (taxminan 150-200 so'z). "
        f"Matn ilmiy uslubda, uzluksiz yozilsin.",
        max_words=250)
    
    annotation_english = await generate_section_with_ai(
        f"Write an ABSTRACT in English for a course work. Subject: {subject}, Topic: {topic}. "
        f"The abstract should include:\n"
        f"1. Main purpose and objectives of the research\n"
        f"2. Research methodology\n"
        f"3. Main results and conclusions\n"
        f"4. Scientific and practical significance of the research\n\n"
        f"The abstract should be brief, clear and professional (approximately 150-200 words). "
        f"Write in scientific style, continuously.",
        max_words=250)
    
    annotation_russian = await generate_section_with_ai(
        f"Напишите АННОТАЦИЮ на русском языке для курсовой работы. Предмет: {subject}, Тема: {topic}. "
        f"Аннотация должна включать:\n"
        f"1. Основную цель и задачи исследования\n"
        f"2. Методологию исследования\n"
        f"3. Основные результаты и выводы\n"
        f"4. Научное и практическое значение исследования\n\n"
        f"Аннотация должна быть краткой, четкой и профессиональной (примерно 150-200 слов). "
        f"Текст должен быть написан в научном стиле, непрерывно.",
        max_words=250)
    
    sections.append({
        'type': 'annotation',
        'content': {
            'uzbek': annotation_uzbek,
            'english': annotation_english,
            'russian': annotation_russian
        }
    })

    intro_content = await generate_section_with_ai(
        f"Kurs ishi uchun KIRISH qismini yozing. Bu qism 4-5 betni tashkil qilishi kerak (taxminan 1400-1600 so'z). "
        f"Fan: {subject}, Mavzu: {topic}. "
        f"KIRISH qismida quyidagilarni JUDA BATAFSIL yozing:\n"
        f"1. Mavzuning dolzarbligi va ahamiyati (global va mahalliy kontekstda)\n"
        f"2. Tadqiqotning maqsadi va vazifalari (kamida 4-5 ta vazifa)\n"
        f"3. Tadqiqot ob'ekti va predmeti\n"
        f"4. Tadqiqot metodologiyasi\n"
        f"5. Ishning ilmiy va amaliy ahamiyati\n\n"
        f"Matn ilmiy uslubda, uzluksiz, bir oqimda yozilsin. Paragraflar orasiga enter tashlamang. "
        f"Matn to'liq, JUDA BATAFSIL va professional bo'lishi kerak. Har bir qismni chuqur va keng yoritib bering.",
        max_words=3000)
    sections.append({'type': 'intro', 'content': intro_content})

    chapter1_section1 = await generate_section_with_ai(
        f"Kurs ishi I BOB ning 1.1-bandini yozing (5-6 bet, taxminan 1800-2000 so'z). "
        f"Fan: {subject}, Mavzu: {topic}. "
        f"1.1-band nazariy asoslar va tushunchalar bo'lishi kerak. "
        f"Asosiy tushunchalar, ta'riflar, tarixiy rivojlanish va nazariy yondashuvlarni JUDA BATAFSIL bayon qiling. "
        f"Matn ilmiy uslubda, uzluksiz, bir oqimda yozilsin. Paragraflar orasiga enter tashlamang. "
        f"Har bir tushunchani chuqur va keng yoritib bering.",
        max_words=3200)

    chapter1_section2 = await generate_section_with_ai(
        f"Kurs ishi I BOB ning 1.2-bandini yozing (5-6 bet, taxminan 1800-2000 so'z). "
        f"Fan: {subject}, Mavzu: {topic}. "
        f"1.2-band xorijiy va mahalliy tajribalar tahlili bo'lishi kerak. "
        f"Jahon va O'zbekiston amaliyotini qiyosiy tahlil qiling, adabiyotlar sharhi bering. "
        f"Matn ilmiy uslubda, uzluksiz, bir oqimda yozilsin. Paragraflar orasiga enter tashlamang. "
        f"JUDA BATAFSIL va professional bayon qiling.",
        max_words=3200)

    # REJA dan olingan sarlavhalardan foydalanish
    ch1_subsections = plan_titles['chapter1']['subsections']
    sections.append({
        'type': 'chapter1',
        'title': plan_titles['chapter1']['title'],
        'subsections': [{
            'number': ch1_subsections[0]['number'] if len(ch1_subsections) > 0 else '1.1',
            'title': ch1_subsections[0]['title'] if len(ch1_subsections) > 0 else 'Asosiy tushunchalar va nazariy asoslar',
            'content': chapter1_section1
        }, {
            'number': ch1_subsections[1]['number'] if len(ch1_subsections) > 1 else '1.2',
            'title': ch1_subsections[1]['title'] if len(ch1_subsections) > 1 else 'Xorijiy va mahalliy tajribalar tahlili',
            'content': chapter1_section2
        }]
    })

    chapter2_section1 = await generate_section_with_ai(
        f"Kurs ishi II BOB ning 2.1-bandini yozing (6-7 bet, taxminan 2000-2200 so'z). "
        f"Fan: {subject}, Mavzu: {topic}. "
        f"2.1-band amaliy tahlil va holat tadqiqi bo'lishi kerak. "
        f"Joriy holat tahlili, muammolar va ularning sabablari, statistik ma'lumotlar va faktlar keltirilsin. "
        f"Matn ilmiy uslubda, uzluksiz, bir oqimda yozilsin. Paragraflar orasiga enter tashlamang. "
        f"JUDA BATAFSIL va chuqur tahlil qiling.",
        max_words=3500)

    chapter2_section2 = await generate_section_with_ai(
        f"Kurs ishi II BOB ning 2.2-bandini yozing (6-7 bet, taxminan 2000-2200 so'z). "
        f"Fan: {subject}, Mavzu: {topic}. "
        f"2.2-band tendentsiyalar va rivojlanish yo'nalishlari tahlili bo'lishi kerak. "
        f"Zamonaviy tendentsiyalar, texnologiyalar, innovatsiyalar va istiqbollarni batafsil tahlil qiling. "
        f"Matn ilmiy uslubda, uzluksiz, bir oqimda yozilsin. Paragraflar orasiga enter tashlamang. "
        f"JUDA BATAFSIL va professional bayon qiling.",
        max_words=3500)

    ch2_subsections = plan_titles['chapter2']['subsections']
    sections.append({
        'type': 'chapter2',
        'title': plan_titles['chapter2']['title'],
        'subsections': [{
            'number': ch2_subsections[0]['number'] if len(ch2_subsections) > 0 else '2.1',
            'title': ch2_subsections[0]['title'] if len(ch2_subsections) > 0 else 'Amaliy tahlil va holat tadqiqi',
            'content': chapter2_section1
        }, {
            'number': ch2_subsections[1]['number'] if len(ch2_subsections) > 1 else '2.2',
            'title': ch2_subsections[1]['title'] if len(ch2_subsections) > 1 else 'Tendentsiyalar va rivojlanish yo\'nalishlari',
            'content': chapter2_section2
        }]
    })

    chapter3_section1 = await generate_section_with_ai(
        f"Kurs ishi III BOB ning 3.1-bandini yozing (5-6 bet, taxminan 1800-2000 so'z). "
        f"Fan: {subject}, Mavzu: {topic}. "
        f"3.1-band muammolarni yechish bo'yicha takliflar bo'lishi kerak. "
        f"Aniqlangan muammolarni bartaraf etish uchun aniq, amaliy takliflar bering. "
        f"Matn ilmiy uslubda, uzluksiz, bir oqimda yozilsin. Paragraflar orasiga enter tashlamang. "
        f"JUDA BATAFSIL va amaliy yondashuvda bayon qiling.",
        max_words=3200)

    chapter3_section2 = await generate_section_with_ai(
        f"Kurs ishi III BOB ning 3.2-bandini yozing (5-6 bet, taxminan 1800-2000 so'z). "
        f"Fan: {subject}, Mavzu: {topic}. "
        f"3.2-band takomillashtirish choralari va istiqbollari bo'lishi kerak. "
        f"Takliflarni amalga oshirish mexanizmlari, kutilayotgan natijalar va istiqbollarni batafsil yoritib bering. "
        f"Matn ilmiy uslubda, uzluksiz, bir oqimda yozilsin. Paragraflar orasiga enter tashlamang. "
        f"JUDA BATAFSIL va professional bayon qiling.",
        max_words=3200)

    ch3_subsections = plan_titles['chapter3']['subsections']
    sections.append({
        'type': 'chapter3',
        'title': plan_titles['chapter3']['title'],
        'subsections': [{
            'number': ch3_subsections[0]['number'] if len(ch3_subsections) > 0 else '3.1',
            'title': ch3_subsections[0]['title'] if len(ch3_subsections) > 0 else 'Muammolarni yechish bo\'yicha takliflar',
            'content': chapter3_section1
        }, {
            'number': ch3_subsections[1]['number'] if len(ch3_subsections) > 1 else '3.2',
            'title': ch3_subsections[1]['title'] if len(ch3_subsections) > 1 else 'Takomillashtirish choralari va istiqbollari',
            'content': chapter3_section2
        }]
    })

    conclusion_content = await generate_section_with_ai(
        f"Kurs ishi uchun XULOSA qismini yozing (4-5 bet, taxminan 1400-1600 so'z). "
        f"Fan: {subject}, Mavzu: {topic}. "
        f"XULOSA qismida:\n"
        f"1. Tadqiqotning asosiy natijalari va xulosalarini umumlashtiring\n"
        f"2. Har bir bobdan kelib chiqqan xulosalarni sanab o'ting\n"
        f"3. Amaliy takliflarning qisqacha xulosasini bering\n"
        f"4. Tadqiqotning ilmiy va amaliy ahamiyatini ta'kidlang\n\n"
        f"Matn ilmiy uslubda, uzluksiz, bir oqimda yozilsin. Paragraflar orasiga enter tashlamang. "
        f"JUDA BATAFSIL va chuqur xulosalar bering.",
        max_words=3000)
    sections.append({'type': 'conclusion', 'content': conclusion_content})

    # ADABIYOTLAR ni alohida thread'da yaratish (blocking'dan qochish)
    references_content = await loop.run_in_executor(None, generate_references, subject, topic)
    sections.append({'type': 'references', 'content': references_content})

    # ILOVALAR ni AI orqali yaratish
    appendix_content = await generate_appendix(subject, topic)
    sections.append({'type': 'appendix', 'content': appendix_content})
    
    toc_content = plan_content
    sections.append({'type': 'toc', 'content': toc_content})

    return sections


async def generate_section_with_ai(prompt, max_words=3000):
    try:
        # OpenAI chaqiruvini alohida thread'da ishga tushirish (blocking'dan qochish)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role":
                    "system",
                    "content":
                    "Siz O'zbekiston oliygohlaridagi talabalar uchun kurs ishi yozuvchi sun'iy intellektsiz. "
                    "Matnni to'liq, ilmiy uslubda, batafsil va professional darajada yozing. "
                    "Matn bir oqimda, uzluksiz yozilishi kerak. Paragraflar orasiga qo'shimcha bo'shliq tashlamang. "
                    "Har bir gap mantiqiy ravishda keyingi gapga bog'lanishi kerak."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                max_tokens=int(max_words * 1.5)
            )
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI xatolik: {e}")
        return f"[AI bilan bog'lanishda xatolik yuz berdi: {str(e)}]"


def generate_title_page(name, university, subject, topic, course):
    return f"""O'ZBEKISTON RESPUBLIKASI OLIY VA O'RTA MAXSUS
TA'LIM VAZIRLIGI

{university.upper()}

{subject.upper()} FANIDAN

KURS ISHI

Mavzu: {topic}

Bajardi: {course}-kurs talabasi
{name}

Qabul qildi: __________________

Toshkent – 2025
"""


def generate_plan(subject, topic):
    """Sinxron funksiya - faqat generate_course_work dan chaqiriladi"""
    try:
        prompt = f"""Fan: {subject}
Mavzu: {topic}

Yuqoridagi mavzu bo'yicha kurs ishi uchun REJA tuzing. 

Reja quyidagi formatda bo'lishi kerak:

KIRISH

I BOB. [Mavzuga mos 1-bob sarlavhasi - NAZARIY ASOSLAR]
1.1. [Mavzuga mos 1.1-band sarlavhasi]
1.2. [Mavzuga mos 1.2-band sarlavhasi]

II BOB. [Mavzuga mos 2-bob sarlavhasi - AMALIY TAHLIL]
2.1. [Mavzuga mos 2.1-band sarlavhasi]
2.2. [Mavzuga mos 2.2-band sarlavhasi]

III BOB. [Mavzuga mos 3-bob sarlavhasi - TAKLIFLAR]
3.1. [Mavzuga mos 3.1-band sarlavhasi]
3.2. [Mavzuga mos 3.2-band sarlavhasi]

XULOSA

FOYDALANILGAN ADABIYOTLAR RO'YXATI

ILOVALAR

MUHIM: 
- Faqat rejani yozing, boshqa hech narsa yozilmasin
- Har bir bob va band sarlavhasi mavzuga to'g'ridan-to'g'ri bog'liq bo'lishi kerak
- Sarlavhalar aniq, qisqa va professional bo'lishi kerak
- Faqat yuqoridagi formatda yozing"""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Siz kurs ishi uchun professional reja tuzuvchisiz. Faqat reja matnini qaytaring, boshqa hech narsa yozmang."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        plan = response.choices[0].message.content.strip()
        return plan
        
    except Exception as e:
        print(f"Reja yaratishda xatolik: {e}")
        return """KIRISH

I BOB. NAZARIY ASOSLAR VA ADABIYOTLAR TAHLILI
1.1. Asosiy tushunchalar va nazariy asoslar
1.2. Xorijiy va mahalliy tajribalar tahlili

II BOB. AMALIY TAHLIL VA TADQIQOT
2.1. Amaliy tahlil va holat tadqiqi
2.2. Tendentsiyalar va rivojlanish yo'nalishlari

III BOB. TAKOMILLASHTIRISH TAKLIFLARI VA YECHIMLAR
3.1. Muammolarni yechish bo'yicha takliflar
3.2. Takomillashtirish choralari va istiqbollari

XULOSA

FOYDALANILGAN ADABIYOTLAR RO'YXATI

ILOVALAR"""


def generate_references(subject, topic):
    try:
        prompt = f"""Fan: {subject}
Mavzu: {topic}

Yuqoridagi mavzu bo'yicha kurs ishi uchun FOYDALANILGAN ADABIYOTLAR RO'YXATI tuzing.

Adabiyotlar ro'yxati quyidagilarni o'z ichiga olishi kerak:
1. O'zbekiston qonunlari va me'yoriy hujjatlar (2-3 ta)
2. O'zbek mualliflarining kitoblari (5-7 ta)
3. Rus va xorijiy mualliflarning kitoblari (5-7 ta)
4. Ilmiy jurnallar va maqolalar (3-5 ta)
5. Internet manbalari (3-5 ta)

JAMI: kamida 25 ta manba

Format:
1. Muallif. Kitob nomi. – Nashr: Nashriyot, yil.
2. ...

MUHIM:
- Faqat adabiyotlar ro'yxatini yozing
- Har bir manba mavzuga mos bo'lishi kerak
- Manbalar haqiqiy ko'rinishda bo'lishi kerak (real muallif va kitob nomlari)
- Kamida 25 ta manba bo'lishi shart
- Raqamli tartibda yozing"""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Siz kurs ishi uchun professional adabiyotlar ro'yxati tuzuvchisiz. Faqat adabiyotlar ro'yxatini qaytaring."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        references = response.choices[0].message.content.strip()
        return references
        
    except Exception as e:
        print(f"Adabiyotlar yaratishda xatolik: {e}")
        return """1. O'zbekiston Respublikasining Ta'lim to'g'risidagi Qonuni. – T.: 2020.
2. O'zbekiston Respublikasi Prezidentining Farmonlari va Qarorlari to'plami. – T.: 2020-2025.
3. Karimov I.A. Yuksak ma'naviyat – yengilmas kuch. – T.: Ma'naviyat, 2008.
4. Mirziyoyev Sh.M. Tanqidiy tahlil, qat'iy tartib-intizom va shaxsiy javobgarlik – har bir rahbar faoliyatining kundalik qoidasi bo'lishi kerak. – T.: O'zbekiston, 2017.
5. O'zbekiston milliy ensiklopediyasi. – T.: 2000-2006.
6. Internet manbalari: www.lex.uz, www.press-service.uz, www.ziyonet.uz
7. Maxsus adabiyotlar va ilmiy jurnallar."""


async def generate_appendix(subject, topic):
    """ILOVALAR bo'limini yaratish - kod yozishga mos mavzular uchun kod va natija, boshqalar uchun diagramma/ko'rsatkichlar"""
    try:
        # Mavzuni kod yozishga mosligini tekshirish
        coding_keywords = [
            'dasturlash', 'programming', 'kod', 'code', 'algoritm', 'algorithm', 
            'kompyuter', 'computer', 'software', 'dastur', 'application', 
            'python', 'java', 'javascript', 'c++', 'c#', 'php', 'html', 'css',
            'database', 'baza', 'web', 'sayt', 'mobil', 'mobile', 'android', 'ios',
            'artificial intelligence', 'sun\'iy intellekt', 'machine learning', 'mashina o\'rganishi',
            'data structure', 'ma\'lumotlar strukturas', 'network', 'tarmoq',
            'security', 'xavfsizlik', 'cybersecurity', 'kiberxavfsizlik'
        ]
        
        topic_lower = topic.lower()
        subject_lower = subject.lower()
        combined_text = f"{subject_lower} {topic_lower}"
        
        is_coding_related = any(keyword in combined_text for keyword in coding_keywords)
        
        if is_coding_related:
            # Kod yozishga mos mavzu - kod va natija yozish
            appendix_content = await generate_section_with_ai(
                f"Kurs ishi uchun ILOVALAR bo'limini yozing. Fan: {subject}, Mavzu: {topic}. "
                f"Bu mavzu kod yozishga oid, shuning uchun quyidagilarni yozing:\n\n"
                f"1-ILOVA bo'limida:\n"
                f"- Kod va dastur\n"
                f"- Kodning to'liq matni (mavzu bo'yicha real kod, masalan Python, Java, JavaScript va h.k.)\n"
                f"- Kodning har bir qismini qisqacha tushuntirish\n"
                f"- Dastur ishlashi uchun kerakli kutubxonalar va konfiguratsiyalar\n\n"
                f"2-ILOVA bo'limida:\n"
                f"- Dasturning ishlashi natijalari\n"
                f"- Screenshot'lar yoki chiqish natijalari tavsifi (text formatda)\n"
                f"- Natijalarni tahlil qilish va sharhlash\n"
                f"- Dasturning afzalliklari va cheklovlari\n\n"
                f"Format:\n"
                f"1-ILOVA\n"
                f"Kod va dastur\n"
                f"[Bu yerda to'liq kod va tushuntirishlar]\n\n"
                f"2-ILOVA\n"
                f"Dastur ishlashi natijalari\n"
                f"[Bu yerda natijalar va tahlil]\n\n"
                f"Matn ilmiy uslubda, uzluksiz yozilsin. Kod va natijalar professional va mavzuga mos bo'lishi kerak. "
                f"Hech qanday holatda bo'sh qolmasligi kerak.",
                max_words=2000
            )
        else:
            # Kod yozishga mos bo'lmagan mavzu - diagramma va ko'rsatkichlar
            appendix_content = await generate_section_with_ai(
                f"Kurs ishi uchun ILOVALAR bo'limini yozing. Fan: {subject}, Mavzu: {topic}. "
                f"Bu mavzu kod yozishga mos emas, shuning uchun quyidagilarni yozing:\n\n"
                f"1-ILOVA bo'limida:\n"
                f"- Jadval va diagrammalar\n"
                f"- Mavzu bo'yicha jadvallar (tadqiqot natijalari, statistik ma'lumotlar, solishtirish jadvallari)\n"
                f"- Diagrammalar tavsifi (grafiklar, pie chart, bar chart, line chart va h.k.)\n"
                f"- Har bir jadval va diagrammaning maqsadi va ahamiyati\n"
                f"- Jadvallardagi ma'lumotlarni tahlil qilish\n\n"
                f"2-ILOVA bo'limida:\n"
                f"- Qo'shimcha materiallar va ko'rsatkichlar\n"
                f"- Mavzuga oid ko'rsatkichlar (statistik ma'lumotlar, tahlillar)\n"
                f"- Qo'shimcha grafiklar yoki vizual materiallar tavsifi\n"
                f"- So'rovnomalar natijalari yoki boshqa tadqiqot ma'lumotlari\n"
                f"- Materiallarning tadqiqotga qo'shgan hissasi\n\n"
                f"Format:\n"
                f"1-ILOVA\n"
                f"Jadval va diagrammalar\n"
                f"[Bu yerda jadvallar va diagrammalar tavsifi]\n\n"
                f"2-ILOVA\n"
                f"Qo'shimcha materiallar\n"
                f"[Bu yerda qo'shimcha materiallar tavsifi]\n\n"
                f"Matn ilmiy uslubda, uzluksiz yozilsin. Jadvallar va diagrammalar professional va mavzuga mos bo'lishi kerak. "
                f"Hech qanday holatda bo'sh qolmasligi kerak. Barcha ma'lumotlar haqiqiy ko'rinishda bo'lishi kerak.",
                max_words=2000
            )
        
        return appendix_content
        
    except Exception as e:
        print(f"ILOVALAR yaratishda xatolik: {e}")
        # Fallback - minimal content
        return """1-ILOVA
Jadval va diagrammalar

[Bu yerda jadvallar va diagrammalar tavsifi]

2-ILOVA
Qo'shimcha materiallar

[Bu yerda qo'shimcha materiallar tavsifi]"""