from backend.models.models import Column, Integer, ForeignKey, String, relationship, db, Boolean


class PlatformNews(db.Model):
    __tablename__ = "platform_news"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    img = Column(String)
    text = Column(String)
    teachers = Column(Boolean)
    staff = Column(Boolean)
    students = Column(Boolean)
