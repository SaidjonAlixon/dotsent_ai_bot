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
            max_tokens=4000,
            timeout=120.0
        )
        
        content = response.choices[0].message.content or ""
        
        if not content or len(content) < 100:
            raise ValueError("AI javob juda qisqa yoki bo'sh")
        
        logger.info(f"Kurs ishi muvaffaqiyatli yaratildi: {topic}")
        return content
    
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
