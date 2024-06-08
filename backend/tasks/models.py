from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import String, Integer, Boolean, Column, ForeignKey, DateTime, or_, and_, desc, func, ARRAY, JSON, \
    extract, Date, BigInteger
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, functions
from pprint import pprint
import uuid

db = SQLAlchemy()


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


class Tasks(db.Model):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    role = Column(String)
    tasks_statistics = relationship("TasksStatistics", backref="task", order_by='TasksStatistics.id')


class TasksStatistics(db.Model):
    __tablename__ = "tasksstatistics"
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    calendar_year = Column(Integer, ForeignKey('calendaryear.id'))
    calendar_month = Column(Integer, ForeignKey('calendarmonth.id'))
    calendar_day = Column(Integer, ForeignKey('calendarday.id'))
    completed_tasks = Column(Integer, default=0)
    in_progress_tasks = Column(Integer)
    completed_tasks_percentage = Column(Integer, default=0)
    location_id = Column(Integer, ForeignKey('locations.id'))


class TaskDailyStatistics(db.Model):
    __tablename__ = "taskdailystatistics"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    calendar_year = Column(Integer, ForeignKey('calendaryear.id'))
    calendar_month = Column(Integer, ForeignKey('calendarmonth.id'))
    calendar_day = Column(Integer, ForeignKey('calendarday.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    completed_tasks = Column(Integer, default=0)
    in_progress_tasks = Column(Integer)
    completed_tasks_percentage = Column(Integer, default=0)
