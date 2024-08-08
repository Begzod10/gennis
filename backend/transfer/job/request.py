import requests

from app import app
from backend.models.models import Roles

url = "http://127.0.0.1:8000/Permissions/create_group_and_add_permissions/"


def transfer_job():
    with app.app_context():
        roles = Roles.query.order_by(Roles.id).all()
        for role in roles:
            info = {
                "name": role.type_role,
                "system_id": 1,
                "permissions": []
            }
            url = 'http://localhost:8000/Permissions/create_group_and_add_permissions/'
            x = requests.post(url, json=info)
            print(x.text)

        return True
