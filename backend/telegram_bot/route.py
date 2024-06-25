from app import *
from backend.models.models import *
from backend.group.class_model import *
from backend.student.class_model import *


@app.route(f'{api}/check_student', methods=['POST'])
def check_student():
    pprint(request.get_json())
    student_id = request.get_json()['student_id']
    check_user = Users.query.filter(Users.user_id == student_id, Users.student != None).first()
    info = {"msg": "Student topilmadi", "status": False, "student_id": student_id} if not check_user else {
        "id": check_user.student.id,
        "name": check_user.name,
        "surname": check_user.surname,
        "user_id": check_user.user_id,
        "status": True}
    requests.post(f"{telegram_bot_server}/check_status", headers={
        'Content-Type': 'application/json'
    }, json={
        "info": info,
        "user_id": request.get_json()['user_id'],
        "name": request.get_json()["name"],
        "surname": request.get_json()['surname'],
        "chat_id": request.get_json()['chat_id'],

    })
    return jsonify({
        "success": True
    })


@app.route(f'{api}/send_notification')
def send_notification():
    debtors = Users.query.filter(Users.balance < 0, Users.student != None).order_by(Users.id).all()
    debtors_list = []
    for user in debtors:
        info = {
            "user_id": user.user_id,
            "balance": user.balance
        }
        debtors_list.append(info)
    pprint(iterate_models(debtors))
    requests.post(f"{telegram_bot_server}/send_msg_debtor", headers={
        'Content-Type': 'application/json'
    }, json={
        "text": "Msg to debtors",
        "data": iterate_models(debtors)
    })
    return "True"


@app.route(f'{api}/check_student_info', methods=['POST'])
def check_student_info():
    pprint(request.get_json())
    student_id = request.get_json()['student_id']
    user = Users.query.filter(Users.user_id == student_id).first()
    text = request.get_json()['text']
    info = ''
    if text == "💰 Student hisobi":
        info = f"{user.name} {user.surname} ning hozrgi hisobi: {user.balance}"
    elif text == "\U0001F4B8 Student to'lovlari":
        payments = StudentPayments.query.filter(StudentPayments.student_id == user.student.id).order_by(
            StudentPayments.id).all()
        if payments:
            info = f"{user.name} {user.surname} ning to'lovlari: \n"
            for payment in payments:
                info += f"To'lov : {payment.payment_sum} sana: {payment.day.date.strftime('%Y-%m-%d')} \n"
        else:
            info = f"{user.name} {user.surname} ga hali to'lov qilinmagan"
    elif text == "👥 Student guruhlari":
        for group in user.student.group:
            teacher = Teachers.query.filter(Teachers.id == group.teacher_id).first()
            info += f"Guruh fani: {group.subject.name} \nGuruh narxi: {group.price} \nGuruh o'qtuvchisi: {teacher.user.name} {teacher.user.surname}\n"

    requests.post(f"{telegram_bot_server}/get_infos", headers={
        'Content-Type': 'application/json'
    }, json={
        "info": info,
        "text": text
    })
    return "True"


@app.route(f'{api}/get_group_info',methods=['POST'])
def get_group_info():
    student_id = request.get_json()['student_id']
    user = Users.query.filter(Users.user_id == student_id).first()
    text = request.get_json()['text']
    st_functions = Student_Functions(student_id=user.student.id)
    if text == "\U0001F4CB Student davomatlari":
        current_month = datetime.now().month
        if len(str(current_month)) == 1:
            current_month = "0" + str(current_month)
        current_year = datetime.now().year

        requests.post(f"{telegram_bot_server}/get_gr_infos", headers={
            'Content-Type': 'application/json'
        }, json={
            "info": st_functions.attendance_filter_student(month=current_month, year=current_year),
            "text": text
        })
    elif text == "\U0001F557 Dars vaqtlari":
        groups = db.session.query(Groups).join(Groups.student).options(contains_eager(Groups.student)).filter(
            Students.id == user.student.id).order_by(Groups.id).all()
        time_table_list = []
        for group in groups:
            info = {
                "group_subject": group.subject.name,
                "table": []

            }
            time_table = Group_Room_Week.query.filter(Group_Room_Week.group_id == group.id).order_by(
                Group_Room_Week.id).all()
            for table in time_table:
                table_info = {
                    "week_name": table.week.name,
                    "start_time": table.start_time.strftime("%H-%M"),
                    "end_time": table.end_time.strftime("%H-%M"),
                }
                info['table'].append(table_info)
            time_table_list.append(info)
        requests.post(f"{telegram_bot_server}/get_gr_infos", headers={
            'Content-Type': 'application/json'
        }, json={
            "info": time_table_list,
            "text": text
        })

    return "True"
