# SQLite'dan PostgreSQL'ga O'tish Qo'llanmasi

## 📋 O'zgarishlar Ro'yxati

### 1. **Database Fayli**
- `database.py` (SQLite) → `database_postgresql.py` (PostgreSQL)
- Yoki `database.py` ni to'liq almashtirish

### 2. **Dependencies**
- `requirements.txt` ga `psycopg2-binary==2.9.9` qo'shildi

### 3. **Environment Variables**
- `.env` fayliga `DATABASE_URL` qo'shish kerak

### 4. **SQL Sintaksisi O'zgarishlari**
- `?` → `%s` (parameter placeholders)
- `AUTOINCREMENT` → `SERIAL`
- `INTEGER PRIMARY KEY AUTOINCREMENT` → `SERIAL PRIMARY KEY`
- `INSERT OR REPLACE` → `ON CONFLICT ... DO UPDATE`
- `cursor.lastrowid` → `RETURNING id`
- `PRAGMA` → PostgreSQL'da yo'q

## 🚀 O'tish Qadamlari

### Qadam 1: PostgreSQL Database Yaratish

**Railway'da:**
1. Railway Dashboard → **+ New** → **Database** → **PostgreSQL**
2. Database yaratilgandan keyin, **Variables** tab'ga o'ting
3. `DATABASE_URL` ni ko'ring va nusxalang

**Yoki mahalliy:**
```bash
# PostgreSQL o'rnatish (Linux)
sudo apt-get install postgresql postgresql-contrib

# Database yaratish
sudo -u postgres psql
CREATE DATABASE bot_database;
CREATE USER bot_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE bot_database TO bot_user;
\q
```

### Qadam 2: Environment Variable Qo'shish

`.env` fayliga qo'shing:
```env
DATABASE_URL=postgresql://user:password@host:port/database
```

**Railway uchun:**
Railway avtomatik ravishda `DATABASE_URL` ni yaratadi. Faqat environment variable sifatida qo'shing.

### Qadam 3: Database Faylini O'zgartirish

**Variant 1: To'liq almashtirish**
```bash
# Eski faylni backup qilish
cp database.py database_sqlite_backup.py

# PostgreSQL versiyasini o'rnatish
cp database_postgresql.py database.py
```

**Variant 2: Conditional Import (Ikkala versiyani qo'llab-quvvatlash)**
`database.py` faylini quyidagicha o'zgartirish:
```python
import os

# PostgreSQL yoki SQLite tanlash
if os.getenv("DATABASE_URL"):
    from database_postgresql import Database
else:
    from database_sqlite import Database  # Eski database.py ni database_sqlite.py ga ko'chirish
```

### Qadam 4: Ma'lumotlarni Ko'chirish (Migration)

Agar SQLite'da ma'lumotlar bo'lsa, ularni PostgreSQL'ga ko'chirish kerak:

```python
# migration_script.py
import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import os

# SQLite'dan o'qish
sqlite_conn = sqlite3.connect('bot_database.db')
sqlite_cursor = sqlite_conn.cursor()

# PostgreSQL'ga yozish
pg_conn = psycopg2.connect(os.getenv("DATABASE_URL"))
pg_cursor = pg_conn.cursor()

# Users jadvalini ko'chirish
sqlite_cursor.execute("SELECT * FROM users")
users = sqlite_cursor.fetchall()

for user in users:
    pg_cursor.execute("""
        INSERT INTO users (telegram_id, username, full_name, balance, referal_code, 
                          invited_by, register_date, is_blocked, active_promocode)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (telegram_id) DO NOTHING
    """, user[1:])  # id ni o'tkazib yuborish

# Xuddi shu qilib boshqa jadvallar uchun ham...

pg_conn.commit()
pg_cursor.close()
pg_conn.close()
sqlite_cursor.close()
sqlite_conn.close()
```

### Qadam 5: Test Qilish

```bash
# Dependencies o'rnatish
pip install -r requirements.txt

# Botni ishga tushirish
python main.py
```

## ⚠️ Muhim Eslatmalar

1. **Connection Pool**: PostgreSQL versiyasida connection pool ishlatiladi, bu yaxshi performance beradi.

2. **Transaction Management**: PostgreSQL'da har bir operatsiyadan keyin `commit()` yoki `rollback()` qilish kerak.

3. **Error Handling**: 
   - `sqlite3.IntegrityError` → `psycopg2.IntegrityError`
   - `sqlite3.OperationalError` → `psycopg2.OperationalError`

4. **Data Types**:
   - `TEXT` → `TEXT` yoki `VARCHAR(255)`
   - `INTEGER` → `INTEGER` yoki `BIGINT`
   - `TIMESTAMP` → PostgreSQL'da `TIMESTAMP` ishlatiladi

5. **Railway'da**: Railway PostgreSQL database yaratganda, avtomatik ravishda `DATABASE_URL` environment variable yaratiladi.

## 🔄 Geri Qaytish

Agar muammo bo'lsa, eski SQLite versiyasiga qaytish:
```bash
cp database_sqlite_backup.py database.py
# .env dan DATABASE_URL ni olib tashlash
```

## 📊 Performance Taqqoslash

- **SQLite**: Kichik loyihalar uchun, fayl-based
- **PostgreSQL**: Katta loyihalar uchun, server-based, parallel queries, connection pooling

## ✅ Checklist

- [ ] PostgreSQL database yaratildi
- [ ] `DATABASE_URL` environment variable qo'shildi
- [ ] `psycopg2-binary` o'rnatildi
- [ ] `database.py` yangilandi
- [ ] Ma'lumotlar ko'chirildi (agar kerak bo'lsa)
- [ ] Test qilindi
- [ ] Production'ga deploy qilindi

