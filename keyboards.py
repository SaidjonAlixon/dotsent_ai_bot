from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu():
    """Asosiy menyu"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🧾 Kurs ishi yozish"), KeyboardButton(text="📰 Maqola yozish")],
            [KeyboardButton(text="💰 Balansim"), KeyboardButton(text="💵 Pul ishlash")],
            [KeyboardButton(text="👤 Profil"), KeyboardButton(text="🎁 Promokodlarim")],
            [KeyboardButton(text="❓ Yordam")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_admin_menu():
    """Admin menyusi"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📢 Ommaviy xabar"), KeyboardButton(text="💬 ID orqali xabar")],
            [KeyboardButton(text="💳 Balans boshqarish"), KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="🤝 Referal sozlamalari"), KeyboardButton(text="💸 Narxlarni boshqarish")],
            [KeyboardButton(text="🎟 Promokod yaratish"), KeyboardButton(text="🏠 Foydalanuvchi menyusi")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_cancel_button():
    """Bekor qilish tugmasi"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True
    )
    return keyboard

def get_payment_confirmation(payment_id: int):
    """To'lovni tasdiqlash tugmalari"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_payment_{payment_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_payment_{payment_id}")
            ]
        ]
    )
    return keyboard

def get_balance_buttons():
    """Balans to'ldirish tugmalari"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💵 Balansni to'ldirish", callback_data="add_balance")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")]
        ]
    )
    return keyboard

def get_work_type_buttons():
    """Ish turi tanlash"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🧾 Kurs ishi", callback_data="work_type_kurs")],
            [InlineKeyboardButton(text="📰 Maqola", callback_data="work_type_maqola")]
        ]
    )
    return keyboard
