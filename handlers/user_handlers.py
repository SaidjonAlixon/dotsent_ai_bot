from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import logging
import asyncio
import os

from database import Database
from keyboards import (get_main_menu, get_cancel_button, get_balance_buttons, 
                        get_service_info_buttons, get_payment_amount_buttons, get_support_buttons,
                        get_subscription_keyboard)
from utils.course_writer import generate_course_work
from utils.document_generator import create_word_document
from utils.article_writer import generate_article
from utils.article_document_generator import create_article_document
import config

logger = logging.getLogger(__name__)

router = Router()
db = Database()

# Majburiy obuna tekshirish funksiyasi
async def check_subscription(bot, user_id: int, channel_id: str) -> bool:
    """Foydalanuvchi kanalga obuna bo'lganligini tekshirish"""
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        # Obuna holatlari: creator, administrator, member
        return member.status in ['creator', 'administrator', 'member']
    except Exception as e:
        logger.error(f"Obuna tekshirishda xatolik: {e}")
        return False

# Background task yaratish uchun
async def process_course_work_background(bot, telegram_id, user_data_for_ai, price, data):
    """Background da kurs ishini yaratish"""
    try:
        sections = await generate_course_work(user_data_for_ai)
        
        filename = f"kurs_ishi_{telegram_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        os.makedirs('generated_files', exist_ok=True)
        docx_path = os.path.join('generated_files', filename)
        
        create_word_document(sections, user_data_for_ai, docx_path)
        
        db.update_balance(telegram_id, -price)
        
        document_file = FSInputFile(docx_path)
        
        if config.KURS_ISHLARI_CHANNEL_ID:
            channel_message = await bot.send_document(
                chat_id=config.KURS_ISHLARI_CHANNEL_ID,
                document=document_file,
                caption=f"""🧾 Kurs ishi tayyorlandi

👤 F.I.Sh: {data['fish']}
🆔 ID: {telegram_id}
🏫 O'quv yurti: {data['university']}
📖 Fan: {data['subject']}
📚 Mavzu: {data['topic']}
🎓 Kurs: {user_data_for_ai['course']}
💰 Narx: {price:,} so'm
🕒 Sana: {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
            )
            file_link = f"https://t.me/c/{str(config.KURS_ISHLARI_CHANNEL_ID)[4:]}/{channel_message.message_id}"
        else:
            file_link = docx_path
        
        document_file_user = FSInputFile(docx_path)
        
        info_text = (
            f"✅ Kurs ishingiz tayyor!\n\n"
            f"📚 Mavzu: {data['topic']}\n"
            f"💰 To'langan: {price:,} so'm\n\n"
            f"📝 **Fayl haqida:**\n"
            f"• Fayl Word (DOCX) formatda\n"
            f"• Kompyuterda Word orqali ochib o'zgartirish kiritishingiz mumkin\n"
            f"• PDF kerak bo'lsa, asosiy menyudagi '📄 Word → PDF' tugmasini ishlating"
        )
        
        await bot.send_document(
            chat_id=telegram_id,
            document=document_file_user,
            caption=info_text,
            parse_mode="Markdown",
            reply_markup=get_main_menu()
        )
        
        db.add_order(telegram_id, "kurs_ishi", data['topic'], price, file_link)
        
        # Faylni serverdan o'chirish (joy tejash uchun)
        try:
            os.remove(docx_path)
            logger.info(f"DOCX fayl o'chirildi: {docx_path}")
        except Exception as e:
            logger.error(f"Faylni o'chirishda xatolik: {e}")
        
        logger.info(f"Kurs ishi tayyor: {telegram_id}")
        
    except Exception as e:
        logger.error(f"Kurs ishi yaratishda xatolik: {e}")
        await bot.send_message(
            chat_id=telegram_id,
            text=f"❌ Kurs ishi tayyorlashda xatolik yuz berdi: {str(e)}\n\n"
                 "Balansingiz o'zgartirilmadi. Iltimos, keyinroq qayta urinib ko'ring.",
            reply_markup=get_main_menu()
        )

async def process_article_background(bot, telegram_id, user_data_for_ai, price, topic):
    """Background da maqolani yaratish"""
    try:
        sections = await generate_article(user_data_for_ai)
        
        filename = f"maqola_{telegram_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        os.makedirs('generated_files', exist_ok=True)
        filepath = os.path.join('generated_files', filename)
        
        create_article_document(sections, user_data_for_ai, filepath)
        
        db.update_balance(telegram_id, -price)
        
        document_file = FSInputFile(filepath)
        
        user = db.get_user(telegram_id)
        
        if config.MAQOLALAR_CHANNEL_ID:
            channel_message = await bot.send_document(
                chat_id=config.MAQOLALAR_CHANNEL_ID,
                document=document_file,
                caption=f"""📰 Maqola tayyorlandi

👤 Ismi: {user['full_name']}
🆔 ID: {telegram_id}
🔗 Username: @{user['username'] or 'mavjud emas'}
📝 Mavzu: {topic}
💰 Narx: {price:,} so'm
🕒 Sana: {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
            )
            file_link = f"https://t.me/c/{str(config.MAQOLALAR_CHANNEL_ID)[4:]}/{channel_message.message_id}"
        else:
            file_link = filepath
        
        document_file_user = FSInputFile(filepath)
        
        info_text = (
            f"✅ Maqolangiz tayyor!\n\n"
            f"📝 Mavzu: {topic}\n"
            f"💰 To'langan: {price:,} so'm\n\n"
            f"📝 **Fayl haqida:**\n"
            f"• Fayl Word (DOCX) formatda\n"
            f"• Kompyuterda Word orqali ochib o'zgartirish kiritishingiz mumkin\n"
            f"• PDF kerak bo'lsa, asosiy menyudagi '📄 Word → PDF' tugmasini ishlating"
        )
        
        await bot.send_document(
            chat_id=telegram_id,
            document=document_file_user,
            caption=info_text,
            parse_mode="Markdown",
            reply_markup=get_main_menu()
        )
        
        db.add_order(telegram_id, "maqola", topic, price, file_link)
        
        # Faylni serverdan o'chirish (joy tejash uchun)
        try:
            os.remove(filepath)
            logger.info(f"DOCX fayl o'chirildi: {filepath}")
        except Exception as e:
            logger.error(f"Faylni o'chirishda xatolik: {e}")
        
        logger.info(f"Maqola tayyor: {telegram_id}")
        
    except Exception as e:
        logger.error(f"Maqola yaratishda xatolik: {e}")
        await bot.send_message(
            chat_id=telegram_id,
            text="❌ Maqola tayyorlashda xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.\n\n"
                 "Balansingiz o'zgartirilmadi.",
            reply_markup=get_main_menu()
        )

class UserStates(StatesGroup):
    waiting_for_kurs_topic = State()
    waiting_for_kurs_fish = State()
    waiting_for_kurs_university = State()
    waiting_for_kurs_subject = State()
    waiting_for_kurs_course_number = State()
    waiting_for_maqola_topic = State()
    waiting_for_maqola_author_name = State()
    waiting_for_maqola_field_position = State()
    waiting_for_maqola_supervisor = State()
    waiting_for_payment_amount = State()
    waiting_for_payment_check = State()
    waiting_for_promocode = State()
    waiting_for_word_file = State()

@router.message(Command("start"))
async def cmd_start(message: Message, bot):
    """Start buyrug'i"""
    telegram_id = message.from_user.id
    username = message.from_user.username or ""
    full_name = message.from_user.full_name or "Foydalanuvchi"
    
    # Foydalanuvchi cheklangan yoki yo'qligini tekshirish
    if db.is_user_banned(telegram_id):
        await message.answer(
            "🚫 **Sizning botdan foydalanish huquqingiz yo'q.**\n\n"
            "Agar bu xato deb hisoblasangiz yoki huquqni qaytadan olish uchun "
            "qo'llab-quvvatlash guruhiga murojaat qiling:",
            reply_markup=get_support_buttons(config.SUPPORT_GROUP_URL),
            parse_mode="Markdown"
        )
        return
    
    # Majburiy obuna tekshirish (admin uchun emas)
    if telegram_id != config.ADMIN_ID and config.REQUIRED_CHANNEL_1 and config.REQUIRED_CHANNEL_2:
        # Ikkala kanalga ham obuna bo'lganligini tekshirish
        is_subscribed_1 = await check_subscription(bot, telegram_id, config.REQUIRED_CHANNEL_1)
        is_subscribed_2 = await check_subscription(bot, telegram_id, config.REQUIRED_CHANNEL_2)
        
        if not is_subscribed_1 or not is_subscribed_2:
            await message.answer(
                "🔔 <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:</b>\n\n"
                "Obuna bo'lgandan keyin <b>'✅ Obuna bo'ldim'</b> tugmasini bosing.",
                reply_markup=get_subscription_keyboard(config.REQUIRED_CHANNEL_1, config.REQUIRED_CHANNEL_2),
                parse_mode="HTML"
            )
            return
    
    args = message.text.split()
    invited_by = None
    
    if len(args) > 1 and args[1].startswith("REF"):
        try:
            invited_by = int(args[1].replace("REF", ""))
            referal_bonus = int(db.get_setting("referal_bonus", str(config.DEFAULT_REFERAL_BONUS)))
            db.update_balance(invited_by, referal_bonus)
        except:
            pass
    
    user = db.get_user(telegram_id)
    
    if not user:
        db.add_user(telegram_id, username, full_name, invited_by)
        welcome_text = f"""🎉 Xush kelibsiz, {full_name}!

Men sizga kurs ishi va maqola tayyorlashda yordam beraman.

🔹 Kurs ishi yozish - akademik kurs ishi tayyorlash
🔹 Maqola yozish - ilmiy maqola tayyorlash
🔹 Balansim - hisobingizni to'ldirish va ko'rish
🔹 Pul ishlash - referal orqali bonus olish
🔹 Profil - shaxsiy ma'lumotlaringiz
🔹 Promokodlarim - chegirmalardan foydalanish

Boshlash uchun quyidagi tugmalardan birini tanlang! 👇"""
    else:
        # Foydalanuvchi mavjud bo'lsa, ma'lumotlarini yangilash
        db.update_user_info(telegram_id, username, full_name)
        welcome_text = f"Qaytganingizdan xursandmiz, {full_name}! 😊\n\nQuyidagi tugmalardan birini tanlang:"
    
    await message.answer(welcome_text, reply_markup=get_main_menu())

@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery, bot):
    """'Obuna bo'ldim' tugmasi bosilganda tekshirish"""
    telegram_id = callback.from_user.id
    full_name = callback.from_user.full_name or "Foydalanuvchi"
    
    # Agar kanal ID lari mavjud bo'lsa tekshiramiz
    if not config.REQUIRED_CHANNEL_1 or not config.REQUIRED_CHANNEL_2:
        await callback.answer("⚠️ Majburiy obuna o'rnatilmagan.", show_alert=True)
        return
    
    # Ikkala kanalga ham obuna bo'lganligini tekshirish
    is_subscribed_1 = await check_subscription(bot, telegram_id, config.REQUIRED_CHANNEL_1)
    is_subscribed_2 = await check_subscription(bot, telegram_id, config.REQUIRED_CHANNEL_2)
    
    if is_subscribed_1 and is_subscribed_2:
        # Obuna bo'lgan - asosiy menyuni ko'rsatish
        await callback.message.edit_text(
            f"✅ <b>Obuna tasdiqlandi!</b>\n\n"
            f"Xush kelibsiz, {full_name}! 🎉\n\n"
            f"Endi botdan to'liq foydalanishingiz mumkin.",
            parse_mode="HTML"
        )
        await callback.message.answer(
            "📋 Quyidagi xizmatlardan birini tanlang:",
            reply_markup=get_main_menu()
        )
        await callback.answer()
    else:
        # Hali ham obuna bo'lmagan
        not_subscribed = []
        if not is_subscribed_1:
            not_subscribed.append("1-kanal")
        if not is_subscribed_2:
            not_subscribed.append("2-kanal")
        
        await callback.answer(
            f"❌ Siz {', '.join(not_subscribed)}ga obuna bo'lmadingiz!\n\n"
            f"Iltimos, barcha kanallarga obuna bo'ling va qayta urinib ko'ring.",
            show_alert=True
        )

@router.message(F.text == "🧾 Kurs ishi yozish")
async def kurs_ishi_handler(message: Message, state: FSMContext):
    """Kurs ishi yozish - narx va ma'lumot"""
    kurs_ishi_price = int(db.get_setting("kurs_ishi_price", "50000"))
    
    info_text = (
        "🧾 **Kurs ishi yozish**\n\n"
        "📊 **Xizmat haqida:**\n"
        "• Professional akademik kurs ishi\n"
        "• Barcha oliygohlar talablariga mos\n"
        "• O'zbekiston standartlariga mos\n"
        "• Titul, Mundareja, Mundarija, Ilovalar\n"
        "• Times New Roman 14pt, 1.5 interval\n\n"
        f"💰 **Narx:** {kurs_ishi_price:,} so'm\n\n"
        "⏱ **Tayyor bo'lish muddati:** 5-10 daqiqa\n\n"
        "📄 Namunani ko'rish uchun tugmani bosing. Ma'qul bo'lsa ✅Roziman tugmasini bosing va kurs ishingiz tayyorlanish boshlanadi!"
    )
    
    await message.answer(
        info_text,
        reply_markup=get_service_info_buttons("kurs", config.KURS_ISHI_SAMPLE_URL),
        parse_mode="Markdown"
    )

@router.message(UserStates.waiting_for_kurs_fish)
async def process_kurs_fish(message: Message, state: FSMContext):
    """F.I.Sh qabul qilish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_menu())
        return
    
    await state.update_data(fish=message.text)
    await message.answer(
        "🏫 O'quv yurti nomini kiriting:\n\n"
        "Masalan: Toshkent Davlat Texnika Universiteti",
        reply_markup=get_cancel_button()
    )
    await state.set_state(UserStates.waiting_for_kurs_university)

@router.message(UserStates.waiting_for_kurs_university)
async def process_kurs_university(message: Message, state: FSMContext):
    """O'quv yurti nomini qabul qilish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_menu())
        return
    
    await state.update_data(university=message.text)
    await message.answer(
        "📖 Fan nomini kiriting:\n\n"
        "Masalan: Axborot texnologiyalari",
        reply_markup=get_cancel_button()
    )
    await state.set_state(UserStates.waiting_for_kurs_subject)

@router.message(UserStates.waiting_for_kurs_subject)
async def process_kurs_subject(message: Message, state: FSMContext):
    """Fan nomini qabul qilish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_menu())
        return
    
    await state.update_data(subject=message.text)
    await message.answer(
        "📚 Kurs ishi mavzusini kiriting:\n\n"
        "Masalan: Sun'iy intellektning iqtisodiy rivojlanishga ta'siri",
        reply_markup=get_cancel_button()
    )
    await state.set_state(UserStates.waiting_for_kurs_topic)

@router.message(UserStates.waiting_for_kurs_topic)
async def process_kurs_topic(message: Message, state: FSMContext):
    """Mavzuni qabul qilish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_menu())
        return
    
    await state.update_data(topic=message.text)
    await message.answer(
        "🎓 Kurs raqamini kiriting (1, 2, 3 yoki 4):\n\n"
        "Masalan: 3",
        reply_markup=get_cancel_button()
    )
    await state.set_state(UserStates.waiting_for_kurs_course_number)

@router.message(UserStates.waiting_for_kurs_course_number)
async def process_kurs_course_number(message: Message, state: FSMContext, bot):
    """Kurs raqamini qabul qilish va ishni yaratish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_menu())
        return
    
    try:
        course_number = int(message.text)
        if course_number not in [1, 2, 3, 4]:
            await message.answer("❌ Kurs raqami 1, 2, 3 yoki 4 bo'lishi kerak.")
            return
    except ValueError:
        await message.answer("❌ Iltimos, faqat raqam kiriting (1, 2, 3 yoki 4).")
        return
    
    await state.update_data(course_number=course_number)
    
    telegram_id = message.from_user.id
    user = db.get_user(telegram_id)
    
    if not user:
        await message.answer("❌ Foydalanuvchi topilmadi. /start buyrug'ini yuboring.", reply_markup=get_main_menu())
        await state.clear()
        return
    
    # State'dan promokod ma'lumotlarini olish (agar "Roziman" bosilganda qo'shilgan bo'lsa)
    data = await state.get_data()
    original_price = data.get('original_price')
    discount_amount = data.get('discount_amount', 0)
    promocode_used = data.get('promocode_used')
    final_price = data.get('final_price')  # State'dan yakuniy narxni olish
    
    # Agar state'da promokod ma'lumotlari yo'q bo'lsa, user'dan tekshirish
    if original_price is None:
        price = int(db.get_setting("kurs_ishi_price", str(config.DEFAULT_KURS_ISH_PRICE)))
        original_price = price
        discount_amount = 0
        promocode_used = None
        
        # Foydalanuvchining aktiv promokodini tekshirish
        if user.get('active_promocode'):
            promocode = db.get_promocode(user['active_promocode'])
            if promocode and promocode['work_type'] == 'kurs_ishi':
                # Promokodni yana bir bor tekshirish (ishlatish mumkinligini)
                can_use, _ = db.can_use_promocode(user['active_promocode'], telegram_id)
                if can_use:
                    discount_percent = promocode['discount_percent']
                    discount_amount = int(price * discount_percent / 100)
                    price = price - discount_amount
                    promocode_used = user['active_promocode']
    else:
        # State'dan olingan narx (chegirma bilan)
        # Agar final_price saqlangan bo'lsa, uni ishlatamiz, aks holda hisoblaymiz
        if final_price is not None:
            price = final_price
        else:
            price = original_price - discount_amount
    
    if user["balance"] < price:
        discount_text = ""
        if discount_amount > 0:
            promocode_temp = db.get_promocode(promocode_used) if promocode_used else None
            if promocode_temp:
                discount_text = f"💰 Chegirma qo'llandi!\n💵 Asl narx: {original_price:,} so'm\n🎁 Chegirma: {discount_amount:,} so'm ({promocode_temp.get('discount_percent')}%)\n\n"
        
        await message.answer(
            f"❌ Balansingizda mablag' yetarli emas!\n\n"
            f"Kerakli summa: {price:,} so'm\n"
            f"{discount_text}"
            f"Sizning balansingiz: {user['balance']:,} so'm\n\n"
            f"Iltimos, avval balansni to'ldiring.",
            reply_markup=get_main_menu()
        )
        await state.clear()
        return
    
    data = await state.get_data()
    
    price_info = f"💰 Narx: {price:,} so'm"
    if discount_amount > 0:
        promocode_temp = db.get_promocode(promocode_used) if promocode_used else None
        if promocode_temp:
            price_info = f"💰 Narx: {price:,} so'm\n💵 Asl narx: {original_price:,} so'm\n🎁 Chegirma: {discount_amount:,} so'm ({promocode_temp['discount_percent']}%)"
    
    await message.answer(
        f"✅ Ma'lumotlar qabul qilindi!\n\n"
        f"👤 F.I.Sh: {data['fish']}\n"
        f"🏫 O'quv yurti: {data['university']}\n"
        f"📖 Fan: {data['subject']}\n"
        f"📚 Mavzu: {data['topic']}\n"
        f"🎓 Kurs: {course_number}\n"
        f"{price_info}\n\n"
        f"⏳ Kurs ishingiz tayyorlanmoqda...\n"
        f"📲 Tayyor bo'lgach sizga yuboriladi (10-15 daqiqa)\n\n"
        f"Shu vaqt ichida botning boshqa funksiyalaridan foydalanishingiz mumkin!",
        reply_markup=get_main_menu()
    )
    
    user_data_for_ai = {
        'name': data['fish'],
        'university': data['university'],
        'subject': data['subject'],
        'topic': data['topic'],
        'course': course_number
    }
    
    # Promokodni ishlatilgan deb belgilash
    if promocode_used:
        promocode = db.get_promocode(promocode_used)
        usage_type = promocode.get('usage_type', 'unlimited')
        
        if usage_type == "one_time":
            # 1 martalik - buyurtma yaratilganda o'chiriladi
            db.mark_promocode_as_used(promocode['id'], telegram_id)
            db.deactivate_promocode(promocode['id'])
        elif usage_type == "per_user":
            # Har bir foydalanuvchi 1 marta
            db.mark_promocode_as_used(promocode['id'], telegram_id)
        
        # Foydalanuvchining aktiv promokodini o'chirish
        db.clear_user_promocode(telegram_id)
    
    # Background task yaratish
    asyncio.create_task(
        process_course_work_background(bot, telegram_id, user_data_for_ai, price, data)
    )
    
    await state.clear()

@router.message(F.text == "📰 Maqola yozish")
async def maqola_handler(message: Message, state: FSMContext):
    """Maqola yozish - narx va ma'lumot"""
    maqola_price = int(db.get_setting("maqola_price", "30000"))
    
    info_text = (
        "📰 **Ilmiy maqola yozish**\n\n"
        "📊 **Xizmat haqida:**\n"
        "• Professional ilmiy maqola barcha talablarga mos\n"
        "• 7-10 sahifa\n"
        "• Annotatsiya (3 tilda: O'zbek, Ingliz, Rus)\n"
        "• Kalit so'zlar, Adabiyotlar (APA format)\n"
        "• Times New Roman 14pt, 1.5 interval\n\n"
        f"💰 **Narx:** {maqola_price:,} so'm\n\n"
        "⏱ **Tayyor bo'lish muddati:** 5-10 daqiqa\n\n"
        "📄 Namunani ko'rish uchun tugmani bosing. Ma'qul bo'lsa ✅Roziman tugmasini bosing va maqolangizni yaratish boshlanadi!"
    )
    
    await message.answer(
        info_text,
        reply_markup=get_service_info_buttons("maqola", config.MAQOLA_SAMPLE_URL),
        parse_mode="Markdown"
    )

@router.message(UserStates.waiting_for_maqola_topic)
async def process_maqola_topic(message: Message, state: FSMContext):
    """Maqola mavzusini qabul qilish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_menu())
        return
    
    await state.update_data(topic=message.text)
    await message.answer(
        "👤 Ism va familiyangizni kiriting:\n\n"
        "Masalan: Akmal Abdullayev",
        reply_markup=get_cancel_button()
    )
    await state.set_state(UserStates.waiting_for_maqola_author_name)

@router.message(UserStates.waiting_for_maqola_author_name)
async def process_maqola_author_name(message: Message, state: FSMContext):
    """Muallif ismini qabul qilish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_menu())
        return
    
    await state.update_data(author_name=message.text)
    await message.answer(
        "📚 Sohangiz va lavozimingizni kiriting:\n\n"
        "Masalan: Matematika, Katta o'qituvchi",
        reply_markup=get_cancel_button()
    )
    await state.set_state(UserStates.waiting_for_maqola_field_position)

@router.message(UserStates.waiting_for_maqola_field_position)
async def process_maqola_field_position(message: Message, state: FSMContext):
    """Soha va lavozimni qabul qilish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_menu())
        return
    
    await state.update_data(field_position=message.text)
    
    from keyboards import get_skip_button
    await message.answer(
        "👨‍🏫 Siz bilan ishlaydigan ustoz ism va familiyasini kiriting:\n\n"
        "Masalan: Rustam Karimov\n\n"
        "Agar ustozingiz bo'lmasa, 'O'tkazib yuborish' tugmasini bosing.",
        reply_markup=get_skip_button()
    )
    await state.set_state(UserStates.waiting_for_maqola_supervisor)

@router.message(UserStates.waiting_for_maqola_supervisor)
async def process_maqola_supervisor(message: Message, state: FSMContext, bot):
    """Ustoz ma'lumotini qabul qilish va maqolani yaratish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_menu())
        return
    
    telegram_id = message.from_user.id
    user = db.get_user(telegram_id)
    
    if not user:
        await message.answer("❌ Foydalanuvchi topilmadi. /start buyrug'ini yuboring.", reply_markup=get_main_menu())
        await state.clear()
        return
    
    # State'dan promokod ma'lumotlarini olish (agar "Roziman" bosilganda qo'shilgan bo'lsa)
    state_data = await state.get_data()
    original_price = state_data.get('original_price')
    discount_amount = state_data.get('discount_amount', 0)
    promocode_used = state_data.get('promocode_used')
    final_price = state_data.get('final_price')  # State'dan yakuniy narxni olish
    
    # Agar state'da promokod ma'lumotlari yo'q bo'lsa, user'dan tekshirish
    if original_price is None:
        price = int(db.get_setting("maqola_price", str(config.DEFAULT_MAQOLA_PRICE)))
        original_price = price
        discount_amount = 0
        promocode_used = None
        
        # Foydalanuvchining aktiv promokodini tekshirish
        if user.get('active_promocode'):
            promocode = db.get_promocode(user['active_promocode'])
            if promocode and promocode['work_type'] == 'maqola':
                # Promokodni yana bir bor tekshirish (ishlatish mumkinligini)
                can_use, _ = db.can_use_promocode(user['active_promocode'], telegram_id)
                if can_use:
                    discount_percent = promocode['discount_percent']
                    discount_amount = int(price * discount_percent / 100)
                    price = price - discount_amount
                    promocode_used = user['active_promocode']
    else:
        # State'dan olingan narx (chegirma bilan)
        # Agar final_price saqlangan bo'lsa, uni ishlatamiz, aks holda hisoblaymiz
        if final_price is not None:
            price = final_price
        else:
            price = original_price - discount_amount
    
    if user["balance"] < price:
        discount_text = ""
        if discount_amount > 0:
            promocode_temp = db.get_promocode(promocode_used) if promocode_used else None
            if promocode_temp:
                discount_text = f"💰 Chegirma qo'llandi!\n💵 Asl narx: {original_price:,} so'm\n🎁 Chegirma: {discount_amount:,} so'm ({promocode_temp.get('discount_percent')}%)\n\n"
        
        await message.answer(
            f"❌ Balansingizda mablag' yetarli emas!\n\n"
            f"Kerakli summa: {price:,} so'm\n"
            f"{discount_text}"
            f"Sizning balansingiz: {user['balance']:,} so'm\n\n"
            f"Iltimos, avval balansni to'ldiring.",
            reply_markup=get_main_menu()
        )
        await state.clear()
        return
    
    data = await state.get_data()
    
    # Ustozni saqlash (yoki bo'sh qoldirish)
    supervisor = None if message.text == "⏭ O'tkazib yuborish" else message.text
    await state.update_data(supervisor=supervisor)
    
    data = await state.get_data()
    topic = data['topic']
    author_name = data['author_name']
    field_position = data['field_position']
    
    # Ma'lumotlarni ko'rsatish
    confirmation_text = f"✅ Ma'lumotlar qabul qilindi!\n\n"
    confirmation_text += f"📝 Mavzu: {topic}\n"
    confirmation_text += f"👤 Muallif: {author_name}\n"
    confirmation_text += f"📚 Soha va lavozim: {field_position}\n"
    if supervisor:
        confirmation_text += f"👨‍🏫 Ustoz: {supervisor}\n"
    
    price_info = f"💰 Narx: {price:,} so'm"
    if discount_amount > 0:
        promocode_temp = db.get_promocode(promocode_used) if promocode_used else None
        if promocode_temp:
            price_info = f"💰 Narx: {price:,} so'm\n💵 Asl narx: {original_price:,} so'm\n🎁 Chegirma: {discount_amount:,} so'm ({promocode_temp['discount_percent']}%)"
    
    confirmation_text += f"\n{price_info}\n"
    confirmation_text += f"\n⏳ Maqolangiz tayyorlanmoqda...\n"
    confirmation_text += f"📲 Tayyor bo'lgach sizga yuboriladi (2-3 daqiqa)\n\n"
    confirmation_text += f"Shu vaqt ichida botning boshqa funksiyalaridan foydalanishingiz mumkin!"
    
    await message.answer(confirmation_text, reply_markup=get_main_menu())
    
    # Mualliflar ro'yxatini yaratish
    authors = [{
        'name': author_name,
        'affiliation': field_position
    }]
    
    # Agar ustoz bo'lsa, qo'shish
    if supervisor:
        authors.append({
            'name': supervisor,
            'affiliation': 'Ilmiy rahbar'
        })
    
    user_data_for_ai = {
        'topic': topic,
        'subject': field_position.split(',')[0] if ',' in field_position else field_position,
        'authors': authors
    }
    
    # Promokodni ishlatilgan deb belgilash
    if promocode_used:
        promocode = db.get_promocode(promocode_used)
        usage_type = promocode.get('usage_type', 'unlimited')
        
        if usage_type == "one_time":
            # 1 martalik - buyurtma yaratilganda o'chiriladi
            db.mark_promocode_as_used(promocode['id'], telegram_id)
            db.deactivate_promocode(promocode['id'])
        elif usage_type == "per_user":
            # Har bir foydalanuvchi 1 marta
            db.mark_promocode_as_used(promocode['id'], telegram_id)
        
        # Foydalanuvchining aktiv promokodini o'chirish
        db.clear_user_promocode(telegram_id)
    
    # Background task yaratish
    asyncio.create_task(
        process_article_background(bot, telegram_id, user_data_for_ai, price, topic)
    )
    
    await state.clear()

@router.message(F.text == "💰 Balansim")
async def balance_handler(message: Message):
    """Balans ko'rsatish"""
    telegram_id = message.from_user.id
    user = db.get_user(telegram_id)
    
    if not user:
        await message.answer("❌ Foydalanuvchi topilmadi. /start buyrug'ini yuboring.", reply_markup=get_main_menu())
        return
    
    await message.answer(
        f"💰 Sizning balansingiz: {user['balance']:,} so'm\n\n"
        f"Balansni to'ldirish uchun quyidagi tugmani bosing:",
        reply_markup=get_balance_buttons()
    )

@router.callback_query(F.data == "add_balance")
async def add_balance_callback(callback: CallbackQuery, state: FSMContext):
    """Balans to'ldirish"""
    await callback.message.answer(
        "💵 To'ldirmoqchi bo'lgan summani kiriting (so'mda):\n\n"
        "Masalan: 50000",
        reply_markup=get_cancel_button()
    )
    await state.set_state(UserStates.waiting_for_payment_amount)
    await callback.answer()

@router.message(UserStates.waiting_for_payment_amount)
async def process_payment_amount(message: Message, state: FSMContext):
    """To'lov summasini qabul qilish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_menu())
        return
    
    try:
        amount = int(message.text.replace(",", "").replace(" ", ""))
        if amount < 1000:
            await message.answer("❌ Minimal summa 1,000 so'm bo'lishi kerak.")
            return
        
        await state.update_data(payment_amount=amount)
        await message.answer(
            f"💰 <b>To'lov summasi: {amount:,} so'm</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📱 <b>Quyidagi kartalardan biriga to'lov qiling:</b>\n\n"
            f"🔹 <code>5614 6821 2364 5204</code>\n"
            f"   💳 Uzcard\n\n"
            f"🔹 <code>9860 2301 0130 5897</code>\n"
            f"   💳 Humo\n\n"
            f"🔹 <code>4067 0700 0846 9202</code>\n"
            f"   💳 VISA\n\n"
            f"👤 <i>Ataullayev Saidmuhammadalixon</i>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📸 <b>To'lov chekini (screenshot) yuboring</b>\n\n"
            f"⚠️ <i>Chek haqiqiy bo'lishi kerak!\n"
            f"Admin tekshirib, hisobingizni to'ldiradi.</i>",
            reply_markup=get_cancel_button(),
            parse_mode="HTML"
        )
        await state.set_state(UserStates.waiting_for_payment_check)
    
    except ValueError:
        await message.answer("❌ Iltimos, faqat raqam kiriting.")

@router.message(UserStates.waiting_for_payment_check)
async def process_payment_check(message: Message, state: FSMContext, bot):
    """To'lov chekini qabul qilish"""
    # Bekor qilish tugmasi
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_menu())
        return
    
    # Rasm bo'lmagan xabarlar uchun ogohlantirish
    if not message.photo:
        await message.answer(
            "⚠️ Iltimos, faqat chek rasmini yuboring!\n\n"
            "📸 To'lov chekini (screenshot) yuborishingiz kerak.\n"
            "Boshqa turdagi xabarlar qabul qilinmaydi.",
            reply_markup=get_cancel_button()
        )
        return
    
    # Rasm qabul qilish
    data = await state.get_data()
    amount = data.get("payment_amount")
    
    if not amount:
        await message.answer("❌ To'lov summasi topilmadi. Iltimos, qaytadan boshlang.", reply_markup=get_main_menu())
        await state.clear()
        return
    
    telegram_id = message.from_user.id
    user = db.get_user(telegram_id)
    
    if not user:
        await message.answer("❌ Foydalanuvchi topilmadi. /start buyrug'ini yuboring.", reply_markup=get_main_menu())
        await state.clear()
        return
    
    photo = message.photo[-1]
    file_link = photo.file_id
    
    payment_id = db.add_payment(telegram_id, amount, file_link)
    
    if config.TOLOV_TASDIQLASH_CHANNEL_ID:
        from keyboards import get_payment_confirmation
        
        await bot.send_photo(
            chat_id=config.TOLOV_TASDIQLASH_CHANNEL_ID,
            photo=photo.file_id,
            caption=f"""💳 To'lov tasdiqlash

👤 Ismi: {user['full_name']}
🆔 ID: {telegram_id}
🔗 Username: @{user['username'] or 'mavjud emas'}
💰 Summa: {amount:,} so'm
🆔 To'lov ID: {payment_id}
🕒 Sana: {datetime.now().strftime('%Y-%m-%d %H:%M')}""",
            reply_markup=get_payment_confirmation(payment_id)
        )
    
    await message.answer(
        "✅ To'lov chekingiz qabul qilindi!\n\n"
        "Admin tekshirgandan so'ng balansingiz yangilanadi.\n"
        "Bu odatda 5-30 daqiqa vaqt oladi.",
        reply_markup=get_main_menu()
    )
    
    await state.clear()

@router.message(F.text == "💵 Pul ishlash")
async def referal_handler(message: Message):
    """Referal tizimi"""
    telegram_id = message.from_user.id
    user = db.get_user(telegram_id)
    
    if not user:
        await message.answer("❌ Foydalanuvchi topilmadi. /start buyrug'ini yuboring.", reply_markup=get_main_menu())
        return
    
    referal_count = db.get_referal_count(telegram_id)
    referal_bonus = int(db.get_setting("referal_bonus", str(config.DEFAULT_REFERAL_BONUS)))
    
    bot_username = (await message.bot.get_me()).username
    referal_link = f"https://t.me/{bot_username}?start={user['referal_code']}"
    
    await message.answer(
        f"💵 Referal tizimi\n\n"
        f"🔗 Sizning referal havolangiz:\n{referal_link}\n\n"
        f"👥 Taklif qilganlar soni: {referal_count} ta\n"
        f"💰 Har bir referal uchun: {referal_bonus:,} so'm\n\n"
        f"📊 Jami ishlab topganingiz: {referal_count * referal_bonus:,} so'm\n\n"
        f"Havolani do'stlaringizga ulashing va pul ishlang! 🎉"
    )

@router.message(F.text == "👤 Profil")
async def profile_handler(message: Message):
    """Profil ko'rsatish"""
    telegram_id = message.from_user.id
    user = db.get_user(telegram_id)
    
    if not user:
        await message.answer("❌ Foydalanuvchi topilmadi. /start buyrug'ini yuboring.", reply_markup=get_main_menu())
        return
    
    referal_count = db.get_referal_count(telegram_id)
    
    await message.answer(
        f"👤 Profil ma'lumotlari\n\n"
        f"🆔 ID: {telegram_id}\n"
        f"👤 Ism: {user['full_name']}\n"
        f"🔗 Username: @{user['username'] or 'mavjud emas'}\n"
        f"💰 Balans: {user['balance']:,} so'm\n"
        f"👥 Referal soni: {referal_count} ta\n"
        f"📅 Ro'yxatdan o'tgan: {user['register_date']}"
    )

@router.message(F.text == "🎁 Promokodlarim")
async def promocode_handler(message: Message, state: FSMContext):
    """Promokodlarim - aktiv promokodni ko'rsatish va yangi promokod kiritish"""
    telegram_id = message.from_user.id
    user = db.get_user(telegram_id)
    
    if not user:
        await message.answer("❌ Foydalanuvchi topilmadi. /start buyrug'ini yuboring.", reply_markup=get_main_menu())
        return
    
    # Aktiv promokodni ko'rsatish
    active_promocode_text = ""
    if user.get('active_promocode'):
        promocode = db.get_promocode(user['active_promocode'])
        if promocode:
            work_type_name = "Kurs ishi" if promocode['work_type'] == "kurs_ishi" else "Maqola"
            
            if promocode['usage_type'] == "one_time":
                usage_desc = "1 martalik (1 ta foydalanuvchi)"
            elif promocode['usage_type'] == "per_user":
                usage_desc = "Har bir foydalanuvchi 1 marta"
            else:
                usage_desc = "Cheksiz"
            
            active_promocode_text = (
                f"✅ **Aktiv promokod:**\n\n"
                f"🎁 Kod: `{promocode['code']}`\n"
                f"📝 Turi: {work_type_name}\n"
                f"💰 Chegirma: {promocode['discount_percent']}%\n"
                f"⏱ Foydalanish: {usage_desc}\n\n"
            )
        else:
            # Promokod topilmadi (o'chirilgan bo'lishi mumkin)
            db.clear_user_promocode(telegram_id)
    else:
        active_promocode_text = "ℹ️ Hozirda aktiv promokodingiz yo'q.\n\n"
    
    await message.answer(
        f"{active_promocode_text}"
        f"🎁 **Yangi promokod kiritish:**\n\n"
        f"Promokodni kiriting va chegirmaga ega bo'ling!",
        reply_markup=get_cancel_button(),
        parse_mode="Markdown"
    )
    await state.set_state(UserStates.waiting_for_promocode)

@router.message(UserStates.waiting_for_promocode)
async def process_promocode(message: Message, state: FSMContext):
    """Promokodni tekshirish va ishlatish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_menu())
        return
    
    code = message.text.strip().upper()
    user_id = message.from_user.id
    
    # Promokodni tekshirish
    can_use, message_text = db.can_use_promocode(code, user_id)
    
    if not can_use:
        await message.answer(message_text, reply_markup=get_main_menu())
        await state.clear()
        return
    
    # Promokod ma'lumotlarini olish
    promocode = db.get_promocode(code)
    
    # Promokodni foydalanuvchiga saqlash
    db.set_user_promocode(user_id, code)
    
    # Promokodni ishlatilgan deb belgilash (hozircha emas, buyurtma yaratilganda ishlatiladi)
    # Faqat 1 martalik promokodlar uchun darhol belgilash
    usage_type = promocode.get('usage_type', 'unlimited')
    
    if usage_type == "one_time":
        # 1 martalik - bir kishi ishlatgandan keyin o'chib ketadi
        db.mark_promocode_as_used(promocode['id'], user_id)
        # Promokodni darhol o'chirmaslik, buyurtma yaratilganda o'chiriladi
    elif usage_type == "per_user":
        # Har bir foydalanuvchi 1 marta - buyurtma yaratilganda belgilanadi
        pass
    # unlimited uchun hech narsa qilmaymiz
    
    work_type_name = "Kurs ishi" if promocode['work_type'] == "kurs_ishi" else "Maqola"
    
    await message.answer(
        f"{message_text}\n\n"
        f"🎁 Kod: {code}\n"
        f"📝 Turi: {work_type_name}\n"
        f"💰 Chegirma: {promocode['discount_percent']}%\n\n"
        f"Keyingi buyurtmangizda bu chegirma avtomatik qo'llaniladi!",
        reply_markup=get_main_menu()
    )
    
    await state.clear()


@router.callback_query(F.data.startswith("accept_service_"))
async def accept_service_callback(callback: CallbackQuery, state: FSMContext):
    """Xizmatni qabul qilish - balans tekshiruvi va promokod tekshiruvi"""
    service_type = callback.data.split("_")[-1]
    telegram_id = callback.from_user.id
    user = db.get_user(telegram_id)
    
    if service_type == "kurs":
        price = int(db.get_setting("kurs_ishi_price", "50000"))
        service_name = "Kurs ishi"
        work_type = "kurs_ishi"
    else:
        price = int(db.get_setting("maqola_price", "30000"))
        service_name = "Maqola"
        work_type = "maqola"
    
    original_price = price
    discount_amount = 0
    promocode_info = ""
    
    # Foydalanuvchining aktiv promokodini tekshirish
    if user.get('active_promocode'):
        promocode = db.get_promocode(user['active_promocode'])
        if promocode and promocode['work_type'] == work_type:
            # Promokodni yana bir bor tekshirish (ishlatish mumkinligini)
            can_use, _ = db.can_use_promocode(user['active_promocode'], telegram_id)
            if can_use:
                discount_percent = promocode['discount_percent']
                discount_amount = int(price * discount_percent / 100)
                price = price - discount_amount
                promocode_info = f"\n\n🎁 **Promokod qo'llandi!**\n💰 Asl narx: {original_price:,} so'm\n🎁 Chegirma: {discount_amount:,} so'm ({discount_percent}%)\n✅ Yakuniy narx: {price:,} so'm"
    
    # Balans tekshiruvi (chegirmadan keyingi narx bilan)
    if user['balance'] >= price:
        # Balans yetarli - FSM boshlash
        await callback.answer()
        if service_type == "kurs":
            await callback.message.answer(
                f"📚 Kurs ishi tayyorlash boshlandi!{promocode_info}\n\n"
                "👤 F.I.Sh. (to'liq ismingiz) kiriting:\n\n"
                "Masalan: Alisherov Alisher Alisherovich",
                reply_markup=get_cancel_button(),
                parse_mode="Markdown"
            )
            # Promokod ma'lumotlarini state'ga saqlash (har doim saqlash, chegirma bo'lsa ham bo'lmasa ham)
            await state.update_data(
                original_price=original_price, 
                discount_amount=discount_amount, 
                promocode_used=user.get('active_promocode') if discount_amount > 0 else None,
                final_price=price  # Yakuniy narxni ham saqlaymiz
            )
            await state.set_state(UserStates.waiting_for_kurs_fish)
        else:
            await callback.message.answer(
                f"📝 Maqola mavzusini kiriting:{promocode_info}\n\n"
                "Masalan: Raqamli iqtisodiyotda blockchain texnologiyasining o'rni",
                reply_markup=get_cancel_button(),
                parse_mode="Markdown"
            )
            # Promokod ma'lumotlarini state'ga saqlash (har doim saqlash, chegirma bo'lsa ham bo'lmasa ham)
            await state.update_data(
                original_price=original_price, 
                discount_amount=discount_amount, 
                promocode_used=user.get('active_promocode') if discount_amount > 0 else None,
                final_price=price  # Yakuniy narxni ham saqlaymiz
            )
            await state.set_state(UserStates.waiting_for_maqola_topic)
    else:
        # Balans yetarli emas
        needed = price - user['balance']
        await callback.answer()
        discount_text = ""
        if discount_amount > 0:
            discount_text = f"\n🎁 Promokod qo'llandi!\n💵 Asl narx: {original_price:,} so'm\n🎁 Chegirma: {discount_amount:,} so'm\n✅ Yakuniy narx: {price:,} so'm\n"
        await callback.message.answer(
            f"⚠️ **Balans yetarli emas!**\n\n"
            f"{discount_text}"
            f"💰 Hozirgi balans: {user['balance']:,} so'm\n"
            f"💵 Xizmat narxi: {price:,} so'm\n"
            f"❌ Yetmayapti: {needed:,} so'm\n\n"
            "📲 Iltimos, hisobingizni to'ldiring:",
            reply_markup=get_balance_buttons(),
            parse_mode="Markdown"
        )

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu_callback(callback: CallbackQuery):
    """Asosiy menyuga qaytish"""
    await callback.answer()
    await callback.message.answer(
        "Asosiy menyu:",
        reply_markup=get_main_menu()
    )

@router.callback_query(F.data.startswith("pdf:"))
async def convert_to_pdf_callback(callback: CallbackQuery):
    """DOCX faylni PDF ga o'tkazish"""
    await callback.answer("PDF yaratilmoqda, iltimos kuting...")
    
    try:
        # Filename olish
        filename = callback.data.split("pdf:", 1)[1]
        
        # To'liq yo'lni yaratish
        file_path = os.path.join('generated_files', filename)
        
        if not os.path.exists(file_path):
            await callback.message.answer(
                "❌ Fayl topilmadi yoki o'chirilgan. Iltimos, qayta kurs ishi/maqola yaratib, PDF qilishni darhol bosing."
            )
            return
        
        # PDF fayl nomi
        pdf_path = file_path.replace('.docx', '.pdf')
        
        # LibreOffice orqali PDF ga o'tkazish
        import subprocess
        
        output_dir = os.path.dirname(file_path)
        
        # LibreOffice CLI orqali konvertatsiya
        result = subprocess.run(
            ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', output_dir, file_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0 and os.path.exists(pdf_path):
            # PDF faylni yuborish
            pdf_file = FSInputFile(pdf_path)
            await callback.message.answer_document(
                document=pdf_file,
                caption="📄 PDF formatda tayyor!\n\nEndi telefoningizda ham muammosiz ochiladi."
            )
            
            # PDF faylni o'chirish (joy tejash uchun)
            try:
                os.remove(pdf_path)
            except:
                pass
        else:
            # Agar LibreOffice ishlamasa
            await callback.message.answer(
                "❌ PDF yaratishda xatolik yuz berdi.\n\n"
                "Iltimos, DOCX faylni kompyuteringizda Word orqali oching va "
                "\"Save As\" → \"PDF\" orqali PDF qiling."
            )
            logger.error(f"PDF conversion failed: {result.stderr}")
    
    except subprocess.TimeoutExpired:
        await callback.message.answer(
            "❌ PDF yaratish juda uzoq davom etdi.\n\n"
            "Iltimos, DOCX faylni kompyuteringizda PDF qiling."
        )
    except Exception as e:
        logger.error(f"PDF konvertatsiya xatoligi: {e}")
        await callback.message.answer(
            "❌ PDF yaratishda xatolik yuz berdi.\n\n"
            "Iltimos, DOCX faylni kompyuteringizda Word orqali oching va "
            "\"Save As\" → \"PDF\" orqali PDF qiling."
        )

@router.message(F.text == "📄 Word → PDF")
async def word_to_pdf_handler(message: Message, state: FSMContext):
    """Word faylni PDF ga o'tkazish"""
    await message.answer(
        "📄 <b>Word → PDF konvertatsiya</b>\n\n"
        "📎 Iltimos, Word (.docx) faylni yuboring.\n\n"
        "📝 <i>Fayl yuborilgandan so'ng avtomatik ravishda PDF formatga o'tkaziladi.</i>",
        reply_markup=get_cancel_button(),
        parse_mode="HTML"
    )
    await state.set_state(UserStates.waiting_for_word_file)

@router.message(UserStates.waiting_for_word_file)
async def process_word_file_for_pdf(message: Message, state: FSMContext, bot):
    """Word faylni qabul qilib PDF qilish yoki bekor qilish"""
    # Bekor qilish tugmasi
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_menu())
        return
    
    # Faqat document'larni qabul qilish
    if not message.document:
        await message.answer(
            "❌ Iltimos, Word (.docx) fayl yuboring.\n\n"
            "📎 Faylni yuborish uchun pastdagi 📎 tugmasini bosing.",
            reply_markup=get_cancel_button()
        )
        return
    
    try:
        document = message.document
        
        # Fayl formatini tekshirish
        if not document.file_name.endswith('.docx'):
            await message.answer(
                "❌ Iltimos, faqat Word (.docx) fayl yuboring.\n\n"
                "📝 Eski Word formatini (.doc) qo'llab-quvvatlamaymiz.",
                reply_markup=get_cancel_button()
            )
            return
        
        # Fayl hajmini tekshirish (max 20 MB)
        if document.file_size > 20 * 1024 * 1024:
            await message.answer(
                "❌ Fayl juda katta!\n\n"
                "📏 Maksimal hajm: 20 MB\n"
                f"📦 Sizning fayl: {document.file_size / 1024 / 1024:.2f} MB",
                reply_markup=get_cancel_button()
            )
            return
        
        await message.answer("⏳ PDF yaratilmoqda, iltimos kuting...")
        
        # Faylni yuklab olish
        os.makedirs('generated_files', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        docx_filename = f"word_to_pdf_{message.from_user.id}_{timestamp}.docx"
        docx_path = os.path.join('generated_files', docx_filename)
        
        await bot.download(document, destination=docx_path)
        
        # PDF ga o'tkazish
        pdf_path = docx_path.replace('.docx', '.pdf')
        
        import subprocess
        result = subprocess.run(
            ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', 'generated_files', docx_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0 or not os.path.exists(pdf_path):
            raise Exception(f"PDF konvertatsiya xatolik: {result.stderr}")
        
        # PDF faylni yuborish
        pdf_file = FSInputFile(pdf_path)
        await message.answer_document(
            document=pdf_file,
            caption="✅ <b>PDF tayyor!</b>\n\n"
                    f"📄 Fayl nomi: {document.file_name.replace('.docx', '.pdf')}\n"
                    f"📦 Hajm: {os.path.getsize(pdf_path) / 1024:.2f} KB",
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
        
        await state.clear()
        
        # Fayllarni o'chirish
        try:
            os.remove(docx_path)
            os.remove(pdf_path)
            logger.info(f"Word va PDF fayllar o'chirildi: {docx_path}, {pdf_path}")
        except Exception as e:
            logger.error(f"Fayllarni o'chirishda xatolik: {e}")
        
    except subprocess.TimeoutExpired:
        await message.answer(
            "❌ PDF yaratish juda uzoq davom etdi.\n\n"
            "Iltimos, kichikroq fayl yuboring yoki keyinroq qayta urinib ko'ring.",
            reply_markup=get_main_menu()
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Word to PDF xatolik: {e}")
        await message.answer(
            "❌ PDF yaratishda xatolik yuz berdi.\n\n"
            "Iltimos, faylni tekshiring va qayta urinib ko'ring.",
            reply_markup=get_main_menu()
        )
        await state.clear()

@router.message(F.text == "❓ Yordam")
async def help_handler(message: Message):
    """Yordam"""
    help_text = """❓ **Yordam**

🔹 **Kurs ishi yozish** - Mavzuni kiriting va AI tayyorlaydi
🔹 **Maqola yozish** - Maqola mavzusini kiriting
🔹 **Balansim** - Hisobingizni to'ldiring va ko'ring
🔹 **Pul ishlash** - Referal havolangizni ulashing
🔹 **Profil** - Shaxsiy ma'lumotlaringiz
🔹 **Promokodlarim** - Chegirmalardan foydalaning
🔹 **Word → PDF** - Word faylni PDF qiling (bepul)

💬 Savollaringiz bo'lsa, qo'llab-quvvatlash guruhiga qo'shiling:"""
    
    await message.answer(
        help_text, 
        reply_markup=get_support_buttons(config.SUPPORT_GROUP_URL),
        parse_mode="Markdown"
    )
