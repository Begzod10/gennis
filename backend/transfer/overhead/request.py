import requests

from app import app
from backend.models.models import Overhead, Capital


def transfer_overhead(token):
    with app.app_context():
        branch_url = 'http://localhost:8000/Branch/branch_list/'
        y = requests.get(url=branch_url, headers={'Authorization': f"JWT {token}"})
        payment_types_url = 'http://localhost:8000/Payments/payment-types/'
        z = requests.get(url=payment_types_url, headers={'Authorization': f"JWT {token}"})
        overheads = Overhead.query.order_by(Overhead.id).all()
        for overhead in overheads:
            info = {
                "old_id": overhead.id,
                "name": overhead.item_name,
                "payment": next((payment_type['id'] for payment_type in z.json()['paymenttypes'] if
                                 payment_type['old_id'] == overhead.payment_type_id), 0),
                "price": overhead.item_sum,
                "branch": next(
                    (branch['id'] for branch in y.json()['branches'] if branch['old_id'] == overhead.location_id), 0)
            }
            url = 'http://localhost:8000/Overhead/overheads/create/'
            x = requests.post(url, json=info)
            print(x.text)
        return True
