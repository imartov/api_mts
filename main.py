import os
import requests
from dotenv import load_dotenv


def send_message(request_params:dict) -> None:
    ''' отправка отдельного сообшщения sms '''

    # get environment variables
    load_dotenv()
    CLIENT_ID = os.getenv("CLIENT_ID")
    LOGIN = os.getenv("LOGIN")
    PASSWORD = os.getenv("PASSWORD")
    # ALPHA_NAME = os.getenv("ALPHA_NAME")

    # url for api request
    url = f"https://api.communicator.mts.by/{CLIENT_ID}/json2/broadcast/sync"

    # request_params = {
    #     "recipients": [
    #         {
    #             "phone_number": 375445285989,
    #             "debtor_name": "Александр личный",
    #             "debt_amount": 500
    #         },
    #         {
    #             "phone_number": 375295001701,
    #             "debtor_name": "Александр рабочий",
    #             "debt_amount": 1000
    #         },
    #     ],
    #     "tag": "Debt collection",
    #     "channels": [
    #         "sms"
    #     ],
    #     "channel_options": {
    #         "sms": {
    #             "text": text_message,
    #             "alpha_name": ALPHA_NAME,
    #             "ttl": 300
    #         }
    #     }
    # }

    # sending sms-messages
    resp = requests.post(url=url, json=request_params, auth=(LOGIN, PASSWORD))
    print(resp.status_code)


if __name__ == "__main__":
    send_message()
