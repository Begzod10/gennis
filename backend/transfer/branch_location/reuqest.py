import json

import requests

from app import app
from backend.models.models import Locations


def transfer_location():
    with app.app_context():
        request = 'location:'
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
    with app.app_context():
        url = "http://localhost:8000/Location/location_list/"
        headers = {
            'Accept': 'application/json',
            'Authorization': f"JWT {token}"
        }

        response = requests.request("GET", url, headers=headers).json()
        for location in response['locations']:
            location_base = Locations.query.filter(Locations.id == location.get('old_id')).first()
            url = "http://localhost:8000/Branch/branch_create/"

            year_str = location_base.day.date.strftime(
                '%Y-%m-%d') if location_base.day and location_base.day.date else None

            payload = json.dumps({
                "location": location.get('id'),
                "name": location_base.name,
                "number": location_base.number_location,
                "map_link": location_base.link,
                "code": location_base.code,
                "phone_number": location_base.number_location,
                "director_fio": location_base.director_fio,
                "location_text": location_base.location,
                "district": location_base.bank_sheet,
                "bank_sheet": location_base.bank_sheet,
                "inn": location_base.inn,
                "bank": location_base.bank,
                "mfo": location_base.mfo,
                "campus_name": location_base.campus_name,
                "address": location_base.address,
                "year": year_str,
                "old_id": location_base.id
            })

            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'JWT {token}'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            print(response.text)
