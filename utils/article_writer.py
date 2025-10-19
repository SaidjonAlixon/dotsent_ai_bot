import os
import asyncio
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)


async def generate_article(user_data):
    """Ilmiy maqola yaratish"""
    topic = user_data['topic']
    subject = user_data.get('subject', 'Ilmiy tadqiqot')
    
    sections = []
    
    # 1. Sarlavha va muallif ma'lumotlari
    title_data = {
        'title': topic,
        'authors': user_data.get('authors', [])
    }
    sections.append({'type': 'title', 'content': title_data})
    
    # 2. Annotatsiya (3 tilda)
    annotations = await generate_annotations(topic, subject)
    sections.append({'type': 'annotations', 'content': annotations})
    
    # 3. Kirish
    intro_content = await generate_section_with_ai(
        f"Ilmiy maqola uchun KIRISH qismini yozing (1.5-2 bet, 500-700 so'z).\n"
        f"Mavzu: {topic}\n"
        f"Fan: {subject}\n\n"
        f"KIRISH qismida:\n"
        f"1. Mavzuning dolzarbligi va ahamiyatini yoritib bering\n"
        f"2. Muammoning qo'yilishi\n"
        f"3. Tadqiqot maqsadi\n"
        f"4. Ilmiy yangiligi\n\n"
        f"MUHIM: Matn uzluksiz, bitta oqimda yozilsin. Enter qo'ymang.\n"
        f"Faqat matnni yozing, 'KIRISH' deb sarlavha qo'ymang.",
        max_words=1000
    )
    sections.append({'type': 'kirish', 'content': intro_content})
    
    # 4. Tadqiqot uslublari
    methods_content = await generate_section_with_ai(
        f"Ilmiy maqola uchun TADQIQOT USLUBLARI qismini yozing (1-1.5 bet, 400-500 so'z).\n"
        f"Mavzu: {topic}\n"
        f"Fan: {subject}\n\n"
        f"Bu qismda:\n"
        f"1. Tadqiqot metodologiyasi\n"
        f"2. Ishlatilgan usullar\n"
        f"3. Ma'lumotlar to'plash va tahlil qilish usullari\n\n"
        f"MUHIM: Matn uzluksiz, bitta oqimda yozilsin. Enter qo'ymang.\n"
        f"Faqat matnni yozing, sarlavha qo'ymang.",
        max_words=800
    )
    sections.append({'type': 'methods', 'content': methods_content})
    
    # 5. Natijalar va muhokama
    results_content = await generate_section_with_ai(
        f"Ilmiy maqola uchun NATIJALAR VA MUHOKAMA qismini yozing (2-3 bet, 800-1000 so'z).\n"
        f"Mavzu: {topic}\n"
        f"Fan: {subject}\n\n"
        f"Bu qismda:\n"
        f"1. Tadqiqot natijalari\n"
        f"2. Olingan ma'lumotlar tahlili\n"
        f"3. Natijalarni muhokama qilish\n"
        f"4. Boshqa tadqiqotlar bilan taqqoslash\n\n"
        f"MUHIM: Matn uzluksiz, bitta oqimda yozilsin. Enter qo'ymang.\n"
        f"Faqat matnni yozing, sarlavha qo'ymang.",
        max_words=1500
    )
    sections.append({'type': 'results', 'content': results_content})
    
    # 6. Xulosa
    conclusion_content = await generate_section_with_ai(
        f"Ilmiy maqola uchun XULOSA qismini yozing (1 bet, 300-400 so'z).\n"
        f"Mavzu: {topic}\n"
        f"Fan: {subject}\n\n"
        f"XULOSA qismida:\n"
        f"1. Asosiy xulosalar\n"
        f"2. Amaliy tavsiyalar\n"
        f"3. Keyingi tadqiqotlar uchun yo'nalishlar\n\n"
        f"MUHIM: Matn uzluksiz, bitta oqimda yozilsin. Enter qo'ymang.\n"
        f"Faqat matnni yozing, sarlavha qo'ymang.",
        max_words=600
    )
    sections.append({'type': 'conclusion', 'content': conclusion_content})
    
    # 7. Adabiyotlar (APA format)
    references = await generate_references_apa(topic, subject)
    sections.append({'type': 'references', 'content': references})
    
    return sections


async def generate_annotations(topic, subject):
    """3 tilda annotatsiya yaratish"""
    annotations = {}
    
    # O'zbek tilida
    uz_annotation = await generate_section_with_ai(
        f"Ilmiy maqola uchun O'ZBEK TILIDA annotatsiya yozing.\n"
        f"Mavzu: {topic}\n"
        f"Fan: {subject}\n\n"
        f"Annotatsiya 40-50 so'zdan iborat bo'lishi kerak.\n"
        f"Kalit so'zlar: 5-8 ta (vergul bilan ajratilgan)\n\n"
        f"MUHIM: Faqat annotatsiya matnini yozing, 'ANNOTATSIYA' deb sarlavha qo'ymang.\n"
        f"Matn uzluksiz, bitta paragrafda yozilsin.\n\n"
        f"Format:\n"
        f"[Annotatsiya matni - 40-50 so'z]\n"
        f"Kalit so'zlar: [so'z1, so'z2, so'z3...]",
        max_words=80
    )
    annotations['uz'] = uz_annotation
    
    # Ingliz tilida
    en_annotation = await generate_section_with_ai(
        f"Write ABSTRACT in ENGLISH for scientific article.\n"
        f"Topic: {topic}\n"
        f"Subject: {subject}\n\n"
        f"Abstract should be 40-50 words.\n"
        f"Keywords: 5-8 words (comma separated)\n\n"
        f"IMPORTANT: Write only abstract text, do NOT write 'ABSTRACT' as title.\n"
        f"Text should be continuous, in one paragraph.\n\n"
        f"Format:\n"
        f"[Abstract text - 40-50 words]\n"
        f"Keywords: [word1, word2, word3...]",
        max_words=80
    )
    annotations['en'] = en_annotation
    
    # Rus tilida
    ru_annotation = await generate_section_with_ai(
        f"Напишите АННОТАЦИЮ на РУССКОМ ЯЗЫКЕ для научной статьи.\n"
        f"Тема: {topic}\n"
        f"Предмет: {subject}\n\n"
        f"Аннотация должна быть 40-50 слов.\n"
        f"Ключевые слова: 5-8 слов (через запятую)\n\n"
        f"ВАЖНО: Пишите только текст аннотации, НЕ пишите заголовок 'АННОТАЦИЯ'.\n"
        f"Текст должен быть непрерывным, одним абзацем.\n\n"
        f"Формат:\n"
        f"[Текст аннотации - 40-50 слов]\n"
        f"Ключевые слова: [слово1, слово2, слово3...]",
        max_words=80
    )
    annotations['ru'] = ru_annotation
    
    return annotations


async def generate_references_apa(topic, subject):
    """APA formatda adabiyotlar yaratish"""
    try:
        prompt = f"""Fan: {subject}
Mavzu: {topic}

Yuqoridagi mavzu bo'yicha ilmiy maqola uchun FOYDALANILGAN ADABIYOTLAR RO'YXATI tuzing.

APA (American Psychological Association) formatida yozing.

Adabiyotlar ro'yxati kamida 15-20 ta manbadan iborat bo'lishi kerak:
1. Kitoblar (5-7 ta)
2. Ilmiy jurnallar va maqolalar (7-10 ta)
3. Internet manbalari (3-5 ta)

APA format namunasi:
- Kitob: Author, A. A. (Year). Title of work. Publisher.
- Maqola: Author, A. A. (Year). Title of article. Journal Name, volume(issue), pages.
- Web: Author, A. A. (Year). Title. Site Name. URL

MUHIM:
- Faqat adabiyotlar ro'yxatini yozing
- Har bir manba mavzuga mos bo'lishi kerak
- Alifbo tartibida yozing (muallifning familiyasi bo'yicha)
- To'g'ri APA formatda yozing"""

        # OpenAI chaqiruvini alohida thread'da ishga tushirish
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Siz ilmiy maqola uchun APA formatida adabiyotlar ro'yxati tuzuvchisiz."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
        )
        
        references = response.choices[0].message.content.strip()
        return references
        
    except Exception as e:
        print(f"Adabiyotlar yaratishda xatolik: {e}")
        return """Author, A. A. (2020). Title of the book. Publisher.
Author, B. B. (2021). Title of article. Journal Name, 15(2), 123-145.
Author, C. C. (2022). Research methods. Academic Press."""


async def generate_section_with_ai(prompt, max_words=1000):
    """AI orqali maqola bo'limini yaratish"""
    try:
        # OpenAI chaqiruvini alohida thread'da ishga tushirish (blocking'dan qochish)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Siz ilmiy maqola yozuvchi sun'iy intellektsiz. "
                                   "Matnni ilmiy uslubda, professional darajada yozing. "
                                   "Matn uzluksiz, bir oqimda yozilishi kerak."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=int(max_words * 1.5),
                temperature=0.7
            )
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"AI xatolik: {e}")
        return f"[AI bilan bog'lanishda xatolik: {str(e)}]"
