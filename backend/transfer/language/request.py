import requests

from app import app
from backend.models.models import EducationLanguage


def transfer_language():
    with app.app_context():
        request = 'language:'
        languages = EducationLanguage.query.order_by(EducationLanguage.id).all()
        for language in languages:
            info = {
                "name": language.name,
                "old_id": language.id
            }
            url = 'http://localhost:8000/Language/language/'
            x = requests.post(url, json=info)
            print(x.text)
            print(x.status_code)
            request += f' {x.status_code}'
        return request
