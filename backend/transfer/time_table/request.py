import requests

from app import app
from backend.models.models import Group_Room_Week


def transfer_group_time_table():
    with app.app_context():
        time_tables = Group_Room_Week.query.order_by(Group_Room_Week.id).all()
        for time_table in time_tables:
            info = {
                'old_id': time_table.id,
                'group': time_table.group_id,
                "week": time_table.week.eng_name,
                "room": time_table.room_id,
                "start_time": time_table.start_time.strftime("%H:%M"),
                'end_time': time_table.end_time.strftime("%H:%M"),
                'branch': time_table.location_id
            }
            print(info)
            url = 'http://localhost:8000/Transfer/time_table/create-group-time_table/'
            x = requests.post(url, json=info)
            print(x.text)

    return True
