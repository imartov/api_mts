import requests


def sms_sending() -> None:

    authentication_params = {
        'client_id': '1254', # присваивается провайдером
        # 'extra_id': '? - идентификатор сообщения, указывается заказчиком, не может повторяться, не обязательный аргумент',
        'alpha_name': 'Alivaria', # присваивается провайдером
        'login': 'Alivaria_wxP9', # ввыдается администратором платформы'
        'password': 'tBjAa1' # узнать, актуальный ли пароль'
    }

    request_params = {
        'phone_number': 375445285989,
        'extra_id': '', # what is it?
        # 'callback_url': "https://send-dr-here.com", # what is?
        # 'start_time': '2020-12-12 10:10:10+03:00', # not requirement, what is it?
        'tag': 'debt_collection', # not requirement
        'channels': [
            'sms'
    ],
        'channel_options': {
            'sms': {
                'text': f'Уважаемый клиент!\nОАО "Пивоваренная компания сообщает, что у вас образовалась просроченная задолженность в размере {3434}".\nПросим оплатить',
                'alpha_name': authentication_params['alpha_name'],
                'ttl': 300,
        }

    }
}

    url = f'https://api.br.mts.by/1254'
    resp = requests.get(url=url, params=request_params)
    print("Ответ: ", resp)


if __name__ == '__main__':
    sms_sending()