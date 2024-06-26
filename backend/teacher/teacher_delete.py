from app import app, api, jsonify, db
from backend.models.models import Teachers, DeletedTeachers
from backend.functions.utils import find_calendar_date, get_json_field


@app.route(f'{api}/delete_teacher/<int:user_id>', methods=["POST"])
def teacher_delete(user_id):
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    reason = get_json_field('otherReason')
    teacher = Teachers.query.filter(Teachers.user_id == user_id).first()
    del_group = 0
    status = False
    for gr in teacher.group:
        if gr.deleted:
            del_group += 1
    if del_group == len(teacher.group):
        status = True
    if teacher:
        if not teacher.group or status:
            add = DeletedTeachers(teacher_id=teacher.id, reason=reason, calendar_day=calendar_day.id)
            db.session.add(add)
            db.session.commit()
            return jsonify({
                "success": True,
                "msg": "O'qituvchi o'chirildi"
            })
        else:
            return jsonify({
                "success": False,
                "msg": "O'qituvchida guruh bor"
            })
