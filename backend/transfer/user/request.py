from backend.models.models import Users
import requests
from app import app


def transfer_subjects():
    with app.app_context():
        users = Users.query.order_by(Users.id).all()
        for user in users:
            info = {
                'old_id': user.id,
                "name": user.name,
                "surname": user.name,
                "username": user.name,
                "father_name": user.name,
                "password": user.name,
                "phone": user.name,
                "observer": user.name,
                "comment": user.name,
                "birth_date": user.name,
                "language": 0,
                "branch": 0,
                "is_superuser": False,
                "is_staff": False,
            }
            url = 'http://localhost:8000/Users/users/create/'
            x = requests.post(url, json=info)
            print(x.text)
        return True
