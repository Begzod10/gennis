import requests
from app import app
from backend.models.models import CapitalExpenditure


def transfer_capital():
    with app.app_context():
        capitals = CapitalExpenditure.query.order_by(CapitalExpenditure.id).all()
        for capital in capitals:
            info = {
                "branch": capital.location_id,
                "payment_type": capital.payment_type_id,
                "by_who": capital.by_who,
                "name": capital.item_name,
                "price": capital.item_sum,
                "added_date": capital.day.date.strftime("%Y-%m-%d"),
                "old_id": capital.id,
            }
            url = 'http://localhost:8000/Capital/old_capital_create/'
            x = requests.post(url, json=info)
            print(x.text)
        return True
