from backend.models.models import func, StudentPayments
from app import db


def sum_money(model_item, model_period, period_id, model_location, location_id, model_payment_type_id,
              payment_type_id,
              type_payment=None, status_payment=False):
    if type_payment == "payment":
        payment = db.session.query(
            func.sum(model_item).filter(model_period == period_id, model_location == location_id,
                                        model_payment_type_id == payment_type_id,
                                        StudentPayments.payment == status_payment)
        ).first()
    else:
        payment = db.session.query(
            func.sum(model_item).filter(model_period == period_id, model_location == location_id,
                                        model_payment_type_id == payment_type_id)).first()
    if payment[0]:
        payment = payment[0]
    else:
        payment = 0
    return payment
