"""Toshkent vaqti bilan ishlash uchun utility funksiyalar"""
from datetime import datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo
    USE_ZONEINFO = True
except ImportError:
    # Python < 3.9 uchun
    try:
        from backports.zoneinfo import ZoneInfo
        USE_ZONEINFO = True
    except ImportError:
        USE_ZONEINFO = False
        # pytz fallback
        try:
            import pytz
            PYTZ_AVAILABLE = True
        except ImportError:
            PYTZ_AVAILABLE = False

def get_tashkent_time():
    """Toshkent vaqtini qaytaradi (UTC+5)"""
    try:
        if USE_ZONEINFO:
            return datetime.now(ZoneInfo("Asia/Tashkent"))
        elif PYTZ_AVAILABLE:
            import pytz
            tashkent_tz = pytz.timezone('Asia/Tashkent')
            return datetime.now(tashkent_tz)
        else:
            # Fallback - UTC+5 manual qo'shish
            return datetime.now(timezone(timedelta(hours=5)))
    except Exception as e:
        # Eng oxirgi fallback - oddiy UTC+5 qo'shish
        return datetime.now(timezone(timedelta(hours=5)))

def format_datetime_tashkent(format_str='%Y-%m-%d %H:%M'):
    """Toshkent vaqtini formatlab qaytaradi"""
    return get_tashkent_time().strftime(format_str)

