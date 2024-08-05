import requests

from app import app
from backend.models.models import Locations


def transfer_location():
    with app.app_context():
        request = 'transfer_course_types:'
        locations = Locations.query.order_by(Locations.id).all()
        for location in locations:
            info = {
                "name": location.name,
                "number": location.number_location,
                "system": 1,
                "old_id": location.id
            }
            print(info)
            url = 'http://localhost:8000/Location/location_create/'
            x = requests.post(url, json=info)
            print(x.text)
            print(x.status_code)
            request += f' {x.status_code}'
        return request


def transfer_branch(token):
    url = "http://localhost:8000/Location/location_list/"
    headers = {
        'Accept': 'application/json',
        'Authorization': f"JWT {token}"
    }
    response = requests.request("GET", url, headers=headers)
    print(response.text)
