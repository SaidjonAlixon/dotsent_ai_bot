import os
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

async def generate_course_work(user_data):
    name = user_data['name']
    university = user_data['university']
    subject = user_data['subject']
    topic = user_data['topic']
    course = user_data['course']
    
    sections = []
    
    sections.append({
        'type': 'title_page',
        'content': generate_title_page(name, university, subject, topic, course)
    })
    
    plan_content = generate_plan(subject, topic)
    sections.append({'type': 'plan', 'content': plan_content})
    
    intro_content = await generate_section_with_ai(
        f"Kurs ishi uchun KIRISH qismini yozing. Bu qism 3-4 betni tashkil qilishi kerak (taxminan 1000-1200 so'z). "
        f"Fan: {subject}, Mavzu: {topic}. "
        f"KIRISH qismida quyidagilarni batafsil yozing:\n"
        f"1. Mavzuning dolzarbligi va ahamiyati (global va mahalliy kontekstda)\n"
        f"2. Tadqiqotning maqsadi va vazifalari (kamida 3-4 ta vazifa)\n"
        f"3. Tadqiqot ob'ekti va predmeti\n"
        f"4. Tadqiqot metodologiyasi\n"
        f"5. Ishning ilmiy va amaliy ahamiyati\n\n"
        f"Matn ilmiy uslubda, uzluksiz, bir oqimda yozilsin. Paragraflar orasiga enter tashlamang. "
        f"Matn to'liq, batafsil va professional bo'lishi kerak.",
        max_words=1200
    )
    sections.append({'type': 'intro', 'content': intro_content})
    
    chapter1_section1 = await generate_section_with_ai(
        f"Kurs ishi I BOB ning 1.1-bandini yozing (4-5 bet, taxminan 1400-1600 so'z). "
        f"Fan: {subject}, Mavzu: {topic}. "
        f"1.1-band nazariy asoslar va tushunchalar bo'lishi kerak. "
        f"Asosiy tushunchalar, ta'riflar, tarixiy rivojlanish va nazariy yondashuvlarni batafsil bayon qiling. "
        f"Matn ilmiy uslubda, uzluksiz, bir oqimda yozilsin. Paragraflar orasiga enter tashlamang.",
        max_words=1600
    )
    
    chapter1_section2 = await generate_section_with_ai(
        f"Kurs ishi I BOB ning 1.2-bandini yozing (4-5 bet, taxminan 1400-1600 so'z). "
        f"Fan: {subject}, Mavzu: {topic}. "
        f"1.2-band xorijiy va mahalliy tajribalar tahlili bo'lishi kerak. "
        f"Jahon va O'zbekiston amaliyotini qiyosiy tahlil qiling, adabiyotlar sharhi bering. "
        f"Matn ilmiy uslubda, uzluksiz, bir oqimda yozilsin. Paragraflar orasiga enter tashlamang.",
        max_words=1600
    )
    
    sections.append({
        'type': 'chapter1',
        'title': 'I BOB. NAZARIY ASOSLAR VA ADABIYOTLAR TAHLILI',
        'subsections': [
            {'number': '1.1', 'title': 'Asosiy tushunchalar va nazariy asoslar', 'content': chapter1_section1},
            {'number': '1.2', 'title': 'Xorijiy va mahalliy tajribalar tahlili', 'content': chapter1_section2}
        ]
    })
    
    chapter2_section1 = await generate_section_with_ai(
        f"Kurs ishi II BOB ning 2.1-bandini yozing (5-6 bet, taxminan 1800-2000 so'z). "
        f"Fan: {subject}, Mavzu: {topic}. "
        f"2.1-band amaliy tahlil va holat tadqiqi bo'lishi kerak. "
        f"Joriy holat tahlili, muammolar va ularning sabablari, statistik ma'lumotlar va faktlar keltirilsin. "
        f"Matn ilmiy uslubda, uzluksiz, bir oqimda yozilsin. Paragraflar orasiga enter tashlamang.",
        max_words=2000
    )
    
    chapter2_section2 = await generate_section_with_ai(
        f"Kurs ishi II BOB ning 2.2-bandini yozing (5-6 bet, taxminan 1800-2000 so'z). "
        f"Fan: {subject}, Mavzu: {topic}. "
        f"2.2-band tendentsiyalar va rivojlanish yo'nalishlari tahlili bo'lishi kerak. "
        f"Zamonaviy tendentsiyalar, texnologiyalar, innovatsiyalar va istiqbollarni batafsil tahlil qiling. "
        f"Matn ilmiy uslubda, uzluksiz, bir oqimda yozilsin. Paragraflar orasiga enter tashlamang.",
        max_words=2000
    )
    
    sections.append({
        'type': 'chapter2',
        'title': 'II BOB. AMALIY TAHLIL VA TADQIQOT',
        'subsections': [
            {'number': '2.1', 'title': 'Amaliy tahlil va holat tadqiqi', 'content': chapter2_section1},
            {'number': '2.2', 'title': 'Tendentsiyalar va rivojlanish yo\'nalishlari', 'content': chapter2_section2}
        ]
    })
    
    chapter3_section1 = await generate_section_with_ai(
        f"Kurs ishi III BOB ning 3.1-bandini yozing (4-5 bet, taxminan 1400-1600 so'z). "
        f"Fan: {subject}, Mavzu: {topic}. "
        f"3.1-band muammolarni yechish bo'yicha takliflar bo'lishi kerak. "
        f"Aniqlangan muammolarni bartaraf etish uchun aniq, amaliy takliflar bering. "
        f"Matn ilmiy uslubda, uzluksiz, bir oqimda yozilsin. Paragraflar orasiga enter tashlamang.",
        max_words=1600
    )
    
    chapter3_section2 = await generate_section_with_ai(
        f"Kurs ishi III BOB ning 3.2-bandini yozing (4-5 bet, taxminan 1400-1600 so'z). "
        f"Fan: {subject}, Mavzu: {topic}. "
        f"3.2-band takomillashtirish choralari va istiqbollari bo'lishi kerak. "
        f"Takliflarni amalga oshirish mexanizmlari, kutilayotgan natijalar va istiqbollarni batafsil yoritib bering. "
        f"Matn ilmiy uslubda, uzluksiz, bir oqimda yozilsin. Paragraflar orasiga enter tashlamang.",
        max_words=1600
    )
    
    sections.append({
        'type': 'chapter3',
        'title': 'III BOB. TAKOMILLASHTIRISH TAKLIFLARI VA YECHIMLAR',
        'subsections': [
            {'number': '3.1', 'title': 'Muammolarni yechish bo\'yicha takliflar', 'content': chapter3_section1},
            {'number': '3.2', 'title': 'Takomillashtirish choralari va istiqbollari', 'content': chapter3_section2}
        ]
    })
    
    conclusion_content = await generate_section_with_ai(
        f"Kurs ishi uchun XULOSA qismini yozing (3-4 bet, taxminan 1000-1200 so'z). "
        f"Fan: {subject}, Mavzu: {topic}. "
        f"XULOSA qismida:\n"
        f"1. Tadqiqotning asosiy natijalari va xulosalarini umumlashtiring\n"
        f"2. Har bir bobdan kelib chiqqan xulosalarni sanab o'ting\n"
        f"3. Amaliy takliflarning qisqacha xulosasini bering\n"
        f"4. Tadqiqotning ilmiy va amaliy ahamiyatini ta'kidlang\n\n"
        f"Matn ilmiy uslubda, uzluksiz, bir oqimda yozilsin. Paragraflar orasiga enter tashlamang.",
        max_words=1200
    )
    sections.append({'type': 'conclusion', 'content': conclusion_content})
    
    references_content = generate_references(subject)
    sections.append({'type': 'references', 'content': references_content})
    
    appendix_content = generate_appendix()
    sections.append({'type': 'appendix', 'content': appendix_content})
    
    return sections

async def generate_section_with_ai(prompt, max_words=2000):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "system",
                    "content": "Siz O'zbekiston oliygohlaridagi talabalar uchun kurs ishi yozuvchi sun'iy intellektsiz. "
                    "Matnni to'liq, ilmiy uslubda, batafsil va professional darajada yozing. "
                    "Matn bir oqimda, uzluksiz yozilishi kerak. Paragraflar orasiga qo'shimcha bo'shliq tashlamang. "
                    "Har bir gap mantiqiy ravishda keyingi gapga bog'lanishi kerak."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=int(max_words * 1.5)
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

def generate_references(subject):
    return """1. O'zbekiston Respublikasining Ta'lim to'g'risidagi Qonuni. – T.: 2020.
2. O'zbekiston Respublikasi Prezidentining Farmonlari va Qarorlari to'plami. – T.: 2020-2025.
3. Karimov I.A. Yuksak ma'naviyat – yengilmas kuch. – T.: Ma'naviyat, 2008.
4. Mirziyoyev Sh.M. Tanqidiy tahlil, qat'iy tartib-intizom va shaxsiy javobgarlik – har bir rahbar faoliyatining kundalik qoidasi bo'lishi kerak. – T.: O'zbekiston, 2017.
5. O'zbekiston milliy ensiklopediyasi. – T.: 2000-2006.
6. Internet manbalari: www.lex.uz, www.press-service.uz, www.ziyonet.uz
7. Maxsus adabiyotlar va ilmiy jurnallar."""

def generate_appendix():
    return """1-ILOVA

Jadval va diagrammalar

[Bu yerda tadqiqot natijalari bo'yicha jadvallar va grafiklar joylashtiriladi]

2-ILOVA

Qo'shimcha materiallar

[Bu yerda qo'shimcha hujjatlar va materiallar joylashtiriladi]"""

