from flask import Flask, request, jsonify
import logging, os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {'end_session': False}
    }

    processing_dialog(request.json, response)
    logging.info(f'Response:  {response!r}')
    return jsonify(response)


def processing_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {'suggests': ["Не хочу.", "Не буду.", "Отстань!"], 'current': 'слон'}
        res['response']['text'] = 'Привет! Купи слона!'
        res['response']['buttons'] = get_suggests(user_id)
    else:
        a = [i for i in req['request']['nlu']['tokens'] if i in ['ладно', 'куплю', 'покупаю', 'хорошо']]
        if a:
            if sessionStorage[user_id]['current'] == 'слон':
                res['response']['text'] = 'Слона можно найти на Яндекс.Маркете! Купи еще кролика!'
                sessionStorage[user_id]['current'] = 'кролик'
                sessionStorage[user_id]['suggests'] = ["Не хочу.", "Не буду.", "Отстань!"]
            else:
                res['response']['text'] = 'Кролика можно найти на Яндекс.Маркете! Купи еще слона!'
                sessionStorage[user_id]['current'] = 'слон'
                sessionStorage[user_id]['suggests'] = ["Не хочу.", "Не буду.", "Отстань!"]
            res['response']['buttons'] = get_suggests(user_id)
        else:
            res['response'][
                'text'] = f"Все говорят '{req['request']['original_utterance']}', а ты купи {sessionStorage[user_id]['current']}а!"
            res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]
    suggests = [{'title': suggest, 'hide': True} for suggest in session['suggests'][:2]]
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": f"https://market.yandex.ru/search?text={sessionStorage[user_id]['current']}",
            "hide": True
        })
    return suggests


if __name__ == '__main__':
    port = os.environ.get('PORT', 4545)
    app.run(host='0.0.0.0', port=port)
