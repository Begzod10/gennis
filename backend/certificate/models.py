from backend.models.models import Column, Integer, ForeignKey, String,  DateTime, db



class Certificate(db.Model):
    __tablename__ = "certificate"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    certificate_id_number = Column(String)
    level_id = Column(Integer, ForeignKey('certificate_level.id'))
    ball = Column(Integer)
    link = Column(String)
    date = Column(DateTime)


class CertificateLevels(db.Model):
    __tablename__ = "certificate_level"
    id = Column(Integer, primary_key=True)
    name = Column(String)


class CertificateLinks(db.Model):
    __tablename__ = "certificate_links"
    id = Column(Integer, primary_key=True)
    link = Column(String)
    group_id = Column(Integer, ForeignKey("groups.id"))
