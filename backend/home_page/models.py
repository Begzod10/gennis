from backend.models.models import Column, Integer, ForeignKey, String, relationship, db, Date


class Link(db.Model):
    __tablename__ = "link"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    link = Column(String)
    img = Column(String)

    def convert_json(self, entire=False):
        info = {
            'id': self.id,
            'name': self.name,
            'link': self.link,
            'img': self.img,
        }
        return info


class TeacherData(db.Model):
    __tablename__ = "teacher_data"
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    text = Column(String)
    telegram = Column(String)
    instagram = Column(String)
    facebook = Column(String)
    img = Column(String)

    def convert_json(self, entire=False):
        info = {
            'text': self.text,
            'telegram': self.telegram,
            'instagram': self.instagram,
            'facebook': self.facebook,
            'certificate': self.img,
        }
        return info

    def json2(self):
        info = {
            'telegram': self.telegram,
            'instagram': self.instagram,
            'facebook': self.facebook,
        }
        return info


class StudentCertificate(db.Model):
    __tablename__ = "student_certificate"
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))
    date = Column(Date)
    text = Column(String)
    student_id = Column(Integer, ForeignKey('students.id'))
    img = Column(String)

    def convert_json(self, entire=False):
        info = {
            'id': self.id,
            'text': self.text,
            'student_name': self.student.user.name,
            'student_surname': self.student.user.surname,
            'teacher_name': self.teacher.user.name,
            'teacher_surname': self.teacher.user.surname,
            'group_id': self.group_id,
            'student_id': self.student.user.id,
            'teacher_id': self.teacher.user.id,
            'img': self.img,
            "student_img": self.student.user.photo_profile
        }
        return info


class News(db.Model):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    date = Column(Date)
    description = Column(String)
    links = relationship('NewsLink', backref="news", order_by="NewsLink.id", lazy="select")
    images = relationship('NewsImg', backref="news", order_by="NewsImg.id", lazy="select")

    def convert_json(self, entire=False):
        link_list = []
        for link in self.links:
            link_list.append(link.convert_json())
        files = []
        for img in self.images:
            files.append(img.convert_json())
        info = {
            'id': self.id,
            'title': self.title,
            'date': self.date.strftime('%Y-%m-%d'),
            'text': self.description,
            'links': link_list,
            'images': files
        }
        return info


class NewsLink(db.Model):
    __tablename__ = "news_link"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    link = Column(String)
    news_id = Column(Integer, ForeignKey('news.id'))

    def convert_json(self, entire=False):
        info = {
            'id': self.id,
            'name': self.name,
            'link': self.link
        }
        return info


class NewsImg(db.Model):
    __tablename__ = "news_img"
    id = Column(Integer, primary_key=True)
    url = Column(String)
    new_id = Column(Integer, ForeignKey('news.id'))

    def convert_json(self, entire=False):
        info = {
            'id': self.id,
            'url': self.url
        }
        return info


class HomeDesign(db.Model):
    __tablename__ = "home_design"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    text = Column(String)
    img = Column(String)

    def convert_json(self, entire=False):
        info = {
            'name': self.name,
            'text': self.text,
            'img': self.img
        }
        return info


class HomeVideo(db.Model):
    __tablename__ = "home_video"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    text = Column(String)
    url = Column(String)

    def convert_json(self, entire=False):
        info = {
            'name': self.name,
            'text': self.text,
            'url': self.url,
        }
        return info


class Advantages(db.Model):
    id = Column(Integer, primary_key=True)
    __tablename__ = "advantages"
    name = Column(String)
    text = Column(String)
    img = Column(String)

    def convert_json(self, entire=False):
        return {
            'id': self.id,
            'name': self.name,
            'img': self.img,
            'text': self.text
        }


class Comments(db.Model):
    id = Column(Integer, primary_key=True)
    __tablename__ = "comments"
    comment = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    likes = relationship('CommentLikes', backref="comment", order_by="CommentLikes.id")
    old_id = Column(Integer)


class CommentLikes(db.Model):
    id = Column(Integer, primary_key=True)
    __tablename__ = "commentlikes"
    user_id = Column(Integer, ForeignKey('users.id'))
    comment_id = Column(Integer, ForeignKey('comments.id'))


class Gallery(db.Model):
    id = Column(Integer, primary_key=True)
    __tablename__ = "gallery"
    img = Column(String)
