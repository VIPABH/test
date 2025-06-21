# from sqlalchemy import create_engine, Column, Integer, String
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from datetime import datetime  # استيراد مكتبة datetime لتخزين الوقت

# DATABASE_URL = "sqlite:///db.sqlite3"
# engine = create_engine(DATABASE_URL, echo=False)

# Base = declarative_base()

# class Whisper(Base):
#     __tablename__ = 'whispers'

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     whisper_id = Column(String, unique=True)  # معرف فريد لكل همسة
#     sender_id = Column(Integer)
#     reciver_id = Column(Integer)
#     username = Column(String)
#     message = Column(String)
#     timestamp = Column(String)  # لتخزين الوقت الذي تم فيه إرسال الهمسة

# # دالة لحذف قاعدة البيانات القديمة وإعادة إنشاء الجداول من جديد
# def reset_database():
#     Base.metadata.drop_all(engine)  # حذف الجداول
#     Base.metadata.create_all(engine)  # إعادة إنشاء الجداول

# Session = sessionmaker(bind=engine)
# session = Session()

# def store_whisper(whisper_id, sender_id, reciver_id, username, message):
#     timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # الحصول على الوقت الحالي
#     whisper = Whisper(
#         whisper_id=whisper_id,
#         sender_id=sender_id,
#         reciver_id=reciver_id,
#         username=username,
#         message=message,
#         timestamp=timestamp  # تخزين الوقت
#     )
#     session.add(whisper)
#     session.commit()

# def get_whisper(whisper_id):
#     return session.query(Whisper).filter_by(whisper_id=whisper_id).first()
