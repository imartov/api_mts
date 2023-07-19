''' для перевода данных в json '''
import json
import requests



def sms_sending() -> None:
    ''' отправка сообщения '''
    # authentication_params = {
    #     'client_id': '1254', # присваивается провайдером
    #     # 'extra_id': '? - идентификатор сообщения, указывается заказчиком,
    #                       не может повторяться, не обязательный аргумент',
    #     'alpha_name': 'Alivaria', # присваивается провайдером
    #     'login': 'Alivaria_wxP9', # ввыдается администратором платформы'
    #     'password': 'tBjAa1' # узнать, актуальный ли пароль'
    # }

    request_params = {
        'phone_number': 375445285989,
        'channels': [
            'sms'
    ],
        'channel_options': {
            'sms': {
                'text': 'Any text',
                'alpha_name': "Alivaria",
                'ttl': 300,
        }

    }
}

    url = 'https://api.communicator.mts.by/1254/json2/simple'
    # resp = requests.post(url=url, data=json.dumps(request_params))
    # resp = requests.post(url=url, params=request_params)
    resp = requests.post(url=url, json=request_params)
    print(resp.status_code)


if __name__ == '__main__':
    sms_sending()
