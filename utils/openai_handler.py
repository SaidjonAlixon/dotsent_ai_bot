import openai
import logging
from config import OPENAI_API_KEY, KURS_ISH_PROMPT, MAQOLA_PROMPT

logger = logging.getLogger(__name__)

openai.api_key = OPENAI_API_KEY

async def generate_kurs_ishi(topic: str) -> str:
    """OpenAI orqali kurs ishi yaratish"""
    try:
        prompt = KURS_ISH_PROMPT.format(topic=topic)
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Siz professional akademik yozuvchi siz."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        content = response.choices[0].message.content or ""
        logger.info(f"Kurs ishi muvaffaqiyatli yaratildi: {topic}")
        return content
    
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
            max_tokens=4000
        )
        
        content = response.choices[0].message.content or ""
        logger.info(f"Maqola muvaffaqiyatli yaratildi: {topic}")
        return content
    
    except Exception as e:
        logger.error(f"Maqola yaratishda xatolik: {e}")
        raise
