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

# Namuna fayl havolalari
KURS_ISHI_SAMPLE_URL = os.getenv("KURS_ISHI_SAMPLE_URL", "https://t.me/example")
MAQOLA_SAMPLE_URL = os.getenv("MAQOLA_SAMPLE_URL", "https://t.me/example")

# Qo'llab-quvvatlash guruhi
SUPPORT_GROUP_URL = os.getenv("SUPPORT_GROUP_URL", "https://t.me/example")

# Majburiy obuna kanallari
REQUIRED_CHANNEL_1 = os.getenv("REQUIRED_CHANNEL_1", "")  # Kanal 1 ID (masalan: @channel1 yoki -1001234567890)
REQUIRED_CHANNEL_2 = os.getenv("REQUIRED_CHANNEL_2", "")  # Kanal 2 ID (masalan: @channel2 yoki -1009876543210)
