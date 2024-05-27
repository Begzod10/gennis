from app import app, request, jsonify
from backend.functions.utils import api, find_calendar_date, get_json_field, desc, CalendarMonth, AccountingPeriod, \
    refreshdatas, iterate_models
from backend.models.models import db, Subjects
from .models import Lead, LeadInfos
from datetime import datetime
from flask_jwt_extended import jwt_required


@app.route(f'{api}/register_lead', methods=['POST'])
def register_lead():
    refreshdatas()
    calendar_year, calendar_month, calendar_day = find_calendar_date()
    accounting_period = AccountingPeriod.query.join(CalendarMonth).order_by(desc(CalendarMonth.id)).first().id
    name = get_json_field('name')
    phone = get_json_field('phone')
    location_id = get_json_field('location_id')

    subject_id = get_json_field('subject_id') if 'subject_id' in request.get_json() else None

    exist_user = Lead.query.filter(Lead.phone == phone, Lead.deleted == False).first()
    if not exist_user:
        lead = {
            "name": name,
            "phone": phone,
            "calendar_day": calendar_day.id,
            "account_period_id": accounting_period,
            "location_id": location_id,
        }
        exist_user = Lead(**lead)
        exist_user.add()
    if subject_id:
        subject = Subjects.query.filter(Subjects.id == subject_id).first()
        if exist_user not in subject.leads:
            subject.leads.append(exist_user)
            db.session.commit()
    return jsonify({
        "msg": "Siz muvaffaqiyatli ro'yxatdan o'tdingiz",
        "success": True
    })


@app.route(f'{api}/get_leads_location/<status>/<location_id>')
@jwt_required()
def get_leads_location(status, location_id):
    if status == "news":
        leads = Lead.query.filter(Lead.location_id == location_id, Lead.deleted == False).order_by(desc(Lead.id)).all()
        return jsonify({
            "leads": iterate_models(leads)
        })
    else:
        leads = Lead.query.filter(Lead.location_id == location_id, Lead.deleted == True).order_by(desc(Lead.id)).all()
        return jsonify({
            "leads": iterate_models(leads)
        })


@app.route(f'{api}/lead_crud/<int:pm>', methods=['POST', "GET", "DELETE", "PUT"])
@jwt_required()
def crud_lead(pm):
    lead = Lead.query.filter(Lead.id == pm).first()
    if request.method == "DELETE":
        comment = get_json_field('comment')
        lead.deleted = True
        lead.comment = comment
        db.session.commit()
        return jsonify({
            "msg": "O'quvchi o'chirildi",
            "success": True,

        })
    if request.method == "POST":
        comment = get_json_field('comment')
        date = get_json_field('date')
        date = datetime.strptime(date, '%Y-%m-%d')
        info = {
            "lead_id": lead.id,
            "day": date,
            "comment": comment
        }
        info = LeadInfos(**info)
        info.add()
        return jsonify({
            "msg": "Komment belgilandi",
            "success": True,
            "lead": lead.convert_json()
        })
    if request.method == "GET":
        get_comments = LeadInfos.query.filter(LeadInfos.lead_id == lead.id).order_by(desc(LeadInfos.id)).all()

        return jsonify({
            "comments": iterate_models(get_comments)
        })
