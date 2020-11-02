from flask import Flask
from flask import request
from flask import jsonify
from app.config import URL
import requests
import json

app = Flask(__name__)


def write_json(data, filename='../log/response.json'):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def send_message(chat_id, text='lolkek'):
    url = URL + 'sendMessage'
    message = {'chat_id': chat_id, 'text': text}
    response = requests.post(url, json=message)
    return response.json()


def handle_update(u):
    if 'message' in u:
        chat_id = u['message']['chat']['id']
        text = u['message']['text']
        send_message(chat_id, text)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        update = request.get_json()
        write_json(update)
        handle_update(update)
        return jsonify(update)
    return '<h1>Hello</h1>'


def main():
    # last_message_id = None
    # while True:
    #     last_message_id = echo_last_message(last_message_id)
    pass


if __name__ == '__main__':
    app.run()
