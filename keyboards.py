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
            [KeyboardButton(text="🎟 Promokod yaratish"), KeyboardButton(text="📋 Promokodlar ro'yxati")],
            [KeyboardButton(text="🚫 Foydalanuvchini cheklash"), KeyboardButton(text="✅ Cheklovni olib tashlash")],
            [KeyboardButton(text="🏠 Foydalanuvchi menyusi")]
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

def get_skip_button():
    """O'tkazib yuborish tugmasi"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏭ O'tkazib yuborish")],
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
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

def get_promo_work_type_buttons():
    """Promokod uchun ish turi tanlash"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🧾 Kurs ishi")],
            [KeyboardButton(text="📰 Maqola")],
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_promo_usage_type_buttons():
    """Promokod foydalanish turi"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔄 1 martalik (1 ta foydalanuvchi)")],
            [KeyboardButton(text="👥 Har bir foydalanuvchi uchun 1 marta")],
            [KeyboardButton(text="♾️ Cheksiz foydalanish")],
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_service_info_buttons(service_type: str, sample_url: str):
    """Xizmat ma'lumoti tugmalari"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📄 Namunani ko'rish", url=sample_url)],
            [InlineKeyboardButton(text="✅ Roziman", callback_data=f"accept_service_{service_type}")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")]
        ]
    )
    return keyboard

def get_support_buttons(support_url: str):
    """Yordam tugmalari"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👥 Qo'llab-quvvatlash guruhi", url=support_url)],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")]
        ]
    )
    return keyboard

def get_pdf_convert_button(file_path: str):
    """PDF ga o'tkazish tugmasi"""
    import os
    # Faqat filename (yo'lsiz) - callback_data 64 baytdan oshmasligi uchun
    filename = os.path.basename(file_path)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📄 Word faylni PDF qilish", callback_data=f"pdf:{filename}")]
        ]
    )
    return keyboard

def get_payment_amount_buttons():
    """To'lov miqdori tugmalari"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="10,000 so'm"), KeyboardButton(text="20,000 so'm")],
            [KeyboardButton(text="50,000 so'm"), KeyboardButton(text="100,000 so'm")],
            [KeyboardButton(text="200,000 so'm"), KeyboardButton(text="500,000 so'm")],
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True
    )
    return keyboard
