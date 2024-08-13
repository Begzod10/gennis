import requests

from app import app
from backend.models.models import Professions, Staff, StaffSalary, StaffSalaries

url = "http://127.0.0.1:8000/Permissions/create_group_and_add_permissions/"


def transfer_job():
    with app.app_context():
        roles = Professions.query.order_by(Professions.id).all()
        for role in roles:
            info = {
                "name": role.name,
                "system_id": 1,
                "permissions": []
            }
            url = 'http://localhost:8000/Permissions/create_group_and_add_permissions/'
            x = requests.post(url, json=info)
            print(x.text)

        return True


def transfer_staffs():
    with app.app_context():
        staffs = Staff.query.order_by(Staff.id).all()
        for staff in staffs:
            info = {
                "group": staff.user.role_info.type_role,
                "user": staff.user_id,
                "salary": staff.salary,
                "old_id": staff.id
            }
            url = 'http://localhost:8000/Transfer/users/staff/create/'
            x = requests.post(url, json=info)
            print(x.text)

        return True


def transfer_staffs_salary():
    with app.app_context():
        staffs = StaffSalary.query.filter(StaffSalary.staff != None).order_by(StaffSalary.id).all()
        for staff in staffs:
            year_str = staff.month.date.strftime(
                '%Y-%m-%d') if staff.month and staff.month.date else None

            info = {
                "permission": staff.staff_id,
                "user": staff.staff.user.id,
                "date": year_str,
                "total_salary": staff.total_salary,
                "taken_salary": staff.taken_money,
                "remaining_salary": staff.remaining_salary,
                "old_id": staff.id

            }
            url = 'http://localhost:8000/Transfer/users/staff/salary/'
            x = requests.post(url, json=info)
            print(x.text)

        return True


def transfer_staffs_list_salary():
    with app.app_context():
        staffs = StaffSalaries.query.filter(StaffSalaries.staff != None).order_by(StaffSalaries.id).all()
        for staff in staffs:
            year_str = staff.day.date.strftime(
                '%Y-%m-%d') if staff.day and staff.day.date else None

            info = {
                "permission": staff.staff_id,
                "user": staff.staff.user.id,
                "user_salary": staff.salary_id,
                "payment_types": staff.payment_type_id,
                "branch": staff.location_id,
                "salary": staff.payment_sum,
                "date": year_str,
                "comment": staff.reason,
                "deleted": False,
                'old_id':staff.id

            }
            url = 'http://localhost:8000/Transfer/users/staff/salary_list/'
            x = requests.post(url, json=info)
            if x.status_code != 200 or x.status_code != 201:
                print(x.status_code)
                print(x.text)
        return True
