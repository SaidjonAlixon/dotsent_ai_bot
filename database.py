import psycopg2
import psycopg2.pool
from psycopg2.extras import RealDictCursor
import logging
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from utils.timezone import get_tashkent_time

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, database_url: str = None):
        """PostgreSQL database connection"""
        # DATABASE_URL environment variable'dan olish
        self.database_url = database_url or os.getenv("DATABASE_URL")
        
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable topilmadi! Iltimos, .env fayliga DATABASE_URL qo'shing.")
        
        # Avval init_db'ni chaqirish (oddiy connection bilan)
        # Keyin connection pool yaratish
        self.pool = None
        self.init_db()
        
        # Connection pool yaratish (init_db'dan keyin)
        try:
            self.pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=self.database_url
            )
            logger.info("Connection pool muvaffaqiyatli yaratildi")
        except Exception as e:
            logger.warning(f"Connection pool yaratishda xatolik (oddiy connection ishlatiladi): {e}")
            self.pool = None
    
    def get_connection(self):
        """Database connection olish"""
        if self.pool:
            return self.pool.getconn()
        else:
            return psycopg2.connect(self.database_url)
    
    def return_connection(self, conn):
        """Connection'ni pool'ga qaytarish"""
        if self.pool:
            self.pool.putconn(conn)
        else:
            conn.close()
    
    def _table_exists(self, cursor, table_name: str) -> bool:
        """Jadval mavjudligini tekshirish"""
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            )
        """, (table_name,))
        return cursor.fetchone()[0]
    
    def init_db(self):
        """Ma'lumotlar bazasini yaratish"""
        # Oddiy connection yaratish (pool'siz)
        conn = psycopg2.connect(self.database_url)
        # Autocommit mode'ni yoqish - har bir statement alohida commit bo'ladi
        conn.autocommit = True
        cursor = conn.cursor()
        
        try:
            # Users jadvali - avval yaratish
            if not self._table_exists(cursor, 'users'):
                cursor.execute("""
                    CREATE TABLE users (
                        id SERIAL PRIMARY KEY,
                        telegram_id BIGINT UNIQUE NOT NULL,
                        username VARCHAR(255),
                        full_name VARCHAR(255),
                        balance INTEGER DEFAULT 0,
                        referal_code VARCHAR(255) UNIQUE,
                        invited_by BIGINT,
                        register_date TIMESTAMP NOT NULL,
                        is_blocked INTEGER DEFAULT 0,
                        active_promocode VARCHAR(255) DEFAULT NULL
                    )
                """)
                logger.info("Users jadvali yaratildi")
            else:
                logger.info("Users jadvali allaqachon mavjud")
                # Agar jadval mavjud bo'lsa, INTEGER ni BIGINT ga o'zgartirish (migration)
                try:
                    cursor.execute("ALTER TABLE users ALTER COLUMN telegram_id TYPE BIGINT")
                    logger.info("Users.telegram_id INTEGER dan BIGINT ga o'zgartirildi")
                except psycopg2.ProgrammingError:
                    pass
                try:
                    cursor.execute("ALTER TABLE users ALTER COLUMN invited_by TYPE BIGINT")
                    logger.info("Users.invited_by INTEGER dan BIGINT ga o'zgartirildi")
                except psycopg2.ProgrammingError:
                    pass
            
            # Eski foydalanuvchilar uchun is_blocked ustunini qo'shish (agar mavjud bo'lmasa)
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN is_blocked INTEGER DEFAULT 0")
                logger.info("Users jadvaliga is_blocked ustuni qo'shildi")
            except psycopg2.ProgrammingError as e:
                # Ustun allaqachon mavjud
                pass
            
            # Eski foydalanuvchilar uchun active_promocode ustunini qo'shish
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN active_promocode VARCHAR(255) DEFAULT NULL")
                logger.info("Users jadvaliga active_promocode ustuni qo'shildi")
            except psycopg2.ProgrammingError as e:
                # Ustun allaqachon mavjud
                pass
            
            # Orders jadvali - users jadvali yaratilgandan keyin
            if not self._table_exists(cursor, 'orders'):
                cursor.execute("""
                    CREATE TABLE orders (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT NOT NULL,
                        type VARCHAR(50) NOT NULL,
                        topic TEXT NOT NULL,
                        price INTEGER NOT NULL,
                        file_link TEXT,
                        created_at TIMESTAMP NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users (telegram_id)
                    )
                """)
                logger.info("Orders jadvali yaratildi")
            else:
                logger.info("Orders jadvali allaqachon mavjud")
                # Migration: INTEGER ni BIGINT ga o'zgartirish
                try:
                    cursor.execute("ALTER TABLE orders ALTER COLUMN user_id TYPE BIGINT")
                    logger.info("Orders.user_id INTEGER dan BIGINT ga o'zgartirildi")
                except psycopg2.ProgrammingError:
                    pass
            
            # Payments jadvali
            if not self._table_exists(cursor, 'payments'):
                cursor.execute("""
                    CREATE TABLE payments (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT NOT NULL,
                        amount INTEGER NOT NULL,
                        status VARCHAR(50) DEFAULT 'pending',
                        check_photo_link TEXT,
                        created_at TIMESTAMP NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users (telegram_id)
                    )
                """)
                logger.info("Payments jadvali yaratildi")
            else:
                logger.info("Payments jadvali allaqachon mavjud")
                # Migration: INTEGER ni BIGINT ga o'zgartirish
                try:
                    cursor.execute("ALTER TABLE payments ALTER COLUMN user_id TYPE BIGINT")
                    logger.info("Payments.user_id INTEGER dan BIGINT ga o'zgartirildi")
                except psycopg2.ProgrammingError:
                    pass
            
            # Promocodes jadvali
            if not self._table_exists(cursor, 'promocodes'):
                cursor.execute("""
                    CREATE TABLE promocodes (
                        id SERIAL PRIMARY KEY,
                        code VARCHAR(255) UNIQUE NOT NULL,
                        work_type VARCHAR(50) NOT NULL,
                        discount_percent INTEGER NOT NULL,
                        usage_type VARCHAR(50) DEFAULT 'unlimited',
                        used_by TEXT DEFAULT '[]',
                        expiry_date DATE,
                        active INTEGER DEFAULT 1
                    )
                """)
                logger.info("Promocodes jadvali yaratildi")
            else:
                logger.info("Promocodes jadvali allaqachon mavjud")
            
            # Eski promokodlar uchun yangi ustunlarni qo'shish
            try:
                cursor.execute("ALTER TABLE promocodes ADD COLUMN usage_type VARCHAR(50) DEFAULT 'unlimited'")
                logger.info("Promocodes jadvaliga usage_type ustuni qo'shildi")
            except psycopg2.ProgrammingError:
                pass
            
            try:
                cursor.execute("ALTER TABLE promocodes ADD COLUMN used_by TEXT DEFAULT '[]'")
                logger.info("Promocodes jadvaliga used_by ustuni qo'shildi")
            except psycopg2.ProgrammingError:
                pass
            
            # Settings jadvali
            if not self._table_exists(cursor, 'settings'):
                cursor.execute("""
                    CREATE TABLE settings (
                        key VARCHAR(255) PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                """)
                logger.info("Settings jadvali yaratildi")
            else:
                logger.info("Settings jadvali allaqachon mavjud")
            
            logger.info("PostgreSQL ma'lumotlar bazasi muvaffaqiyatli yaratildi/yoki mavjud")
        except Exception as e:
            logger.error(f"Database yaratishda xatolik: {e}")
            logger.error(f"Xatolik tafsilotlari: {type(e).__name__}: {str(e)}")
            raise
        finally:
            # Autocommit mode'ni o'chirish
            conn.autocommit = False
            cursor.close()
            conn.close()
    
    def add_user(self, telegram_id: int, username: str, full_name: str, invited_by: Optional[int] = None) -> bool:
        """Yangi foydalanuvchi qo'shish"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            referal_code = f"REF{telegram_id}"
            register_date = get_tashkent_time()
            
            cursor.execute("""
                INSERT INTO users (telegram_id, username, full_name, referal_code, invited_by, register_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (telegram_id, username, full_name, referal_code, invited_by, register_date))
            
            conn.commit()
            return True
        except psycopg2.IntegrityError:
            if conn:
                conn.rollback()
            return False
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Foydalanuvchi qo'shishda xatolik: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Foydalanuvchi ma'lumotlarini olish"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT id, telegram_id, username, full_name, balance, referal_code, invited_by, 
                       register_date, is_blocked, active_promocode 
                FROM users 
                WHERE telegram_id = %s
            """, (telegram_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Foydalanuvchi olishda xatolik: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def set_user_promocode(self, telegram_id: int, promocode_code: str) -> bool:
        """Foydalanuvchining aktiv promokodini saqlash"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users SET active_promocode = %s WHERE telegram_id = %s
            """, (promocode_code, telegram_id))
            
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Foydalanuvchi promokodini saqlashda xatolik: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def clear_user_promocode(self, telegram_id: int) -> bool:
        """Foydalanuvchining aktiv promokodini o'chirish"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users SET active_promocode = NULL WHERE telegram_id = %s
            """, (telegram_id,))
            
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Foydalanuvchi promokodini o'chirishda xatolik: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def update_user_info(self, telegram_id: int, username: str, full_name: str) -> bool:
        """Foydalanuvchi ma'lumotlarini yangilash"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users SET username = %s, full_name = %s WHERE telegram_id = %s
            """, (username, full_name, telegram_id))
            
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Foydalanuvchi ma'lumotlarini yangilashda xatolik: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def update_balance(self, telegram_id: int, amount: int) -> bool:
        """Balansni yangilash"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users SET balance = balance + %s WHERE telegram_id = %s
            """, (amount, telegram_id))
            
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Balansni yangilashda xatolik: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def add_order(self, user_id: int, order_type: str, topic: str, price: int, file_link: str = "") -> int:
        """Yangi buyurtma qo'shish"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            created_at = get_tashkent_time()
            
            cursor.execute("""
                INSERT INTO orders (user_id, type, topic, price, file_link, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (user_id, order_type, topic, price, file_link, created_at))
            
            order_id = cursor.fetchone()[0]
            conn.commit()
            return order_id
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Buyurtma qo'shishda xatolik: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def add_payment(self, user_id: int, amount: int, check_photo_link: str) -> int:
        """To'lov qo'shish"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            created_at = get_tashkent_time()
            
            cursor.execute("""
                INSERT INTO payments (user_id, amount, status, check_photo_link, created_at)
                VALUES (%s, %s, 'pending', %s, %s)
                RETURNING id
            """, (user_id, amount, check_photo_link, created_at))
            
            payment_id = cursor.fetchone()[0]
            conn.commit()
            return payment_id
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"To'lov qo'shishda xatolik: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def update_payment_status(self, payment_id: int, status: str) -> bool:
        """To'lov statusini yangilash"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE payments SET status = %s WHERE id = %s
            """, (status, payment_id))
            
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"To'lov statusini yangilashda xatolik: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def get_payment(self, payment_id: int) -> Optional[Dict[str, Any]]:
        """To'lov ma'lumotlarini olish"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("SELECT * FROM payments WHERE id = %s", (payment_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"To'lov olishda xatolik: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def add_promocode(self, code: str, work_type: str, discount_percent: int, expiry_date: str = None, usage_type: str = "unlimited") -> bool:
        """Promokod qo'shish"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO promocodes (code, work_type, discount_percent, expiry_date, usage_type, used_by, active)
                VALUES (%s, %s, %s, %s, %s, '[]', 1)
            """, (code, work_type, discount_percent, expiry_date, usage_type))
            
            conn.commit()
            return True
        except psycopg2.IntegrityError:
            if conn:
                conn.rollback()
            return False
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Promokod qo'shishda xatolik: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def get_promocode(self, code: str) -> Optional[Dict[str, Any]]:
        """Promokod ma'lumotlarini olish"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT id, code, work_type, discount_percent, usage_type, used_by, expiry_date, active 
                FROM promocodes 
                WHERE code = %s AND active = 1
            """, (code,))
            row = cursor.fetchone()
            
            if row:
                result = dict(row)
                # PostgreSQL DATE ni string'ga o'girish
                if result.get('expiry_date'):
                    result['expiry_date'] = str(result['expiry_date'])
                return result
            return None
        except Exception as e:
            logger.error(f"Promokod olishda xatolik: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def can_use_promocode(self, code: str, user_id: int) -> tuple[bool, str]:
        """Promokodni ishlatish mumkinligini tekshirish"""
        import json
        
        promocode = self.get_promocode(code)
        if not promocode:
            return False, "❌ Bunday promokod topilmadi yoki muddati tugagan."
        
        # Muddati tekshirish
        if promocode.get('expiry_date'):
            from datetime import datetime
            expiry = datetime.strptime(promocode['expiry_date'], "%Y-%m-%d")
            if expiry.date() < get_tashkent_time().date():
                return False, "❌ Promokod muddati tugagan."
        
        usage_type = promocode.get('usage_type', 'unlimited')
        used_by_str = promocode.get('used_by', '[]')
        
        try:
            used_by = json.loads(used_by_str) if used_by_str else []
        except:
            used_by = []
        
        # 1 martalik - bir kishi ishlatgandan keyin o'chib ketadi
        if usage_type == "one_time":
            if len(used_by) > 0:
                return False, "❌ Bu promokod allaqachon ishlatilgan."
            return True, "✅ Promokod qabul qilindi!"
        
        # Har bir foydalanuvchi 1 marta
        elif usage_type == "per_user":
            if user_id in used_by:
                return False, "❌ Siz bu promokodni allaqachon ishlatgansiz."
            return True, "✅ Promokod qabul qilindi!"
        
        # Cheksiz
        elif usage_type == "unlimited":
            return True, "✅ Promokod qabul qilindi!"
        
        return False, "❌ Noma'lum xatolik."
    
    def mark_promocode_as_used(self, promo_id: int, user_id: int = None):
        """Promokodni ishlatilgan deb belgilash"""
        import json
        
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Joriy used_by ni olish
            cursor.execute("SELECT used_by FROM promocodes WHERE id = %s", (promo_id,))
            row = cursor.fetchone()
            
            if row:
                used_by_str = row[0] if row[0] else '[]'
                try:
                    used_by = json.loads(used_by_str) if used_by_str else []
                except:
                    used_by = []
                
                # Foydalanuvchi ID ni qo'shish (agar berilgan bo'lsa)
                if user_id and user_id not in used_by:
                    used_by.append(user_id)
                
                # Yangilash
                cursor.execute(
                    "UPDATE promocodes SET used_by = %s WHERE id = %s",
                    (json.dumps(used_by), promo_id)
                )
                
                conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Promokodni ishlatilgan deb belgilashda xatolik: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def deactivate_promocode(self, promo_id: int):
        """Promokodni o'chirish (active = 0)"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("UPDATE promocodes SET active = 0 WHERE id = %s", (promo_id,))
            
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Promokodni o'chirishda xatolik: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def get_all_promocodes(self) -> list:
        """Barcha promokodlarni olish"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT id, code, work_type, discount_percent, usage_type, used_by, expiry_date, active 
                FROM promocodes 
                ORDER BY id DESC
            """)
            rows = cursor.fetchall()
            
            promocodes = []
            for row in rows:
                result = dict(row)
                # PostgreSQL DATE ni string'ga o'girish
                if result.get('expiry_date'):
                    result['expiry_date'] = str(result['expiry_date'])
                promocodes.append(result)
            
            return promocodes
        except Exception as e:
            logger.error(f"Promokodlarni olishda xatolik: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def delete_promocode(self, promo_id: int) -> bool:
        """Promokodni o'chirish (active = 0 qilish)"""
        return self.deactivate_promocode(promo_id)
    
    def get_setting(self, key: str, default: str = "") -> str:
        """Sozlama olish"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT value FROM settings WHERE key = %s", (key,))
            row = cursor.fetchone()
            
            return row[0] if row else default
        except Exception as e:
            logger.error(f"Sozlama olishda xatolik: {e}")
            return default
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def set_setting(self, key: str, value: str) -> bool:
        """Sozlama o'rnatish"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO settings (key, value) 
                VALUES (%s, %s)
                ON CONFLICT (key) DO UPDATE SET value = %s
            """, (key, value, value))
            
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Sozlama o'rnatishda xatolik: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def get_referal_count(self, telegram_id: int) -> int:
        """Referal sonini olish"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE invited_by = %s", (telegram_id,))
            result = cursor.fetchone()
            count = result[0] if result else 0
            return count
        except Exception as e:
            logger.error(f"Referal sonini olishda xatolik: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def get_all_users(self) -> List[int]:
        """Barcha foydalanuvchilar ID sini olish"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT telegram_id FROM users")
            result = cursor.fetchall()
            users = [row[0] for row in result if row]
            return users
        except Exception as e:
            logger.error(f"Foydalanuvchilarni olishda xatolik: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def mark_user_as_blocked(self, telegram_id: int) -> bool:
        """Foydalanuvchini blok deb belgilash"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("UPDATE users SET is_blocked = 1 WHERE telegram_id = %s", (telegram_id,))
            
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Foydalanuvchini blok deb belgilashda xatolik: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def unmark_user_as_blocked(self, telegram_id: int) -> bool:
        """Foydalanuvchini faol deb belgilash (unblock)"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("UPDATE users SET is_blocked = 0 WHERE telegram_id = %s", (telegram_id,))
            
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Foydalanuvchini faol deb belgilashda xatolik: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def get_statistics(self) -> Dict[str, int]:
        """Statistika olish"""
        conn = None
        cursor = None
        try:
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
            
            return {
                "total_users": total_users,
                "blocked_users": blocked_users,
                "kurs_ishlari": kurs_ishlari,
                "maqolalar": maqolalar,
                "total_orders": total_orders
            }
        except Exception as e:
            logger.error(f"Statistika olishda xatolik: {e}")
            return {
                "total_users": 0,
                "blocked_users": 0,
                "kurs_ishlari": 0,
                "maqolalar": 0,
                "total_orders": 0
            }
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def ban_user(self, telegram_id: int) -> bool:
        """Foydalanuvchini cheklash"""
        return self.mark_user_as_blocked(telegram_id)
    
    def unban_user(self, telegram_id: int) -> bool:
        """Foydalanuvchi cheklovini olib tashlash"""
        return self.unmark_user_as_blocked(telegram_id)
    
    def is_user_banned(self, telegram_id: int) -> bool:
        """Foydalanuvchi cheklangan yoki yo'qligini tekshirish"""
        user = self.get_user(telegram_id)
        if user:
            return user.get('is_blocked', 0) == 1
        return False
