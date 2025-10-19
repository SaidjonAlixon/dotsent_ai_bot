import sqlite3
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_name: str = "bot_database.db"):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_db(self):
        """Ma'lumotlar bazasini yaratish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            full_name TEXT,
            balance INTEGER DEFAULT 0,
            referal_code TEXT UNIQUE,
            invited_by INTEGER,
            register_date TEXT NOT NULL,
            is_blocked INTEGER DEFAULT 0
        )
        """)
        
        # Eski foydalanuvchilar uchun is_blocked ustunini qo'shish (agar mavjud bo'lmasa)
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN is_blocked INTEGER DEFAULT 0")
            conn.commit()
        except sqlite3.OperationalError:
            pass
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            topic TEXT NOT NULL,
            price INTEGER NOT NULL,
            file_link TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (telegram_id)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            check_photo_link TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (telegram_id)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS promocodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            work_type TEXT NOT NULL,
            discount_percent INTEGER NOT NULL,
            expiry_date TEXT,
            active INTEGER DEFAULT 1
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Ma'lumotlar bazasi muvaffaqiyatli yaratildi")
    
    def add_user(self, telegram_id: int, username: str, full_name: str, invited_by: Optional[int] = None) -> bool:
        """Yangi foydalanuvchi qo'shish"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            referal_code = f"REF{telegram_id}"
            register_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute("""
            INSERT INTO users (telegram_id, username, full_name, referal_code, invited_by, register_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (telegram_id, username, full_name, referal_code, invited_by, register_date))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Foydalanuvchi ma'lumotlarini olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "telegram_id": row[1],
                "username": row[2],
                "full_name": row[3],
                "balance": row[4],
                "referal_code": row[5],
                "invited_by": row[6],
                "register_date": row[7]
            }
        return None
    
    def update_balance(self, telegram_id: int, amount: int) -> bool:
        """Balansni yangilash"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            UPDATE users SET balance = balance + ? WHERE telegram_id = ?
            """, (amount, telegram_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Balansni yangilashda xatolik: {e}")
            return False
    
    def add_order(self, user_id: int, order_type: str, topic: str, price: int, file_link: str = "") -> int:
        """Yangi buyurtma qo'shish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
        INSERT INTO orders (user_id, type, topic, price, file_link, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, order_type, topic, price, file_link, created_at))
        
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return order_id
    
    def add_payment(self, user_id: int, amount: int, check_photo_link: str) -> int:
        """To'lov qo'shish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
        INSERT INTO payments (user_id, amount, status, check_photo_link, created_at)
        VALUES (?, ?, 'pending', ?, ?)
        """, (user_id, amount, check_photo_link, created_at))
        
        payment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return payment_id
    
    def update_payment_status(self, payment_id: int, status: str) -> bool:
        """To'lov statusini yangilash"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            UPDATE payments SET status = ? WHERE id = ?
            """, (status, payment_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"To'lov statusini yangilashda xatolik: {e}")
            return False
    
    def get_payment(self, payment_id: int) -> Optional[Dict[str, Any]]:
        """To'lov ma'lumotlarini olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM payments WHERE id = ?", (payment_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "user_id": row[1],
                "amount": row[2],
                "status": row[3],
                "check_photo_link": row[4],
                "created_at": row[5]
            }
        return None
    
    def add_promocode(self, code: str, work_type: str, discount_percent: int, expiry_date: str) -> bool:
        """Promokod qo'shish"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT INTO promocodes (code, work_type, discount_percent, expiry_date)
            VALUES (?, ?, ?, ?)
            """, (code, work_type, discount_percent, expiry_date))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_promocode(self, code: str) -> Optional[Dict[str, Any]]:
        """Promokod ma'lumotlarini olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM promocodes WHERE code = ? AND active = 1", (code,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "code": row[1],
                "work_type": row[2],
                "discount_percent": row[3],
                "expiry_date": row[4],
                "active": row[5]
            }
        return None
    
    def get_setting(self, key: str, default: str = "") -> str:
        """Sozlama olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else default
    
    def set_setting(self, key: str, value: str) -> bool:
        """Sozlama o'rnatish"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
            """, (key, value))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Sozlama o'rnatishda xatolik: {e}")
            return False
    
    def get_referal_count(self, telegram_id: int) -> int:
        """Referal sonini olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE invited_by = ?", (telegram_id,))
        result = cursor.fetchone()
        count = result[0] if result else 0
        conn.close()
        
        return count
    
    def get_all_users(self) -> List[int]:
        """Barcha foydalanuvchilar ID sini olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT telegram_id FROM users")
        result = cursor.fetchall()
        users = [row[0] for row in result if row]
        conn.close()
        
        return users
    
    def mark_user_as_blocked(self, telegram_id: int) -> bool:
        """Foydalanuvchini blok deb belgilash"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("UPDATE users SET is_blocked = 1 WHERE telegram_id = ?", (telegram_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Foydalanuvchini blok deb belgilashda xatolik: {e}")
            return False
    
    def unmark_user_as_blocked(self, telegram_id: int) -> bool:
        """Foydalanuvchini faol deb belgilash (unblock)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("UPDATE users SET is_blocked = 0 WHERE telegram_id = ?", (telegram_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Foydalanuvchini faol deb belgilashda xatolik: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, int]:
        """Statistika olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_blocked = 1")
        blocked_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders WHERE type = 'kurs_ishi'")
        kurs_ishlari = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders WHERE type = 'maqola'")
        maqolalar = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_users": total_users,
            "blocked_users": blocked_users,
            "kurs_ishlari": kurs_ishlari,
            "maqolalar": maqolalar,
            "total_orders": total_orders
        }
