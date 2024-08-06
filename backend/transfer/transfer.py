from app import *


def send_data():
    systems = [{"name": "Gennis"}, {"name": "Turon"}]
    for system in systems:
        response = requests.get('http://127.0.0.1:8000/receive-data/', json=system)
    return f'Data sent! Response: {response.text}'
