from app import app, jsonify
from backend.models.models import Week, Group_Room_Week, Rooms, Groups
from backend.functions.utils import update_week, api

from flask_jwt_extended import jwt_required


@app.route(f'{api}/view_table2/<int:location_id>/<day>', methods=['GET'])
@jwt_required()
def view_table(location_id, day):
    update_week(location_id)
    week_day = Week.query.filter(Week.location_id == location_id, Week.eng_name == day).order_by(
        Week.id).first()
    week_days = Week.query.filter(Week.location_id == location_id).order_by(
        Week.order).all()
    time_table = Group_Room_Week.query.filter(Group_Room_Week.location_id == location_id,
                                              Group_Room_Week.week_id == week_day.id).order_by(
        Group_Room_Week.id).all()
    rooms = Rooms.query.filter(Rooms.location_id == location_id).order_by(Rooms.id).all()

    time_table_list = []
    for time in time_table:
        info = {
            "id": time.id,
            "teacher": [],
            "from": time.start_time.strftime("%H:%M"),
            "to": time.end_time.strftime("%H:%M"),
            "room": time.room_id,
            "week": time.week_id
        }
        for teach in time.teacher:
            group = Groups.query.filter(Groups.id == time.group_id).first()
            teach_info = {
                "name": teach.user.name,
                "surname": teach.user.surname,
                "color": teach.table_color,
                "group_id": time.group_id,
                "group_name": group.name

            }
            info['teacher'].append(teach_info)
        time_table_list.append(info)
    rooms_list = [{"id": room.id, "name": room.name} for room in rooms]
    week_days_list = [
        {
            "id": room.id,
            "name": room.name,
            "value": room.eng_name
        } for room in week_days
    ]
    day_dict = {gr['id']: gr for gr in time_table_list}
    filtered_time_table_list = list(day_dict.values())
    return jsonify({
        "time_table": filtered_time_table_list,
        "rooms": rooms_list,
        "week_days": week_days_list,
        "success": True
    })
