from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Хранилище данных о сессиях.
sessionStorage = {}

# животные
animals = [
    'слон',
    'кролик'
]


@app.route('/post', methods=['POST'])
# Функция получает тело запроса и возвращает ответ.
def main():
    logging.info('Request: %r', request.json)

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info('Response: %r', request.json)

    return jsonify(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.

        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ],
            'animal': 0
        }

        res['response']['text'] = 'Привет! Купи ' + animals[sessionStorage[user_id]['animal']] + 'a!'
        res['response']['buttons'] = get_suggests(user_id, animals[sessionStorage[user_id]['animal']])
        return

    # Обрабатываем ответ пользователя.
    if req['request']['original_utterance'].lower() in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо'
    ]:
        # Пользователь согласился, прощаемся.

        sessionStorage[user_id]['suggests'] = [
            "Не хочу.",
            "Не буду.",
            "Отстань!",
        ]
        if sessionStorage[user_id]['animal'] == len(animals) - 1:
            res['response']['text'] = animals[sessionStorage[user_id]['animal']] + 'а можно найти на Яндекс.Маркете!'
            sessionStorage[user_id]['animal'] += 1
            res['response']['end_session'] = True
        else:
            res['response']['text'] = animals[sessionStorage[user_id]['animal']] + 'а можно найти на Яндекс.Маркете!'
            sessionStorage[user_id]['animal'] += 1
            res['response']['text'] += ' А ' + animals[sessionStorage[user_id]['animal']] + 'a купишь? '
            res['response']['buttons'] = get_suggests(user_id, animals[sessionStorage[user_id]['animal']])
        return

    # Если нет, то убеждаем его купить слона!
    res['response']['text'] = ('Все говорят "%s", а ты купи ' + animals[sessionStorage[user_id]['animal']] + 'а!') % (
        req['request']['original_utterance']
    )
    res['response']['buttons'] = get_suggests(user_id, animals[sessionStorage[user_id]['animal']])


# Функция возвращает две подсказки для ответа.
def get_suggests(user_id, animal):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на Яндекс.Маркет.
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=" + animal,
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    app.run()
