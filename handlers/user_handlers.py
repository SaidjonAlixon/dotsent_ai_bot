from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import logging

from database import Database
from keyboards import get_main_menu, get_cancel_button, get_balance_buttons
from utils.course_writer import generate_course_work
from utils.document_generator import create_word_document
import config
import os

logger = logging.getLogger(__name__)

router = Router()
db = Database()

class UserStates(StatesGroup):
    waiting_for_kurs_topic = State()
    waiting_for_kurs_fish = State()
    waiting_for_kurs_university = State()
    waiting_for_kurs_subject = State()
    waiting_for_kurs_course_number = State()
    waiting_for_maqola_topic = State()
    waiting_for_payment_amount = State()
    waiting_for_payment_check = State()
    waiting_for_promocode = State()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Start buyrug'i"""
    telegram_id = message.from_user.id
    username = message.from_user.username or ""
    full_name = message.from_user.full_name or "Foydalanuvchi"
    
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
        welcome_text = f"Qaytganingizdan xursandmiz, {full_name}! 😊\n\nQuyidagi tugmalardan birini tanlang:"
    
    await message.answer(welcome_text, reply_markup=get_main_menu())

@router.message(F.text == "🧾 Kurs ishi yozish")
async def kurs_ishi_handler(message: Message, state: FSMContext):
    """Kurs ishi yozish"""
    await message.answer(
        "📚 Kurs ishi tayyorlash boshlandi!\n\n"
        "👤 F.I.Sh. (to'liq ismingiz) kiriting:\n\n"
        "Masalan: Abdullayev Akmal Rustamovich",
        reply_markup=get_cancel_button()
    )
    await state.set_state(UserStates.waiting_for_kurs_fish)

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
    
    price = int(db.get_setting("kurs_ishi_price", str(config.DEFAULT_KURS_ISH_PRICE)))
    
    if user["balance"] < price:
        await message.answer(
            f"❌ Balansingizda mablag' yetarli emas!\n\n"
            f"Kerakli summa: {price:,} so'm\n"
            f"Sizning balansingiz: {user['balance']:,} so'm\n\n"
            f"Iltimos, avval balansni to'ldiring.",
            reply_markup=get_main_menu()
        )
        await state.clear()
        return
    
    data = await state.get_data()
    
    await message.answer(
        f"✅ Ma'lumotlar qabul qilindi!\n\n"
        f"👤 F.I.Sh: {data['fish']}\n"
        f"🏫 O'quv yurti: {data['university']}\n"
        f"📖 Fan: {data['subject']}\n"
        f"📚 Mavzu: {data['topic']}\n"
        f"🎓 Kurs: {course_number}\n\n"
        f"⏳ Kurs ishingiz tayyorlanmoqda...\n"
        f"Bu 2-3 daqiqa vaqt olishi mumkin. Iltimos, kuting.",
        reply_markup=get_main_menu()
    )
    
    try:
        user_data_for_ai = {
            'name': data['fish'],
            'university': data['university'],
            'subject': data['subject'],
            'topic': data['topic'],
            'course': course_number
        }
        
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
🎓 Kurs: {course_number}
💰 Narx: {price:,} so'm
🕒 Sana: {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
            )
            file_link = f"https://t.me/c/{str(config.KURS_ISHLARI_CHANNEL_ID)[4:]}/{channel_message.message_id}"
        else:
            file_link = docx_path
        
        document_file_user = FSInputFile(docx_path)
        await message.answer_document(
            document=document_file_user,
            caption=f"✅ Kurs ishingiz tayyor!\n\n📚 Mavzu: {data['topic']}\n💰 To'langan: {price:,} so'm"
        )
        
        db.add_order(telegram_id, "kurs_ishi", data['topic'], price, file_link)
        
    except Exception as e:
        logger.error(f"Kurs ishi yaratishda xatolik: {e}")
        await message.answer(
            f"❌ Kurs ishi tayyorlashda xatolik yuz berdi: {str(e)}\n\n"
            "Balansingiz o'zgartirilmadi. Iltimos, keyinroq qayta urinib ko'ring.",
            reply_markup=get_main_menu()
        )
    
    await state.clear()

@router.message(F.text == "📰 Maqola yozish")
async def maqola_handler(message: Message, state: FSMContext):
    """Maqola yozish"""
    await message.answer(
        "📝 Maqola mavzusini kiriting:\n\nMasalan: Raqamli iqtisodiyotda blockchain texnologiyasining o'rni",
        reply_markup=get_cancel_button()
    )
    await state.set_state(UserStates.waiting_for_maqola_topic)

@router.message(UserStates.waiting_for_maqola_topic)
async def process_maqola_topic(message: Message, state: FSMContext, bot):
    """Maqola mavzusini qabul qilish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_menu())
        return
    
    topic = message.text
    telegram_id = message.from_user.id
    user = db.get_user(telegram_id)
    
    if not user:
        await message.answer("❌ Foydalanuvchi topilmadi. /start buyrug'ini yuboring.", reply_markup=get_main_menu())
        await state.clear()
        return
    
    price = int(db.get_setting("maqola_price", str(config.DEFAULT_MAQOLA_PRICE)))
    
    if user["balance"] < price:
        await message.answer(
            f"❌ Balansingizda mablag' yetarli emas!\n\n"
            f"Kerakli summa: {price:,} so'm\n"
            f"Sizning balansingiz: {user['balance']:,} so'm\n\n"
            f"Iltimos, avval balansni to'ldiring.",
            reply_markup=get_main_menu()
        )
        await state.clear()
        return
    
    await message.answer(
        "⏳ Sizning maqolangiz tayyorlanmoqda...\n\n"
        "Bu biroz vaqt olishi mumkin. Iltimos, kuting.",
        reply_markup=get_main_menu()
    )
    
    try:
        from utils.course_writer import generate_section_with_ai
        
        content = await generate_section_with_ai(
            f"Quyidagi mavzuda ilmiy maqola yozing: {topic}\n\n"
            f"Maqola quyidagi qismlardan iborat bo'lishi kerak:\n"
            f"1. Annotatsiya (o'zbek va ingliz tillarida)\n"
            f"2. Kirish\n"
            f"3. Asosiy qism (2-3 bo'lim)\n"
            f"4. Xulosa\n"
            f"5. Foydalanilgan adabiyotlar\n\n"
            f"Matn ilmiy uslubda, batafsil va professional bo'lishi kerak.",
            max_words=3000
        )
        
        sections = [
            {'type': 'intro', 'content': content}
        ]
        
        user_data_maqola = {
            'name': user['full_name'],
            'university': '',
            'subject': '',
            'topic': topic,
            'course': ''
        }
        
        filename = f"maqola_{telegram_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        os.makedirs('generated_files', exist_ok=True)
        filepath = os.path.join('generated_files', filename)
        
        create_word_document(sections, user_data_maqola, filepath)
        
        db.update_balance(telegram_id, -price)
        
        document_file = FSInputFile(filepath)
        
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
        await message.answer_document(
            document=document_file_user,
            caption=f"✅ Maqolangiz tayyor!\n\n📝 Mavzu: {topic}\n💰 To'langan: {price:,} so'm"
        )
        
        db.add_order(telegram_id, "maqola", topic, price, file_link)
        
    except Exception as e:
        logger.error(f"Maqola yaratishda xatolik: {e}")
        await message.answer(
            "❌ Maqola tayyorlashda xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.\n\n"
            "Balansingiz o'zgartirilmadi.",
            reply_markup=get_main_menu()
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
            f"💳 To'lov summasi: {amount:,} so'm\n\n"
            f"Iltimos, to'lov chekini (screenshot) yuboring:",
            reply_markup=get_cancel_button()
        )
        await state.set_state(UserStates.waiting_for_payment_check)
    
    except ValueError:
        await message.answer("❌ Iltimos, faqat raqam kiriting.")

@router.message(UserStates.waiting_for_payment_check, F.photo)
async def process_payment_check(message: Message, state: FSMContext, bot):
    """To'lov chekini qabul qilish"""
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
    """Promokod kiritish"""
    await message.answer(
        "🎁 Promokodni kiriting:\n\n"
        "Promokod orqali chegirmaga ega bo'ling!",
        reply_markup=get_cancel_button()
    )
    await state.set_state(UserStates.waiting_for_promocode)

@router.message(UserStates.waiting_for_promocode)
async def process_promocode(message: Message, state: FSMContext):
    """Promokodni tekshirish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_menu())
        return
    
    code = message.text.strip().upper()
    promocode = db.get_promocode(code)
    
    if not promocode:
        await message.answer("❌ Bunday promokod topilmadi yoki muddati tugagan.", reply_markup=get_main_menu())
        await state.clear()
        return
    
    if promocode['expiry_date']:
        expiry = datetime.strptime(promocode['expiry_date'], "%Y-%m-%d")
        if expiry < datetime.now():
            await message.answer("❌ Promokod muddati tugagan.", reply_markup=get_main_menu())
            await state.clear()
            return
    
    await message.answer(
        f"✅ Promokod qabul qilindi!\n\n"
        f"🎁 Kod: {code}\n"
        f"📝 Turi: {promocode['work_type']}\n"
        f"💰 Chegirma: {promocode['discount_percent']}%\n\n"
        f"Keyingi buyurtmangizda bu chegirma avtomatik qo'llaniladi!",
        reply_markup=get_main_menu()
    )
    
    await state.clear()

@router.message(F.text == "❓ Yordam")
async def help_handler(message: Message):
    """Yordam"""
    help_text = """❓ Yordam

🔹 Kurs ishi yozish - Mavzuni kiriting va AI tayyorlaydi
🔹 Maqola yozish - Maqola mavzusini kiriting
🔹 Balansim - Hisobingizni to'ldiring va ko'ring
🔹 Pul ishlash - Referal havolangizni ulashing
🔹 Profil - Shaxsiy ma'lumotlaringiz
🔹 Promokodlarim - Chegirmalardan foydalaning

💬 Admin bilan bog'lanish: /admin
📞 Texnik yordam: @support"""
    
    await message.answer(help_text)
