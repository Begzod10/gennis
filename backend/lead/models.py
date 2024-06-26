# from backend.functions.utils import find_calendar_date
from backend.models.models import Column, Integer, db, String, ForeignKey, Boolean, desc, DateTime, relationship
from datetime import datetime


class LeadInfos(db.Model):
    __tablename__ = "lead_infos"
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey('lead.id'))
    comment = Column(String)
    day = Column(DateTime)
    added_date = Column(DateTime)

    def convert_json(self, entire=False):
        return {
            "id": self.id,
            "comment": self.comment,
            "date": self.day.strftime("%Y-%m-%d")
        }

    def add(self):
        db.session.add(self)
        db.session.commit()


class Lead(db.Model):
    __tablename__ = "lead"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone = Column(String)
    calendar_day = Column(Integer, ForeignKey('calendarday.id'))
    deleted = Column(Boolean, default=False)
    account_period_id = Column(Integer, ForeignKey('accountingperiod.id'))
    comment = Column(String)
    location_id = Column(Integer, ForeignKey('locations.id'))
    infos = relationship("LeadInfos", backref="lead", order_by=desc(LeadInfos.id))

    def convert_json(self, entire=False):

        info = LeadInfos.query.filter(LeadInfos.lead_id == self.id).order_by(desc("id")).first()
        day = info.day if info else self.day.date
        if info:
            lead_day = int(day.strftime("%d"))
            current_month = int(datetime.today().strftime("%m"))
            current_day = int(datetime.today().strftime("%d"))
            lead_month = int(day.strftime("%m"))
            if current_month == lead_month:
                index = current_day - lead_day
                if index > 2:
                    index = 2
                if index < 0:
                    index = 0
            else:
                index = 2
        else:
            index = 2
        history = []
        completed = []
        if self.infos:
            for info in self.infos:
                history.append(info.convert_json())

        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "day": self.day.date.strftime("%Y-%m-%d"),
            "deleted": self.deleted,
            "comment": self.comment,
            "status": ['green', 'yellow', 'red'][index],
            "history": history,
            "subjects": [subject.convert_json() for subject in self.subject]
        }

    def add(self):
        db.session.add(self)
        db.session.commit()


db.Table('lead_subject',
         db.Column('lead_id', db.Integer, db.ForeignKey('lead.id')),
         db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id'))
         )
