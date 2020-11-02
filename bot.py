import config
import requests
import random


def get_updates():
    url = config.URL + 'getupdates'
    r = requests.get(url)
    return r.json()


def get_message():
    data = get_updates()
    update_id = data['result'][-1]['update_id']
    chat_id = data['result'][-1]['message']['chat']['id']
    text = data['result'][-1]['message']['text']

    message = {'update_id': update_id, 'chat_id': chat_id, 'text': text}
    return message


def send_message(chat_id, text="ping"):
    url = config.URL + 'sendmessage?chat_id={}&text={}'.format(chat_id, text)
    r = requests.get(url)илит


def main():
    last_update_id = None
    while True:
        message = get_message()
        if message['update_id'] != last_update_id:
            text = message['text']
            if text[0] == '/':
                text = text[1:]
            # answer = 'Ты сказал ' + text + '? Ты охуел что-ли?'
            r = random.randint(0, 1)
            answer = 'Абзагир' if r else 'Динара'

            send_message(message['chat_id'], answer)
            last_update_id = message['update_id']


if __name__ == '__main__':
    main()
