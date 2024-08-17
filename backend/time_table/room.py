from backend.models.models import Rooms, Week, Group_Room_Week, RoomImages, Subjects, Groups
from backend.functions.utils import update_week
from backend.functions.small_info import room_images, checkFile

from werkzeug.utils import secure_filename
import os
from app import app, api, request, jsonify, db


@app.route(f'{api}/create_room/<int:location_id>', methods=['POST'])
def create_room(location_id):
    name = request.get_json()['roomName']
    electronic_board = request.get_json()['isDoska']
    seats_number = int(request.get_json()['numberStudents'])
    selectedSubjects = request.get_json()['selectedSubjects']
    room = Rooms(name=name, electronic_board=electronic_board, seats_number=seats_number, location_id=location_id)
    db.session.add(room)
    db.session.commit()
    for sub in selectedSubjects:
        subject = Subjects.query.filter(Subjects.id == sub['id']).first()
        subject.room.append(room)
        db.session.commit()
    return jsonify({
        "ok": True,
        "id": room.id
    })


@app.route(f'{api}/upload_room_img/<int:room_id>/<type>', methods=['POST'])
def upload_room_img(room_id, type):
    images = request.files.getlist('file')
    for img in images:
        app.config['UPLOAD_FOLDER'] = room_images()

        if img and checkFile(img.filename):
            photo_filename = secure_filename(img.filename)
            photo_filename = f"{room_id}{photo_filename}"
            img.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
            url = "static" + "/" + "room" + "/" + photo_filename
            add = RoomImages(room_id=room_id, photo_url=url)
            db.session.add(add)
            db.session.commit()
    if type == "new":
        return jsonify({
            "msg": "Xona yaratildi",
            "success": True,

        })
    else:
        return jsonify({
            "msg": "Rasm yuklandi",
            "success": True,

        })


@app.route(f'{api}/rooms_location/<int:location_id>')
def rooms_location(location_id):
    rooms = Rooms.query.filter(Rooms.location_id == location_id).order_by(Rooms.id).all()
    room_list = []
    for room in rooms:
        info = {
            "id": room.id,
            "name": room.name,
            "electronic_board": room.electronic_board,
            "seats_number": room.seats_number,
            "images": []
        }
        for img in room.images:
            img_info = {
                "url": img.photo_url
            }
            info['images'].append(img_info)
        room_list.append(info)
    return jsonify({
        "data": room_list
    })


@app.route(f'{api}/room_profile/<int:room_id>')
def room_profile(room_id):
    room = Rooms.query.filter(Rooms.id == room_id).first()
    room_image = []
    for img in room.images:
        info = {
            "id": img.id,
            "name": img.photo_url
        }
        room_image.append(info)
    subject_list = []
    for sub in room.subject:
        info = {
            "id": sub.id,
            "name": sub.name,
        }

        subject_list.append(info)

    return jsonify({
        "info": {
            "id": room.id,
            "name": room.name,
            "seats": room.seats_number,
            "electronic": room.electronic_board,
            "links": [
                {
                    "name": "changeInfo",
                    "title": "Ma'lumotlarni o'zgratirish",
                    "iconClazz": "fa-pen",
                    "type": "btn"
                },
                {
                    "name": "changePhoto",
                    "title": "Rasmni yangilash",
                    "iconClazz": "fa-camera",
                    "type": "btn"
                },
                {
                    "link": "roomTimeTable",
                    "title": "Dars Jadvali",
                    "iconClazz": "fas fa-user-clock",
                    "type": "link"
                }
            ],
            "images": room_image,
            "subjects": subject_list
        }
    })


@app.route(f'{api}/edit_room/<int:room_id>', methods=['POST'])
def edit_room(room_id):
    name = request.get_json()['name']
    electronic_board = request.get_json()['eBoard']
    seats_number = int(request.get_json()['seats'])

    room = Rooms.query.filter(Rooms.id == room_id).first()

    Rooms.query.filter(Rooms.id == room_id).update({
        "name": name,
        "electronic_board": electronic_board,
        "seats_number": seats_number,
    })
    db.session.commit()
    selected_subjects = request.get_json()['selectedSubjects']
    for sub in room.subject:
        room.subject.remove(sub)
        db.session.commit()
    for sub in selected_subjects:
        subject = Subjects.query.filter(Subjects.id == sub['id']).first()
        room.subject.append(subject)
        db.session.commit()
    return jsonify({
        "msg": "Xona ma'lumotlari o'zgartirildi",
        "success": True
    })


@app.route(f'{api}/delete_room_img/<int:img_id>')
def delete_room_img(img_id):
    room_img = RoomImages.query.filter(RoomImages.id == img_id).first()
    if room_img.photo_url:
        if os.path.isfile(f'frontend/build/{room_img.photo_url}'):
            os.remove(f'frontend/build/{room_img.photo_url}')
    db.session.delete(room_img)
    db.session.commit()

    return jsonify({
        "msg": "Rasm o'chirildi",
        "success": True
    })


@app.route(f'{api}/room_time_table/<int:room_id>')
def room_time_table(room_id):
    room = Rooms.query.filter(Rooms.id == room_id).first()
    update_week(room.location_id)
    week_days = Week.query.filter(Week.location_id == room.location_id).order_by(
        Week.order).all()
    time_table = Group_Room_Week.query.filter(Group_Room_Week.location_id == room.location_id,
                                              Group_Room_Week.room_id == room_id).order_by(
        Group_Room_Week.id).all()

    time_table_list = []

    week_days_list = []
    for time in time_table:
        info = {
            "teacher": [],
            "from": time.start_time.strftime("%H:%M"),
            "to": time.end_time.strftime("%H:%M"),
            "room": time.room_id,
            "day": time.week_id
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

    for week in week_days:
        info = {
            "id": week.id,
            "name": week.name,
            "value": week.eng_name
        }
        week_days_list.append(info)
    return jsonify({
        "time_table": time_table_list,
        "week_days": week_days_list,
        "success": True
    })
