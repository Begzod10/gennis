from backend.models.models import Column, Integer, ForeignKey, String, Boolean, relationship, DateTime, db


class Group_Room_Week(db.Model):
    __tablename__ = "group_room_week"
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'))
    room_id = Column(Integer, ForeignKey('rooms.id'))
    week_id = Column(Integer, ForeignKey('week.id'))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    location_id = Column(Integer, ForeignKey('locations.id'))


db.Table('time_table_student',
         db.Column("student_id", db.Integer, db.ForeignKey('students.id')),
         db.Column('group_room_week', db.Integer, db.ForeignKey('group_room_week.id'))
         )

db.Table('time_table_teacher',
         db.Column("teacher_id", db.Integer, db.ForeignKey('teachers.id')),
         db.Column('group_room_week', db.Integer, db.ForeignKey('group_room_week.id'))
         )


class Week(db.Model):
    __tablename__ = "week"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    eng_name = Column(String)
    location_id = Column(Integer, ForeignKey("locations.id"))
    order = Column(Integer)
    time_table = relationship("Group_Room_Week", backref="week", order_by="Group_Room_Week.id", lazy="select")
    old_id = Column(Integer)


db.Table('room_subject',
         db.Column('room_id', db.Integer, db.ForeignKey('rooms.id')),
         db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id'))
         )


class Rooms(db.Model):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    electronic_board = Column(Boolean)
    seats_number = Column(Integer)
    location_id = Column(Integer, ForeignKey("locations.id"))
    images = relationship("RoomImages", backref="room", order_by="RoomImages.id")
    time_table = relationship("Group_Room_Week", backref="room", order_by="Group_Room_Week.id", lazy="select")
    old_id = Column(Integer)


class RoomImages(db.Model):
    __tablename__ = "room_images"
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    photo_url = Column(String)
