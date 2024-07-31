from flask import Flask, jsonify, request, render_template, session, json, send_file, send_from_directory
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired

from flask_cors import CORS
from flask_jwt_extended import JWTManager
from backend.models.models import *

app = Flask(__name__, static_folder="frontend/build", static_url_path="/")

CORS(app)

app.config.from_object('backend.models.config')
db = db_setup(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)



classroom_server = "http://192.168.68.109:5001"






# classroom_server = "https://classroom.gennis.uz/"
telegram_bot_server = "http://127.0.0.1:5000"

# filters
from backend.functions.filters import *

# account folder
from backend.account.payment import *
from backend.account.account import *
from backend.account.overhead_capital import *
from backend.account.salary import *
from backend.account.test_acc import *

# functions folder
from backend.functions.checks import *
from backend.functions.small_info import *

# QR code
from backend.QR_code.qr_code import *

# routes
from backend.routes.base_routes import *

# student
from backend.student.student_functions import *
from backend.student.change_student import *
from backend.student.calling_to_students import *
# programmers
from backend.for_programmers.for_programmers import *

# teacher
from backend.teacher.teacher_delete import *
from backend.teacher.teacher import *
from backend.teacher.lesson_plan import *
from backend.teacher.observation import *
from backend.teacher.teacher_home_page import *

# group
from backend.group.create_group import *
from backend.group.view import *
from backend.group.change import *
from backend.group.test import *

# time_table
from backend.time_table.view import *
from backend.time_table.room import *

# home
from backend.home_page.route import *
# certificate
from backend.certificate.views import *
# get api
from backend.routes.get_api import *

# classroom
from backend.class_room.views import *

# bot
from backend.telegram_bot.route import *

# book
from backend.book.main import *

# lead
from backend.lead.views import *

# mobile
from backend.mobile.views import *

# tasks
from backend.tasks.admin import *
from backend.tasks.teacher import *

# teacher observation, attendance, teacher_group_statistics

if __name__ == '__main__':

    app.run()
