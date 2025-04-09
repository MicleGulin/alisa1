from flask import Flask, request, jsonify
import logging, os

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

# Создадим словарь, чтобы с навыком хранились подсказки, которые видел пользователь (buttons)
# sessionStorage[user_id] = {'suggests': ["Не хочу.", "Не буду.", "Отстань!" ]}
sessionStorage = {}


@app.route('/post', methods=['POST'])
# Получаем, что отправила Алиса
def main():
    logging.info(f'Request: {request.json!r}')

    # Начинаем формировать ответ
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {'end_session': False}
    }

    # Отправляем request.json и response в функцию processing_dialog, чтобы дописался ответ
    processing_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')
    return jsonify(response)


def processing_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:  # Инициализация
        sessionStorage[user_id] = {'suggests': ["Не хочу.", "Не буду.", "Отстань!"]}
        res['response']['text'] = 'Привет! Купи слона!'
        res['response']['buttons'] = get_suggests(user_id)
    else:
        a = [i for i in req['request']['nlu']['tokens'] if i in ['ладно', 'куплю', 'покупаю', 'хорошо']]
        if a:
            res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
            res['response']['end_session'] = True
        else:
            res['response']['text'] = f"Все говорят '{req['request']['original_utterance']}', а ты купи слона!"
            res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [{'title': suggest, 'hide': True} for suggest in session['suggests'][:2]]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    # Если осталась только одна подсказка, предлагаем подсказку с яндекс маркетом
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=слон",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    port = os.environ.get('PORT', 4545)
    app.run(host='0.0.0.0', port=port)
