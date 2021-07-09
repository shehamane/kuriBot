import json
from json import load


def set_payment_method(method_type, info):
    with open('src/data/config.json') as file:
        data = load(file)
    data['paymentMethod']['type'] = method_type
    data['paymentMethod']['info'] = info
    with open('src/data/config.json', 'w') as file:
        file.write(json.dumps(data, ensure_ascii=False, indent=4))
