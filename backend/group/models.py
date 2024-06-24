from backend.models.models import Column, Integer, Float, ForeignKey, String, Boolean, relationship, DateTime, db

db.Table('student_group',
         db.Column('student_id', db.Integer, db.ForeignKey('students.id')),
         db.Column('group_id', db.Integer, db.ForeignKey('groups.id'))
         )

db.Table('teacher_group',
         db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id')),
         db.Column('group_id', db.Integer, db.ForeignKey('groups.id'))
         )


class Groups(db.Model):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    level_id = Column(Integer, ForeignKey('subjectlevels.id'))
    course_type_id = Column(Integer, ForeignKey('coursetypes.id'))
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    teacher_salary = Column(Integer)
    location_id = Column(Integer, ForeignKey('locations.id'))
    status = Column(Boolean, default=False)
    education_language = Column(Integer, ForeignKey('educationlanguage.id'))
    calendar_day = Column(Integer, ForeignKey("calendarday.id"))
    attendance = relationship("Attendance", backref="group", order_by="Attendance.id")
    attendance_days = Column(Integer)
    attendance_history_student = relationship("AttendanceHistoryStudent", backref="group",
                                              order_by="AttendanceHistoryStudent.id")
    attendance_history_teacher = relationship("AttendanceHistoryTeacher", backref="group",
                                              order_by="AttendanceHistoryTeacher.id")
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    teacher_id = Column(Integer)
    charity = relationship('StudentCharity', backref="group", order_by="StudentCharity.id")
    history_group = relationship('StudentHistoryGroups', backref="group", order_by="StudentHistoryGroups.id")
    attendance_days_get = relationship("AttendanceDays", backref="group", order_by="AttendanceDays.id")

    deleted_teacher_salary = relationship("DeletedTeacherSalaries", backref="group",
                                          order_by="DeletedTeacherSalaries.id")
    price = Column(Integer)
    deleted = Column(Boolean, default=False)
    old_id = Column(Integer)
    deleted_from_group = relationship("DeletedStudents", backref="group", order_by="DeletedStudents.id", lazy="select")
    time_table = relationship("Group_Room_Week", backref="group", order_by="Group_Room_Week.id", lazy="select")
    certificate_url = Column(String)
    lesson_plan = relationship("LessonPlan", backref="group", order_by="LessonPlan.id", lazy="select")
    book_order = relationship("BookOrder", backref="group", order_by="BookOrder.id", lazy="select")
    observation = relationship("TeacherObservationDay", backref="group", order_by="TeacherObservationDay.id",
                               lazy='select')
    test = relationship("GroupTest", backref="group", order_by="GroupTest.id")
    student_tests = relationship("StudentTest", backref="group", order_by="StudentTest.id")

    def convert_json(self, entire=False):
        if not entire:
            info = {
                "id": self.id,
                "name": self.name,
                "students": len(self.student),
                "teacher__id": self.teacher_id,
                "student_list": []
            }
            for student in self.student:
                st_info = {
                    "id": student.id,
                    "name": student.user.name,
                    "surname": student.user.surname,
                }
                info['student_list'].append(st_info)
        else:

            info = {
                "id": self.id,
                "name": self.name,
                "teacher": {
                    "id": self.teacher_id,
                    "name": self.teacher[0].user.name,
                    "surname": self.teacher[0].user.surname,
                },
                "subject": self.subject.name
            }
        return info


class GroupReason(db.Model):
    __tablename__ = "group_reason"
    id = Column(Integer, primary_key=True)
    reason = Column(String)
    statistics = relationship("TeacherGroupStatistics", backref="group_reason", lazy="select",
                              order_by="TeacherGroupStatistics.id")
    deleted_students = relationship("DeletedStudents", backref="group_reason", lazy="select",
                                    order_by="DeletedStudents.id")

    def add(self):
        db.session.add(self)
        db.session.commit()

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "name": self.reason
        }


class AttendanceHistoryStudent(db.Model):
    __tablename__ = "attendancehistorystudent"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    total_debt = Column(Integer)
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))
    present_days = Column(Integer)
    absent_days = Column(Integer)
    average_ball = Column(Integer)
    payment = Column(Integer, default=0)
    remaining_debt = Column(Integer)
    location_id = Column(Integer, ForeignKey('locations.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    status = Column(Boolean, default=False)
    total_discount = Column(Integer)
    scored_days = Column(Integer)
    old_id = Column(Integer)


class AttendanceHistoryTeacher(db.Model):
    __tablename__ = "attendancehistoryteacher"
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    total_salary = Column(Integer)
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))
    taken_money = Column(Integer)
    remaining_salary = Column(Integer)
    location_id = Column(Integer, ForeignKey('locations.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    status = Column(Boolean, default=False)
    old_id = Column(Integer)


class Attendance(db.Model):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    student_id = Column(Integer, ForeignKey('students.id'))
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    course_id = Column(Integer, ForeignKey('coursetypes.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    attendance_days_get = relationship("AttendanceDays", backref="attendance", order_by="AttendanceDays.calendar_day")
    old_id = Column(Integer)
    ball_percentage = Column(Integer)


class AttendanceDays(db.Model):
    __tablename__ = "attendancedays"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    attendance_id = Column(Integer, ForeignKey('attendance.id'))
    calendar_day = Column(Integer, ForeignKey('calendarday.id'))
    status = Column(Integer, default=False)
    activeness = Column(Integer)
    dictionary = Column(Integer)
    homework = Column(Integer)
    average_ball = Column(Integer)
    balance_per_day = Column(Integer)
    salary_per_day = Column(Integer)
    balance_with_discount = Column(Integer)
    discount_per_day = Column(Integer)
    location_id = Column(Integer, ForeignKey('locations.id'))
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))
    reason = Column(String)
    discount = Column(Boolean, default=False)
    date = Column(DateTime)
    teacher_ball = Column(Integer)
    calling_status = Column(Boolean, default=False)
    calling_date = Column(DateTime)

    def convert_json(self, entire=False):
        if self.status == 1:
            status = True
        else:
            status = False
        return {
            "id": self.id,
            "day": self.day.date.strftime("%Y-%m-%d"),
            "homework": self.homework,
            "dictionary": self.dictionary,
            "activeness": self.activeness,
            "status": status,
            "student": {
                "id": self.student.id,
                "name": self.student.user.name,
                "surname": self.student.user.surname
            }
        }


class GroupTest(db.Model):
    __tablename__ = "group_test"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    group_id = Column(Integer, ForeignKey('groups.id'))
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    level = Column(String)
    number_tests = Column(Integer)
    calendar_year = Column(Integer, ForeignKey('calendaryear.id'))
    calendar_month = Column(Integer, ForeignKey('calendarmonth.id'))
    calendar_day = Column(Integer, ForeignKey('calendarday.id'))
    student_tests = relationship("StudentTest", backref="group_test", order_by="StudentTest.id")
    percentage = Column(Float, default=0)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "name": self.name,
            "date": self.day.date.strftime("%Y-%m-%d"),
            "day": self.day.date.strftime("%d"),
            "month": self.day.date.strftime("%m"),
            "year": self.day.date.strftime("%Y"),
            "students": [item.convert_json() for item in self.student_tests],
            "number": self.number_tests,
            "status": True if self.student_tests else False,
            "level": self.level,
            "percentage": self.percentage
        }
