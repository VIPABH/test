from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
import os

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("متغير البيئة 'DATABASE_URL' غير موجود. تأكد من تعيينه بشكل صحيح.")

if DATABASE_URL.startswith('postgresql://'):
    engine = create_engine(DATABASE_URL, echo=False)
    BASE = declarative_base()
    SessionLocal = sessionmaker(bind=engine)
    SESSION = SessionLocal()

else:
    raise ValueError("رابط قاعدة البيانات غير صالح أو غير مدعوم. تأكد من أنه PostgreSQL.")
