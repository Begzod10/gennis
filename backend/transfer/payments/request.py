from backend.models.models import PaymentTypes
import requests
from app import app


def transfer_payment_types():
    with app.app_context():
        payment_types = PaymentTypes.query.order_by(PaymentTypes.id).all()
        for payment_type in payment_types:
            info = {
                'old_id': payment_type.id,
                'name': payment_type.name,
            }
            url = 'http://localhost:8000/Payments/payment-types/create/'
            x = requests.post(url, json=info)
            print(x.text)
        return True
