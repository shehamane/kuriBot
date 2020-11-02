from flask import Flask
from app.config import URL
import requests
import json


def write_json(data, filename='../log/response.json'):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def get_updates():
    url = URL + 'getUpdates'
    response = requests.get(url)
    # write_json(response.json())
    return response.json()


def send_message(chat_id, text='lolkek'):
    url = URL + 'sendMessage'
    message = {'chat_id': chat_id, 'text': text}
    response = requests.post(url, json=message)
    return response.json()


def echo_last_message(last_id):
    update = get_updates()['result'][-1]
    update_id = update['update_id']
    if update_id != last_id:
        chat_id = update['message']['chat']['id']
        text = update['message']['text']
        send_message(chat_id, text)
    return update_id


def main():
    last_message_id = None
    while True:
        last_message_id = echo_last_message(last_message_id)


if __name__ == '__main__':
    main()
