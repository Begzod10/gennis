import json

import requests


def login():
    url = "http://127.0.0.1:8000/Api/token/"

    payload = json.dumps({
        "username": "admin",
        "password": "123"
    })
    headers = {
        'Content-Type': 'application/json',
        'Cookie': 'csrftoken=AogUAI2DE6WZwx9YDvCXZouYxy3K2syD'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    datas = response.json()
    return datas.get('access')
