from backend.models.models import Rooms, RoomImages
import requests
from app import app


def transfer_rooms():
    with app.app_context():
        rooms = Rooms.query.order_by(Rooms.id).all()
        for room in rooms:
            info = {
                'old_id': room.id,
                'name': room.name,
                'seats_number': room.seats_number,
                'electronic_board': room.electronic_board,
                'deleted': room.deleted,
                'branch': room.location_id
            }
            url = 'http://localhost:8000/Transfer/rooms/create-rooms/'
            x = requests.post(url, json=info)
            print(x.text)
        return True


def transfer_room_images():
    with app.app_context():
        room_images = RoomImages.query.order_by(RoomImages.id).all()
        for room_image in room_images:
            info = {
                'old_id': room_image.id,
                'room': room_image.room_id,
                'image': room_image.photo_url,
            }
            url = 'http://localhost:8000/Transfer/rooms/create-room-images/'
            x = requests.post(url, json=info)
            print(x.text)
        return True


def transfer_room_subjects():
    with app.app_context():
        rooms = Rooms.query.order_by(Rooms.id).all()
        for room in rooms:
            for subject in room.subject:
                info = {
                    'room': room.id,
                    'subject': subject.id,
                }
                url = 'http://localhost:8000/Transfer/rooms/create-room-subjects/'
                x = requests.post(url, json=info)
                print(x.text)
        return True
