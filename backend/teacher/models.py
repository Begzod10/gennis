import pprint

from backend.models.models import Column, Integer, ForeignKey, String, relationship, DateTime, db, desc, contains_eager
from backend.student.models import Students
from backend.group.models import Groups


class Teachers(db.Model):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    subject = relationship('Subjects', secondary="teacher_subject", backref="teacher", order_by="Subjects.id")
    group = relationship('Groups', secondary="teacher_group", backref="teacher", order_by="Groups.id")
    attendance = relationship("Attendance", backref="teacher", order_by="Attendance.id")
    attendance_history = relationship("AttendanceHistoryTeacher", backref="teacher",
                                      order_by="AttendanceHistoryTeacher.id")
    attendance_location = relationship("TeacherSalary", backref="teacher", order_by="TeacherSalary.id")
    history_group = relationship('StudentHistoryGroups', backref="teacher", order_by="StudentHistoryGroups.id")
    teacher_cash = relationship('TeacherSalaries', backref="teacher", order_by="TeacherSalaries.id")
    deleted_teacher_salaries = relationship("DeletedTeacherSalaries", backref="teacher",
                                            order_by="DeletedTeacherSalaries.id")
    attendance_days_get = relationship("AttendanceDays", backref="teacher", order_by="AttendanceDays.id")
    deleted = relationship("DeletedTeachers", backref="teacher", order_by="DeletedTeachers.id")
    old_id = Column(Integer)
    locations = relationship("Locations", secondary="teacher_locations", backref="teacher", order_by="Locations.id")
    deleted_from_group = relationship("DeletedStudents", backref="teacher", order_by="DeletedStudents.id",
                                      lazy="select")
    time_table = relationship("Group_Room_Week", secondary="time_table_teacher", backref="teacher",
                              order_by="Group_Room_Week.id",
                              lazy="select")
    table_color = Column(String)
    lesson_plan = relationship("LessonPlan", backref="teacher", order_by="LessonPlan.id", lazy="select")
    book_order = relationship("BookOrder", backref="teacher", order_by="BookOrder.id", lazy="select")
    observation = relationship("TeacherObservationDay", backref="teacher", order_by="TeacherObservationDay.id",
                               lazy='select')

    black_salary = relationship("TeacherBlackSalary", backref="teacher", order_by="TeacherBlackSalary.id",
                                lazy="select")
    student_certificate = relationship("StudentCertificate", backref="teacher", order_by="StudentCertificate.id")
    total_students = Column(Integer)

    def convert_json(self, entire=False):
        return {
            "info": self.user.convert_json(entire=True)
        }


db.Table('teacher_locations',
         db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id')),
         db.Column('location_id', db.Integer, db.ForeignKey('locations.id'))
         )


class DeletedTeachers(db.Model):
    __tablename__ = "deletedteachers"
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id'))  # relationship qilinmagan
    reason = Column(String)
    calendar_day = Column(Integer, ForeignKey("calendarday.id"))  # relationship qilinmagan


class LessonPlan(db.Model):
    __tablename__ = "lesson_plan"
    id = Column(Integer, primary_key=True)
    objective = Column(String)
    main_lesson = Column(String)
    homework = Column(String)
    assessment = Column(String)
    activities = Column(String)
    resources = Column(String)
    date = Column(DateTime)
    updated_date = Column(DateTime)
    group_id = Column(Integer, ForeignKey('groups.id'))
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    students = relationship("LessonPlanStudents", backref="lesson_plan", order_by="LessonPlanStudents.id",
                            lazy="select")

    def add(self):
        db.session.add(self)
        db.session.commit()

    def convert_json(self, entire=False):
        students = db.session.query(Students).join(Students.group).options(
            contains_eager(Students.group)).filter(
            Groups.id == self.group_id).order_by(Students.id).all()

        info = {
            "id": self.id,
            "objective": self.objective,
            "main_lesson": self.main_lesson,
            "homework": self.homework,
            "assessment": self.assessment,
            "activities": self.activities,
            "resources": self.resources,
            "date": self.date.strftime("%Y-%m-%d"),
            "day": self.date.strftime("%d"),
            "month": self.date.strftime("%m"),
            "year": self.date.strftime("%Y"),
            "group": {
                "id": self.group.id,
                "name": self.group.name
            },
            "teacher": {
                "id": self.teacher.user.id,
                "name": self.teacher.user.name
            },
            "students": []
        }
        if self.students:
            for student in self.students:
                info['students'].append(student.convert_json())
            pprint.pprint(info['students'])
            if len(self.students) != len(students):
                students = db.session.query(Students).join(Students.group).options(
                    contains_eager(Students.group)).filter(
                    Groups.id == self.group_id, ~Students.id.in_([st.student.id for st in self.students])).order_by(
                    Students.id).all()
                for student in students:
                    student_info = {
                        "comment": "",
                        "student": {
                            "id": student.id,
                            "name": student.user.name,
                            "surname": student.user.surname
                        }
                    }
                    info['students'].append(student_info)
        else:
            for student in students:
                student_info = {
                    "comment": "",
                    "student": {
                        "id": student.id,
                        "name": student.user.name,
                        "surname": student.user.surname
                    }
                }
                info['students'].append(student_info)
        return info

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class LessonPlanStudents(db.Model):
    __tablename__ = "lesson_plan_students"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    comment = Column(String)
    lesson_plan_id = Column(Integer, ForeignKey('lesson_plan.id'))

    def convert_json(self, entire=False):
        return {
            "comment": self.comment,
            "student": {
                "id": self.student.id,
                "name": self.student.user.name,
                "surname": self.student.user.surname
            }
        }

    def add(self):
        db.session.add(self)
        db.session.commit()


class ObservationInfo(db.Model):
    __tablename__ = "observation_info"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    teacher = relationship("TeacherObservation", backref="observation", order_by="TeacherObservation.id", lazy="select")

    def add(self):
        db.session.add(self)
        db.session.commit()

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "title": self.title,
        }


class ObservationOptions(db.Model):
    __tablename__ = "observation_options"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    value = Column(Integer)
    teacher = relationship("TeacherObservation", backref="observation_option", order_by="TeacherObservation.id",
                           lazy="select")

    def add(self):
        db.session.add(self)
        db.session.commit()

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "name": self.name,
            "value": self.value
        }


class TeacherObservationDay(db.Model):
    __tablename__ = "teacher_observation_day"
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'))
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    calendar_day = Column(Integer, ForeignKey("calendarday.id"))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey('calendaryear.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    average = Column(Integer, default=0)

    def add(self):
        db.session.add(self)
        db.session.commit()


class TeacherObservation(db.Model):
    __tablename__ = "teacher_observation"
    id = Column(Integer, primary_key=True)
    observation_info_id = Column(Integer, ForeignKey('observation_info.id'))
    observation_options_id = Column(Integer, ForeignKey('observation_options.id'))
    comment = Column(String)
    observation_id = Column(Integer, ForeignKey('teacher_observation_day.id'))

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "group": self.group.convert_json(),
            "observer": self.user.convert_json(entire=True),
            "day": self.day.convert_json(),
            "average": self.average,
            "comment": self.comment
        }

    def add(self):
        db.session.add(self)
        db.session.commit()


class TeacherGroupStatistics(db.Model):
    __tablename__ = "teacher_group_statistics"
    id = Column(Integer, primary_key=True)
    number_students = Column(Integer)
    updated_data = Column(Integer, ForeignKey("calendarday.id"))
    reason_id = Column(Integer, ForeignKey('group_reason.id'))
    calendar_month = Column(Integer, ForeignKey('calendarmonth.id'))
    calendar_year = Column(Integer, ForeignKey('calendaryear.id'))
    percentage = Column(Integer)
    teacher_id = Column(Integer, ForeignKey('teachers.id'))

    def convert_json(self):
        return {
            "id": self.id,
            "number_students": self.number_students,
            "updated_data": self.day.date.strftime("%Y-%m-%d"),
            "month": self.month.date.strftime("%Y-%m"),
            "year": self.month.date.strftime("%Y"),
            "reason": self.group_reason.reason,
            "percentage": self.percentage
        }

    def add(self):
        db.session.add(self)
        db.session.commit()
