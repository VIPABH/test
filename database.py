# from sqlalchemy.orm import Session
# from models import SessionLocal, AllowedUser

# # إضافة مستخدم إلى قاعدة البيانات
# def add_user_to_db(user_id: int):
#     db = SessionLocal()
#     try:
#         user = AllowedUser(user_id=user_id)
#         db.add(user)
#         db.commit()
#     except Exception as e:
#         db.rollback()
#         raise e
#     finally:
#         db.close()

# # التحقق من وجود مستخدم في قاعدة البيانات
# def is_user_allowed(user_id: int) -> bool:
#     db = SessionLocal()
#     try:
#         user = db.query(AllowedUser).filter(AllowedUser.user_id == user_id).first()
#         return user is not None
#     finally:
#         db.close()

# # حذف مستخدم من قاعدة البيانات
# def delete_user_from_db(user_id: int):
#     db = SessionLocal()
#     try:
#         user = db.query(AllowedUser).filter(AllowedUser.user_id == user_id).first()
#         if user:
#             db.delete(user)
#             db.commit()
#             return True
#         return False
#     except Exception as e:
#         db.rollback()
#         raise e
#     finally:
#         db.close()

# # جلب جميع المستخدمين المسموح لهم مع الوقت
# def get_allowed_users():
#     db = SessionLocal()
#     try:
#         users = db.query(AllowedUser).all()
#         return users
#     finally:
#         db.close()
