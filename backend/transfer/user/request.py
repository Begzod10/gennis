from backend.models.models import Users
import requests
from app import app


def transfer_users(token):
    with app.app_context():
        url = "http://localhost:8000/Language/language/"
        headers = {
            'Accept': 'application/json',
            'Authorization': f"JWT {token}"
        }

        languages = requests.request("GET", url, headers=headers).json()
        url = "http://localhost:8000/Branch/branch_list/"
        headers = {
            'Accept': 'application/json',
            'Authorization': f"JWT {token}"
        }

        branches = requests.request("GET", url, headers=headers).json()
        for language in languages['languages']:
            for branch in branches['branches']:
                users = Users.query.order_by(Users.id).all()
                for user in users:
                    if user.education_language == language['old_id'] and user.location_id == branch['old_id']:
                        phone = 0
                        for number in user.phone:
                            if number.personal == True:
                                phone = number.phone
                        info = {
                            'old_id': user.id,
                            "name": user.name,
                            "surname": user.surname,
                            "username": user.username,
                            "father_name": user.father_name,
                            "password": user.password,
                            "phone": phone,
                            "observer": user.observer,
                            "comment": user.comment,
                            "birth_date": f'{user.born_year}-{user.born_month}-{user.born_day}',
                            "language": language['id'],
                            "branch": branch['id'],
                            "is_superuser": False,
                            "is_staff": False,
                        }
                        url = 'http://localhost:8000/Users/users/create/'
                        x = requests.post(url, json=info)
                        print(x.text)
        return True
