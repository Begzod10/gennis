from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import String, Integer, Boolean, Float, Column, ForeignKey, DateTime, or_, and_, desc, func, ARRAY, \
    JSON, \
    extract, Date, BigInteger
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, functions
from pprint import pprint
import uuid

db = SQLAlchemy()


# app.config['SQLALCHEMY_ECO'] = True
# lazy = "dynamic" -> bu relationship bugan table lani 2 tarafdan , filter, order  qb beradi va misol uchun child table orqali parentni ozgartirsa boladi yoki teskarisi
# lazy = "select" -> bu relationship bugan table lani aloxida query qb beradi
# lazy = "joined" -> bu relationship bugan table lani bittada hammasini query qb beradi
# lazy = "subquery" -> "joined" ga oxshidi test qlib iwltib koriw kere farqi tezligida bolishi mumkin
def db_setup(app):
    app.config.from_object('backend.models.config')
    db.app = app
    db.init_app(app)
    Migrate(app, db)
    return db


from backend.home_page.models import *
from backend.account.models import *
from backend.time_table.models import *
from backend.group.models import *
from backend.student.models import *
from backend.teacher.models import *
from backend.certificate.models import *
from backend.book.models import *
from backend.lead.models import *
from backend.for_programmers.models import *
from backend.tasks.models.models import *





class CalendarYear(db.Model):
    __tablename__ = "calendaryear"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    users = db.relationship("Users", backref="year", order_by="Users.id")
    groups = db.relationship("Groups", backref="year", order_by="Groups.id")
    attendance_history_student = relationship("AttendanceHistoryStudent", backref="year",
                                              order_by="AttendanceHistoryStudent.id")
    attendance_history_teacher = relationship("AttendanceHistoryTeacher", backref="year",
                                              order_by="AttendanceHistoryTeacher.id")
    month = relationship("CalendarMonth", backref="year", order_by="CalendarMonth.id")
    accounting_period = relationship("AccountingPeriod", backref="year", order_by="AccountingPeriod.id")
    teacher_salary_id = relationship("TeacherSalary", backref="year", order_by="TeacherSalary.id")
    attendance = relationship("Attendance", backref="year", order_by="Attendance.id")
    location = relationship('Locations', backref="year", order_by="Locations.id")
    student_payment = relationship('StudentPayments', backref="year", order_by="StudentPayments.id")
    teacher_cash = relationship('TeacherSalaries', backref="year", order_by="TeacherSalaries.id")
    charity = relationship('StudentCharity', backref="year", order_by="StudentCharity.id")
    stuff_salary = relationship('StaffSalary', backref="year", order_by="StaffSalary.id")
    staff_given_salary = relationship("StaffSalaries", backref="year", order_by="StaffSalaries.id")
    overhead_data = relationship('Overhead', backref="year", order_by="Overhead.id")
    accounting = relationship("AccountingInfo", backref="year", order_by="AccountingInfo.id")
    deleted_payments = relationship("DeletedStudentPayments", backref="year", order_by="DeletedStudentPayments.id")
    deleted_teacher_salaries = relationship("DeletedTeacherSalaries", backref="year",
                                            order_by="DeletedTeacherSalaries.id")
    staff_deleted_salary = relationship("DeletedStaffSalaries", backref="year", order_by="DeletedStaffSalaries.id")
    book_overhead = relationship("BookOverhead", backref="year", lazy="select", order_by="BookOverhead.id")
    center_balances = relationship("CenterBalance", backref="year", lazy="select", order_by="CenterBalance.id")
    center_balances_overheads = relationship("CenterBalanceOverhead", backref="year", lazy="select",
                                             order_by="CenterBalanceOverhead.id")
    editor_balances = relationship("EditorBalance", backref="year", lazy="select", order_by="EditorBalance.id")
    book_debts = relationship("CollectedBookPayments", backref="year", lazy="select",
                              order_by="CollectedBookPayments.id")
    observation = relationship("TeacherObservationDay", backref="year",
                               order_by="TeacherObservationDay.id",
                               lazy='select')
    black_salary = relationship("TeacherBlackSalary", backref="year", order_by="TeacherBlackSalary.id",
                                lazy="select")
    teacher_group_statistics = relationship("TeacherGroupStatistics", backref="year",
                                            order_by="TeacherGroupStatistics.id",
                                            lazy="select")
    capitals = relationship("Capital", backref="year", lazy="select", order_by="Capital.id")
    test = relationship("GroupTest", backref="year", order_by="GroupTest.id")

    capital_term = relationship("CapitalTerm", backref="year", order_by="CapitalTerm.id", lazy="select")
    tasks_statistics = relationship("TasksStatistics", backref="year", order_by='TasksStatistics.id')
    tasks_daily_statistics = relationship("TaskDailyStatistics", backref="year", order_by='TaskDailyStatistics.id')

    # student_tests = relationship("StudentTest", backref="year", order_by="StudentTest.id")

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "value": self.date.strftime("%Y")
        }


class CalendarMonth(db.Model):
    __tablename__ = "calendarmonth"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    users = db.relationship("Users", backref="month", order_by="Users.id")
    groups = db.relationship("Groups", backref="month", order_by="Groups.id")
    attendance_history_student = relationship("AttendanceHistoryStudent", backref="month",
                                              order_by="AttendanceHistoryStudent.id")
    attendance_history_teacher = relationship("AttendanceHistoryTeacher", backref="month",
                                              order_by="AttendanceHistoryTeacher.id")
    accounting_period = relationship("AccountingPeriod", backref="month", order_by="AccountingPeriod.id")
    teacher_salary_id = relationship("TeacherSalary", backref="month", order_by="TeacherSalary.id")
    year_id = Column(Integer, ForeignKey('calendaryear.id'))
    day = relationship('CalendarDay', backref="month", order_by="CalendarDay.id")
    attendance = relationship("Attendance", backref="month", order_by="Attendance.id")
    location = relationship('Locations', backref="month", order_by="Locations.id")
    student_payment = relationship('StudentPayments', backref="month", order_by="StudentPayments.id")
    teacher_cash = relationship('TeacherSalaries', backref="month", order_by="TeacherSalaries.id")
    charity = relationship('StudentCharity', backref="month", order_by="StudentCharity.id")
    stuff_salary = relationship('StaffSalary', backref="month", order_by="StaffSalary.id")
    staff_given_salary = relationship("StaffSalaries", backref="month", order_by="StaffSalaries.id")
    overhead_data = relationship('Overhead', backref="month", order_by="Overhead.id")
    # accounting = relationship("AccountingInfo", backref="month", order_by="AccountingInfo.id")
    deleted_payments = relationship("DeletedStudentPayments", backref="month", order_by="DeletedStudentPayments.id")
    deleted_teacher_salaries = relationship("DeletedTeacherSalaries", backref="month",
                                            order_by="DeletedTeacherSalaries.id")
    staff_deleted_salary = relationship("DeletedStaffSalaries", backref="month", order_by="DeletedStaffSalaries.id")
    old_id = Column(Integer)
    book_overhead = relationship("BookOverhead", backref="month", lazy="select", order_by="BookOverhead.id")
    center_balances = relationship("CenterBalance", backref="month", lazy="select", order_by="CenterBalance.id")
    center_balances_overheads = relationship("CenterBalanceOverhead", backref="month", lazy="select",
                                             order_by="CenterBalanceOverhead.id")
    editor_balances = relationship("EditorBalance", backref="month", lazy="select", order_by="EditorBalance.id")
    book_debts = relationship("CollectedBookPayments", backref="month", lazy="select",
                              order_by="CollectedBookPayments.id")
    observation = relationship("TeacherObservationDay", backref="month",
                               order_by="TeacherObservationDay.id",
                               lazy='select')
    black_salary = relationship("TeacherBlackSalary", backref="month", order_by="TeacherBlackSalary.id",
                                lazy="select")
    teacher_group_statistics = relationship("TeacherGroupStatistics", backref="month",
                                            order_by="TeacherGroupStatistics.id",
                                            lazy="select")
    capitals = relationship("Capital", backref="month", lazy="select", order_by="Capital.id")
    test = relationship("GroupTest", backref="month", order_by="GroupTest.id")

    capital_term = relationship("CapitalTerm", backref="month", order_by="CapitalTerm.id", lazy="select")
    tasks_statistics = relationship("TasksStatistics", backref="month", order_by='TasksStatistics.id')
    tasks_daily_statistics = relationship("TaskDailyStatistics", backref="month", order_by='TaskDailyStatistics.id')

    # student_tests = relationship("StudentTest", backref="month", order_by="StudentTest.id")

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "month": self.date.strftime("%m"),
            "year": self.date.strftime("%Y"),
            "date": self.date
        }


class AccountingPeriod(db.Model):
    __tablename__ = "accountingperiod"
    id = Column(Integer, primary_key=True)
    from_date = Column(DateTime)
    to_date = Column(DateTime)
    student_payments = relationship("StudentPayments", backref="period", order_by="StudentPayments.id", lazy="select")
    deleted_payments = relationship("DeletedStudentPayments", backref="period", order_by="DeletedStudentPayments.id")
    teacher_salaries = relationship("TeacherSalaries", backref="period", order_by="TeacherSalaries.id")
    staff_salaries = relationship("StaffSalaries", backref="period", order_by="StaffSalaries.id")
    overhead = relationship("Overhead", backref="period", order_by="Overhead.id")
    capital = relationship("CapitalExpenditure", backref="period", order_by="CapitalExpenditure.id")
    day = relationship('CalendarDay', backref="period", order_by="CalendarDay.id")
    charity = relationship('StudentCharity', backref="period", order_by="StudentCharity.id")
    year_id = Column(Integer, ForeignKey('calendaryear.id'))
    month_id = Column(Integer, ForeignKey('calendarmonth.id'))
    deleted_teacher_salaries = relationship("DeletedTeacherSalaries", backref="period",
                                            order_by="DeletedTeacherSalaries.id")
    staff_deleted_salary = relationship("DeletedStaffSalaries", backref="period", order_by="DeletedStaffSalaries.id")
    old_id = Column(Integer)
    accounting = relationship("AccountingInfo", backref="period", order_by="AccountingInfo.id")
    book_overhead = relationship("BookOverhead", backref="period", lazy="select", order_by="BookOverhead.id")
    center_balances = relationship("CenterBalance", backref="period", lazy="select", order_by="CenterBalance.id")
    center_balances_overheads = relationship("CenterBalanceOverhead", backref="period", lazy="select",
                                             order_by="CenterBalanceOverhead.id")
    editor_balances = relationship("EditorBalance", backref="period", lazy="select", order_by="EditorBalance.id")
    book_debts = relationship("CollectedBookPayments", backref="period", lazy="select",
                              order_by="CollectedBookPayments.id")
    capitals = relationship("Capital", backref="period", lazy="select", order_by="Capital.id")
    capital_term = relationship("CapitalTerm", backref="period", order_by="CapitalTerm.id", lazy="select")


class CalendarDay(db.Model):
    __tablename__ = "calendarday"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    month_id = Column(Integer, ForeignKey('calendarmonth.id'))
    users = db.relationship("Users", backref="day", order_by="Users.id")
    groups = db.relationship("Groups", backref="day", order_by="Groups.id")
    attendance = relationship("AttendanceDays", backref="day", order_by="AttendanceDays.id")
    location = relationship('Locations', backref="day", order_by="Locations.id")
    student_payment = relationship('StudentPayments', backref="day", order_by="StudentPayments.id")
    teacher_cash = relationship('TeacherSalaries', backref="day", order_by="TeacherSalaries.id")
    charity = relationship('StudentCharity', backref="day", order_by="StudentCharity.id")
    staff_given_salary = relationship("StaffSalaries", backref="day", order_by="StaffSalaries.id")
    overhead_data = relationship('Overhead', backref="day", order_by="Overhead.id")
    capital_data = relationship('CapitalExpenditure', backref="day", order_by="CapitalExpenditure.id")
    deleted_capital_data = relationship("DeletedCapitalExpenditure", backref="day",
                                        order_by="DeletedCapitalExpenditure.id")
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))
    deleted_payments = relationship("DeletedStudentPayments", backref="day", order_by="DeletedStudentPayments.id")
    deleted_teacher_salaries = relationship("DeletedTeacherSalaries", backref="day",
                                            order_by="DeletedTeacherSalaries.id")
    staff_deleted_salary = relationship("DeletedStaffSalaries", backref="day", order_by="DeletedStaffSalaries.id")
    qr_students_link = relationship("QR_students", backref="day", order_by="QR_students.id")
    deleted_from_group = relationship("DeletedStudents", backref="day", order_by="DeletedStudents.id", lazy="select")
    deleted_reg_students = relationship("RegisterDeletedStudents", backref="day", order_by="RegisterDeletedStudents.id",
                                        lazy="select")
    reasons = relationship("Debtor_Reasons", backref="day", order_by="Debtor_Reasons.id", lazy="select")
    book_payments = relationship('BookPayments', backref='day', order_by='BookPayments.id', lazy='select')
    del_book_payments = relationship("DeletedBookPayments", backref='day', order_by='DeletedBookPayments.id',
                                     lazy='select')
    book_order = relationship("BookOrder", backref="day", order_by="BookOrder.id", lazy="select")
    old_id = Column(Integer)
    book_overhead = relationship("BookOverhead", backref="day", lazy="select", order_by="BookOverhead.id")
    center_balances_overheads = relationship("CenterBalanceOverhead", backref="day", lazy="select",
                                             order_by="CenterBalanceOverhead.id")
    user_books = relationship("UserBooks", backref="day", lazy="select", order_by="UserBooks.id")
    branch_payment = relationship("BranchPayment", backref="day", lazy="select", order_by="BranchPayment.id")
    observation = relationship("TeacherObservationDay", backref="day", order_by="TeacherObservationDay.id",
                               lazy='select')
    leads = relationship("Lead", backref="day", order_by="Lead.id", lazy='select')

    teacher_group_statistics = relationship("TeacherGroupStatistics", backref="day",
                                            order_by="TeacherGroupStatistics.id", lazy="select")
    capitals = relationship("Capital", backref="day", lazy="select", order_by="Capital.id")
    test = relationship("GroupTest", backref="day", order_by="GroupTest.id")

    tasks_statistics = relationship("TasksStatistics", backref="day", order_by='TasksStatistics.id')
    tasks_daily_statistics = relationship("TaskDailyStatistics", backref="day", order_by='TaskDailyStatistics.id')

    student_tests = relationship("StudentTest", backref="day", order_by="StudentTest.id")

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "day": self.date.strftime("%d"),
            "month": self.date.strftime("%m"),
            "year": self.date.strftime("%Y"),
        }


class Locations(db.Model):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    number_location = Column(String)
    location = Column(String)
    link = Column(String)
    code = Column(Integer)
    director_fio = Column(String)
    location_type = Column(String)
    district = Column(String)
    bank_sheet = Column(String)
    inn = Column(String)
    bank = Column(String)
    mfo = Column(String)
    campus_name = Column(String)
    address = Column(String)
    users = relationship('Users', backref="location", order_by="Users.id")
    groups = relationship("Groups", backref="location", order_by="Groups.id")
    attendance = relationship("Attendance", backref="location", order_by="Attendance.id")
    attendance_student = relationship("AttendanceHistoryStudent", backref="location",
                                      order_by="AttendanceHistoryStudent.id")
    attendance_teacher = relationship("AttendanceHistoryTeacher", backref="location",
                                      order_by="AttendanceHistoryTeacher.id")
    student_payment = relationship('StudentPayments', backref="location", order_by="StudentPayments.id")
    teacher_cash = relationship('TeacherSalaries', backref="location", order_by="TeacherSalaries.id")
    attendance_location = relationship("TeacherSalary", backref="location", order_by="TeacherSalary.id")
    stuff_salary = relationship('StaffSalary', backref="location", order_by="StaffSalary.id")
    staff_given_salary = relationship("StaffSalaries", backref="location", order_by="StaffSalaries.id")
    calendar_day = Column(Integer, ForeignKey("calendarday.id"))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    overhead_data = relationship('Overhead', backref="location", order_by="Overhead.id")
    contract_students_data = relationship('Contract_Students_Data', backref="location",
                                          order_by="Contract_Students_Data.id")
    attendance_days_get = relationship("AttendanceDays", backref="location", order_by="AttendanceDays.id")
    accounting = relationship("AccountingInfo", backref="location", order_by="AccountingInfo.id")
    charity = relationship('StudentCharity', backref="location", order_by="StudentCharity.id")
    deleted_payments = relationship("DeletedStudentPayments", backref="location", order_by="DeletedStudentPayments.id")
    deleted_teacher_salaries = relationship("DeletedTeacherSalaries", backref="location",
                                            order_by="DeletedTeacherSalaries.id")
    staff_deleted_salary = relationship("DeletedStaffSalaries", backref="location", order_by="DeletedStaffSalaries.id")
    time_table = relationship("Group_Room_Week", backref="location", order_by="Group_Room_Week.id", lazy="select")
    book_order = relationship("BookOrder", backref="location", order_by="BookOrder.id", lazy="select")
    old_id = Column(Integer)
    center_balances = relationship("CenterBalance", backref="location", lazy="select", order_by="CenterBalance.id")
    tasks_statistics = relationship("TasksStatistics", backref="location", order_by="TasksStatistics.id")
    tasks_daily_statistics = relationship("TaskDailyStatistics", backref="location", order_by='TaskDailyStatistics.id')

    def convert_json(self, entire=False):
        return {
            "value": self.id,
            "name": self.name,
            "number_location": self.number_location,
            "location": self.location,
            "link": self.link,
            "code": self.code,
            "director_fio": self.director_fio,
            "location_type": self.location_type,
            "district": self.district,
            "bank_sheet": self.bank_sheet,
            "inn": self.inn,
            "bank": self.bank,
            "mfo": self.mfo,
            "campus_name": self.campus_name,
            "address": self.address

        }


# class Branch(db.Model):
#     __tablename__ = "branch"
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     cost =


class QR_students(db.Model):
    __tablename__ = "qr_students"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    phone = Column(Integer)
    winning_amount = Column(Integer)
    calendar_day = Column(Integer, ForeignKey("calendarday.id"))


class QR_sum(db.Model):
    __tablename__ = "qr_sum"
    id = Column(Integer, primary_key=True)
    sum = Column(Integer)


class EducationLanguage(db.Model):
    __tablename__ = "educationlanguage"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    user = relationship("Users", backref="language", order_by="Users.id")
    groups = relationship("Groups", backref="language", order_by="Groups.id")
    old_id = Column(Integer)


class Users(db.Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey('locations.id'))
    password = Column(String, nullable=False)
    student = relationship("Students", uselist=False, backref="user", order_by="Students.id")
    teacher = relationship("Teachers", uselist=False, backref='user', order_by="Teachers.id")
    phone = relationship("PhoneList", backref='user', order_by="PhoneList.id")
    education_language = Column(Integer, ForeignKey('educationlanguage.id'))
    staff = relationship("Staff", backref="user", order_by="Staff.id")
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    username = Column(String)
    user_id = Column(String)
    director = Column(Boolean)
    photo_profile = Column(String)
    born_day = Column(Integer)
    born_month = Column(Integer)
    born_year = Column(Integer)
    age = Column(Integer)
    comment = Column(String)
    father_name = Column(String)
    balance = Column(Integer)
    calendar_day = Column(Integer, ForeignKey("calendarday.id"))
    calendar_month = Column(Integer, ForeignKey("calendarmonth.id"))
    calendar_year = Column(Integer, ForeignKey("calendaryear.id"))
    role_id = Column(Integer, ForeignKey("roles.id"))
    taken_payments = relationship("StudentPayments", backref="user", order_by="StudentPayments.id", lazy="select")
    given_capital = relationship("CapitalExpenditure", backref="user", order_by="CapitalExpenditure.id", lazy="select")
    given_overhead = relationship("Overhead", backref="user", order_by="Overhead.id", lazy="select")
    given_st_salaries = relationship("StaffSalaries", backref="user", order_by="StaffSalaries.id", lazy="select")
    given_tch_salaries = relationship("TeacherSalaries", backref="user", order_by="TeacherSalaries.id", lazy="select")
    comments = relationship("Comments", backref='user', order_by='Comments.id', lazy='select')
    likes = relationship("CommentLikes", backref='user', order_by='CommentLikes.id', lazy='select')
    old_id = Column(Integer)
    book_order = relationship("BookOrder", backref="user", order_by="BookOrder.id", lazy="select")
    platform_news = relationship("PlatformNews", backref="user", order_by="PlatformNews.id", lazy="select")
    observation = relationship("TeacherObservationDay", backref="user", order_by="TeacherObservationDay.id",
                               lazy='select')
    observer = Column(Boolean, default=False)
    tasks_statistics = relationship("TasksStatistics", backref="user", order_by='TasksStatistics.id')
    tasks_daily_statistics = relationship("TaskDailyStatistics", backref="user", order_by='TaskDailyStatistics.id')

    def convert_json(self, entire=False):
        if not entire:
            info = {
                "id": self.id,
                "location": {
                    "id": self.location.id,
                    "name": self.location.name,
                },
                "name": self.name.title(),
                "surname": self.surname.title(),
                # "username": self.username.title(),
                "username": self.username,
                "password": self.password,
                "father_name": self.father_name.title(),
                "user_id": self.user_id,
                "phone_list": [],
                "education_language": {
                    "id": self.language.id,
                    "name": self.language.name
                },
                "photo_profile": self.photo_profile,
                "born_day": self.born_day,
                "born_month": self.born_month,
                "born_year": self.born_year,
                "age": self.age,
                "balance": self.balance,
                "role": {
                    "id": self.role_info.id,
                    "name": self.role_info.type_role,
                    "role": self.role_info.role
                },
                "student": {},
                "teacher": {},
                "phone": []
            }
            for phone in self.phone:
                phone_info = {
                    "phone": phone.phone,
                    "parent": phone.parent,
                    "personal": phone.personal
                }
                info['phone'].append(phone_info)
            if self.student:
                info["student"] = {
                    "subjects": [],
                    "group": [],
                    "ball_time": self.student.ball_time.strftime("%Y-%m-%d %H:%M"),
                    "combined_debt": self.student.combined_debt,
                    "debtor": self.student.debtor,
                    "extra_payment": self.student.extra_payment,
                    "representative_name": self.student.representative_name,
                    "representative_surname": self.student.representative_surname
                }
                for subject in self.student.subject:
                    info['student']['subjects'].append(
                        {
                            "id": subject.id,
                            "name": subject.name,
                            "ball_number": subject.ball_number
                        }
                    )
                for group in self.student.group:
                    if not group.deleted:
                        group_info = clone_group_info(group)
                        info['student']['group'].append(group_info)

            elif self.teacher:
                info["teacher"] = {
                    "subjects": [],
                    "group": [],
                }
                for subject in self.teacher.subject:
                    info['teacher']['subjects'].append(
                        {
                            "id": subject.id,
                            "name": subject.name,
                            "ball_number": subject.ball_number
                        }
                    )
                for group in self.teacher.group:
                    if not group.deleted and group.status:
                        group_info = clone_group_info(group)
                        info['teacher']['group'].append(group_info)
            return info
        else:
            return {
                "id": self.id,
                "name": self.name.title(),
                "surname": self.surname.title(),
                "username": self.username,
                "user_id": self.user_id
            }


def clone_group_info(group):
    group_info = {
        "id": group.id,
        "name": group.name,
        "teacher_salary": group.teacher_salary,
        "location": {
            "id": group.location.id,
            "name": group.location.name,
        },
        "status": group.status,
        "education_language": {
            "id": group.language.id,
            "name": group.language.name
        },
        "attendance_days": group.attendance_days,
        "price": group.price,
        "teacher_id": group.teacher_id,
        "subjects": {
            "id": group.subject.id,
            "name": group.subject.name,
            "ball_number": group.subject.ball_number
        },
        "course": {}
    }
    if group.level:
        level_info = {
            "id": group.level.id,
            "name": group.level.name
        }
        group_info['course'] = level_info
    return group_info


class PhoneList(db.Model):
    __tablename__ = "phonelist"
    id = Column(Integer, primary_key=True)
    phone = Column(String)
    parent = Column(Boolean)
    personal = Column(Boolean)
    other = Column(Boolean)
    user_id = Column(Integer, ForeignKey('users.id'))


class Roles(db.Model):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    role = Column(String)
    type_role = Column(String)
    users_link = relationship("Users", backref="role_info", order_by="Users.id")
    old_id = Column(Integer)

    def add(self):
        db.session.add(self)
        db.session.commit()


class Staff(db.Model):
    __tablename__ = "staff"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    profession_id = Column(Integer, ForeignKey('professions.id'))
    stuff_salary = relationship('StaffSalary', backref="staff", order_by="StaffSalary.id")
    staff_given_salary = relationship("StaffSalaries", backref="staff", order_by="StaffSalaries.id")
    staff_deleted_salary = relationship("DeletedStaffSalaries", backref="staff", order_by="DeletedStaffSalaries.id")
    salary = Column(Integer)
    old_id = Column(Integer)
    deleted = Column(Boolean, default=False)
    deleted_comment = Column(String)


class DeletedStaff(db.Model):
    __tablename__ = "deleted_staff"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))  # relationship qilinmagan
    reason = Column(String)
    calendar_day = Column(Integer, ForeignKey("calendarday.id"))  # relationship qilinmagan


class CourseTypes(db.Model):
    __tablename__ = "coursetypes"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    cost = Column(Integer)
    group = relationship("Groups", backref="course_type", order_by="Groups.id")
    attendance = relationship("Attendance", backref="course_type", order_by="Attendance.id")
    old_id = Column(Integer)


db.Table('student_subject',
         db.Column('student_id', db.Integer, db.ForeignKey('students.id')),
         db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id'))
         )

db.Table('teacher_subject',
         db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id')),
         db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id'))
         )


class Subjects(db.Model):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    ball_number = Column(Integer)
    group = relationship("Groups", backref="subject", order_by="Groups.id")
    attendance = relationship("Attendance", backref="subject", order_by="Attendance.id")
    attendance_history_student = relationship("AttendanceHistoryStudent", backref="subject",
                                              order_by="AttendanceHistoryStudent.id")
    attendance_history_teacher = relationship("AttendanceHistoryTeacher", backref="subject",
                                              order_by="AttendanceHistoryTeacher.id")
    subject_level = relationship('SubjectLevels', backref="subject", order_by="SubjectLevels.id")
    room = relationship("Rooms", secondary="room_subject", backref="subject", order_by="Rooms.id")
    leads = relationship('Lead', secondary="lead_subject", backref="subject", order_by="Lead.id")
    test = relationship('GroupTest', backref="subject", order_by="GroupTest.id")
    old_id = Column(Integer)
    disabled = Column(Boolean)
    classroom_id = Column(Integer)
    student_tests = relationship("StudentTest", backref="subject", order_by="StudentTest.id")

    def convert_json(self):
        return {
            "id": self.id,
            "name": self.name
        }

    def add(self):
        db.session.add(self)
        db.session.commit()


class SubjectLevels(db.Model):
    __tablename__ = "subjectlevels"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    groups = relationship("Groups", backref="level", order_by="Groups.id")
    classroom_id = Column(Integer)
    disabled = Column(Boolean)

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "name": self.name,
            "subject": {
                "id": self.subject.id,
                "name": self.subject.name,
            }
        }

    def add(self):
        db.session.add(self)
        db.session.commit()


class Professions(db.Model):
    __tablename__ = "professions"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    staff = db.relationship("Staff", backref="profession", order_by="Staff.id")
    staff_salaries = db.relationship("StaffSalaries", backref="profession", order_by="StaffSalaries.id")
    deleted_staff_salaries = relationship("DeletedStaffSalaries", backref="profession")
    old_id = Column(Integer)

    def add(self):
        db.session.add(self)
        db.session.commit()
