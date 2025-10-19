from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import logging

from database import Database
from keyboards import get_admin_menu, get_main_menu, get_cancel_button
import config

logger = logging.getLogger(__name__)

router = Router()
db = Database()

class AdminStates(StatesGroup):
    waiting_for_broadcast_message = State()
    waiting_for_user_id = State()
    waiting_for_direct_message = State()
    waiting_for_balance_user_id = State()
    waiting_for_balance_amount = State()
    waiting_for_referal_bonus = State()
    waiting_for_price_type = State()
    waiting_for_price_amount = State()
    waiting_for_promocode_data = State()

def is_admin(user_id: int) -> bool:
    """Admin ekanligini tekshirish"""
    return user_id == config.ADMIN_ID

@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Admin panel"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Sizda admin huquqlari yo'q.")
        return
    
    await message.answer(
        "👨‍💼 Admin panel\n\nQuyidagi tugmalardan birini tanlang:",
        reply_markup=get_admin_menu()
    )

@router.message(F.text == "📢 Ommaviy xabar")
async def broadcast_start(message: Message, state: FSMContext):
    """Ommaviy xabar yuborish"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        "📢 Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni kiriting:\n\n"
        "Matn, rasm yoki fayl yuborishingiz mumkin.",
        reply_markup=get_cancel_button()
    )
    await state.set_state(AdminStates.waiting_for_broadcast_message)

@router.message(AdminStates.waiting_for_broadcast_message)
async def broadcast_send(message: Message, state: FSMContext, bot):
    """Ommaviy xabarni yuborish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_admin_menu())
        return
    
    users = db.get_all_users()
    success = 0
    failed = 0
    blocked = 0
    
    await message.answer(f"📤 Xabar yuborilmoqda... Jami: {len(users)} foydalanuvchi")
    
    for user_id in users:
        try:
            if message.text:
                await bot.send_message(user_id, message.text)
            elif message.photo:
                await bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption)
            elif message.document:
                await bot.send_document(user_id, message.document.file_id, caption=message.caption)
            success += 1
            # Agar muvaffaqiyatli yuborilsa, foydalanuvchini faol deb belgilash
            db.unmark_user_as_blocked(user_id)
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Xabar yuborishda xatolik (user {user_id}): {e}")
            
            # Agar bot blocked bo'lsa, belgilash
            if "bot was blocked" in error_msg.lower() or "forbidden" in error_msg.lower():
                db.mark_user_as_blocked(user_id)
                blocked += 1
            else:
                failed += 1
    
    await message.answer(
        f"✅ Xabar yuborildi!\n\n"
        f"✅ Muvaffaqiyatli: {success}\n"
        f"🚫 Botni blok qilganlar: {blocked}\n"
        f"❌ Boshqa xatoliklar: {failed}",
        reply_markup=get_admin_menu()
    )
    await state.clear()

@router.message(F.text == "💬 ID orqali xabar")
async def direct_message_start(message: Message, state: FSMContext):
    """ID orqali xabar yuborish"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        "💬 Foydalanuvchi ID sini kiriting:",
        reply_markup=get_cancel_button()
    )
    await state.set_state(AdminStates.waiting_for_user_id)

@router.message(AdminStates.waiting_for_user_id)
async def direct_message_get_id(message: Message, state: FSMContext):
    """ID ni qabul qilish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_admin_menu())
        return
    
    try:
        user_id = int(message.text)
        user = db.get_user(user_id)
        
        if not user:
            await message.answer("❌ Bunday foydalanuvchi topilmadi.")
            return
        
        await state.update_data(target_user_id=user_id)
        await message.answer(
            f"👤 Foydalanuvchi: {user['full_name']} (@{user['username'] or 'mavjud emas'})\n\n"
            f"Xabaringizni kiriting:"
        )
        await state.set_state(AdminStates.waiting_for_direct_message)
    
    except ValueError:
        await message.answer("❌ Iltimos, faqat raqam kiriting.")

@router.message(AdminStates.waiting_for_direct_message)
async def direct_message_send(message: Message, state: FSMContext, bot):
    """Xabarni yuborish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_admin_menu())
        return
    
    data = await state.get_data()
    user_id = data.get("target_user_id")
    
    try:
        if message.text:
            await bot.send_message(user_id, message.text)
        elif message.photo:
            await bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption)
        elif message.document:
            await bot.send_document(user_id, message.document.file_id, caption=message.caption)
        
        await message.answer("✅ Xabar yuborildi!", reply_markup=get_admin_menu())
    except Exception as e:
        await message.answer(f"❌ Xabar yuborishda xatolik: {e}", reply_markup=get_admin_menu())
    
    await state.clear()

@router.message(F.text == "💳 Balans boshqarish")
async def balance_manage_start(message: Message, state: FSMContext):
    """Balans boshqarish"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        "💳 Foydalanuvchi ID sini kiriting:",
        reply_markup=get_cancel_button()
    )
    await state.set_state(AdminStates.waiting_for_balance_user_id)

@router.message(AdminStates.waiting_for_balance_user_id)
async def balance_manage_get_id(message: Message, state: FSMContext):
    """ID ni qabul qilish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_admin_menu())
        return
    
    try:
        user_id = int(message.text)
        user = db.get_user(user_id)
        
        if not user:
            await message.answer("❌ Bunday foydalanuvchi topilmadi.")
            return
        
        await state.update_data(balance_user_id=user_id)
        await message.answer(
            f"👤 Foydalanuvchi: {user['full_name']}\n"
            f"💰 Joriy balans: {user['balance']:,} so'm\n\n"
            f"Qo'shish yoki kamaytirish uchun summa kiriting:\n"
            f"Qo'shish: 10000\n"
            f"Kamaytirish: -5000"
        )
        await state.set_state(AdminStates.waiting_for_balance_amount)
    
    except ValueError:
        await message.answer("❌ Iltimos, faqat raqam kiriting.")

@router.message(AdminStates.waiting_for_balance_amount)
async def balance_manage_update(message: Message, state: FSMContext):
    """Balansni yangilash"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_admin_menu())
        return
    
    try:
        amount = int(message.text.replace(",", "").replace(" ", ""))
        data = await state.get_data()
        user_id = data.get("balance_user_id")
        
        db.update_balance(user_id, amount)
        user = db.get_user(user_id)
        
        await message.answer(
            f"✅ Balans yangilandi!\n\n"
            f"Yangi balans: {user['balance']:,} so'm",
            reply_markup=get_admin_menu()
        )
    
    except ValueError:
        await message.answer("❌ Iltimos, faqat raqam kiriting.")
    
    await state.clear()

@router.message(F.text == "📊 Statistika")
async def statistics(message: Message):
    """Statistika"""
    if not is_admin(message.from_user.id):
        return
    
    stats = db.get_statistics()
    
    await message.answer(
        f"📊 Statistika\n\n"
        f"👥 Jami foydalanuvchilar: {stats['total_users']}\n"
        f"🚫 Botni blok qilganlar: {stats['blocked_users']}\n"
        f"✅ Faol foydalanuvchilar: {stats['total_users'] - stats['blocked_users']}\n\n"
        f"🧾 Kurs ishlari: {stats['kurs_ishlari']}\n"
        f"📰 Maqolalar: {stats['maqolalar']}\n"
        f"📝 Jami buyurtmalar: {stats['total_orders']}\n\n"
        f"📅 Sana: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )

@router.message(F.text == "🤝 Referal sozlamalari")
async def referal_settings(message: Message, state: FSMContext):
    """Referal sozlamalari"""
    if not is_admin(message.from_user.id):
        return
    
    current_bonus = db.get_setting("referal_bonus", str(config.DEFAULT_REFERAL_BONUS))
    
    await message.answer(
        f"🤝 Referal sozlamalari\n\n"
        f"Joriy bonus: {current_bonus} so'm\n\n"
        f"Yangi bonus miqdorini kiriting:",
        reply_markup=get_cancel_button()
    )
    await state.set_state(AdminStates.waiting_for_referal_bonus)

@router.message(AdminStates.waiting_for_referal_bonus)
async def referal_settings_update(message: Message, state: FSMContext):
    """Referal bonusni yangilash"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_admin_menu())
        return
    
    try:
        bonus = int(message.text.replace(",", "").replace(" ", ""))
        db.set_setting("referal_bonus", str(bonus))
        
        await message.answer(
            f"✅ Referal bonus yangilandi!\n\n"
            f"Yangi bonus: {bonus:,} so'm",
            reply_markup=get_admin_menu()
        )
    
    except ValueError:
        await message.answer("❌ Iltimos, faqat raqam kiriting.")
    
    await state.clear()

@router.message(F.text == "💸 Narxlarni boshqarish")
async def price_management(message: Message, state: FSMContext):
    """Narxlarni boshqarish"""
    if not is_admin(message.from_user.id):
        return
    
    kurs_price = db.get_setting("kurs_ishi_price", str(config.DEFAULT_KURS_ISH_PRICE))
    maqola_price = db.get_setting("maqola_price", str(config.DEFAULT_MAQOLA_PRICE))
    
    await message.answer(
        f"💸 Narxlarni boshqarish\n\n"
        f"🧾 Kurs ishi: {kurs_price} so'm\n"
        f"📰 Maqola: {maqola_price} so'm\n\n"
        f"Qaysi narxni o'zgartirmoqchisiz?\n\n"
        f"1 - Kurs ishi\n"
        f"2 - Maqola",
        reply_markup=get_cancel_button()
    )
    await state.set_state(AdminStates.waiting_for_price_type)

@router.message(AdminStates.waiting_for_price_type)
async def price_management_type(message: Message, state: FSMContext):
    """Narx turini tanlash"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_admin_menu())
        return
    
    if message.text == "1":
        await state.update_data(price_type="kurs_ishi_price")
        await message.answer("Kurs ishi uchun yangi narxni kiriting (so'mda):")
        await state.set_state(AdminStates.waiting_for_price_amount)
    elif message.text == "2":
        await state.update_data(price_type="maqola_price")
        await message.answer("Maqola uchun yangi narxni kiriting (so'mda):")
        await state.set_state(AdminStates.waiting_for_price_amount)
    else:
        await message.answer("❌ Iltimos, 1 yoki 2 raqamini kiriting.")

@router.message(AdminStates.waiting_for_price_amount)
async def price_management_update(message: Message, state: FSMContext):
    """Narxni yangilash"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_admin_menu())
        return
    
    try:
        price = int(message.text.replace(",", "").replace(" ", ""))
        data = await state.get_data()
        price_type = data.get("price_type")
        
        db.set_setting(price_type, str(price))
        
        type_name = "Kurs ishi" if price_type == "kurs_ishi_price" else "Maqola"
        
        await message.answer(
            f"✅ Narx yangilandi!\n\n"
            f"{type_name}: {price:,} so'm",
            reply_markup=get_admin_menu()
        )
    
    except ValueError:
        await message.answer("❌ Iltimos, faqat raqam kiriting.")
    
    await state.clear()

@router.message(F.text == "🎟 Promokod yaratish")
async def promocode_create(message: Message, state: FSMContext):
    """Promokod yaratish"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        "🎟 Promokod yaratish\n\n"
        "Quyidagi formatda ma'lumot kiriting:\n\n"
        "Kod Turi Chegirma Muddat\n\n"
        "Masalan:\n"
        "YANGI2025 kurs_ishi 20 2025-12-31\n\n"
        "Turi: kurs_ishi yoki maqola\n"
        "Chegirma: foizda (1-100)\n"
        "Muddat: YYYY-MM-DD formatda",
        reply_markup=get_cancel_button()
    )
    await state.set_state(AdminStates.waiting_for_promocode_data)

@router.message(AdminStates.waiting_for_promocode_data)
async def promocode_create_process(message: Message, state: FSMContext):
    """Promokodni yaratish"""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_admin_menu())
        return
    
    try:
        parts = message.text.split()
        if len(parts) != 4:
            await message.answer("❌ Noto'g'ri format. Iltimos, qaytadan urinib ko'ring.")
            return
        
        code, work_type, discount, expiry = parts
        discount = int(discount)
        
        if work_type not in ["kurs_ishi", "maqola"]:
            await message.answer("❌ Turi faqat 'kurs_ishi' yoki 'maqola' bo'lishi mumkin.")
            return
        
        if discount < 1 or discount > 100:
            await message.answer("❌ Chegirma 1 dan 100 gacha bo'lishi kerak.")
            return
        
        datetime.strptime(expiry, "%Y-%m-%d")
        
        if db.add_promocode(code.upper(), work_type, discount, expiry):
            await message.answer(
                f"✅ Promokod yaratildi!\n\n"
                f"🎁 Kod: {code.upper()}\n"
                f"📝 Turi: {work_type}\n"
                f"💰 Chegirma: {discount}%\n"
                f"📅 Muddat: {expiry}",
                reply_markup=get_admin_menu()
            )
        else:
            await message.answer("❌ Bunday promokod allaqachon mavjud.", reply_markup=get_admin_menu())
    
    except ValueError:
        await message.answer("❌ Noto'g'ri format. Iltimos, qaytadan urinib ko'ring.")
    
    await state.clear()

@router.callback_query(F.data.startswith("approve_payment_"))
async def approve_payment(callback: CallbackQuery, bot):
    """To'lovni tasdiqlash"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Sizda admin huquqlari yo'q.", show_alert=True)
        return
    
    payment_id = int(callback.data.split("_")[-1])
    payment = db.get_payment(payment_id)
    
    if not payment:
        await callback.answer("❌ To'lov topilmadi.", show_alert=True)
        return
    
    if payment['status'] != 'pending':
        await callback.answer("❌ To'lov allaqachon ko'rib chiqilgan.", show_alert=True)
        return
    
    db.update_payment_status(payment_id, 'approved')
    db.update_balance(payment['user_id'], payment['amount'])
    
    user = db.get_user(payment['user_id'])
    
    try:
        await bot.send_message(
            payment['user_id'],
            f"✅ To'lovingiz tasdiqlandi!\n\n"
            f"💰 Summa: {payment['amount']:,} so'm\n"
            f"💳 Yangi balans: {user['balance']:,} so'm"
        )
    except:
        pass
    
    await callback.message.edit_caption(
        caption=callback.message.caption + f"\n\n✅ Tasdiqlandi - {callback.from_user.full_name}"
    )
    await callback.answer("✅ To'lov tasdiqlandi!", show_alert=True)

@router.callback_query(F.data.startswith("reject_payment_"))
async def reject_payment(callback: CallbackQuery, bot):
    """To'lovni rad etish"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Sizda admin huquqlari yo'q.", show_alert=True)
        return
    
    payment_id = int(callback.data.split("_")[-1])
    payment = db.get_payment(payment_id)
    
    if not payment:
        await callback.answer("❌ To'lov topilmadi.", show_alert=True)
        return
    
    if payment['status'] != 'pending':
        await callback.answer("❌ To'lov allaqachon ko'rib chiqilgan.", show_alert=True)
        return
    
    db.update_payment_status(payment_id, 'rejected')
    
    try:
        await bot.send_message(
            payment['user_id'],
            f"❌ To'lovingiz rad etildi.\n\n"
            f"💰 Summa: {payment['amount']:,} so'm\n\n"
            f"Iltimos, to'lovni to'g'ri amalga oshiring yoki admin bilan bog'laning."
        )
    except:
        pass
    
    await callback.message.edit_caption(
        caption=callback.message.caption + f"\n\n❌ Rad etildi - {callback.from_user.full_name}"
    )
    await callback.answer("❌ To'lov rad etildi.", show_alert=True)

@router.message(F.text == "🏠 Foydalanuvchi menyusi")
async def back_to_user_menu(message: Message):
    """Foydalanuvchi menyusiga qaytish"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer("Foydalanuvchi menyusi:", reply_markup=get_main_menu())
