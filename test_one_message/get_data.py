import json, os
from dotenv import load_dotenv
from test import ApiMTS
from utils import create_extra_id


def get_data() -> None:
    ''' получение параметров для запроса '''
    with open("test_one_message\\test_data_one_message.json", "r", encoding="utf-8") as file:
        request_params = json.load(file)

    # get text message
    with open("text_message.txt", "r", encoding="utf-8") as file:
        text_message = file.read()

    # get environment variables
    load_dotenv()
    ALPHA_NAME = os.getenv("ALPHA_NAME")

    # generate extra_id and set to recipients list
    extra_id = create_extra_id()
    request_params["extra_id"] = extra_id

    # set text message and alfa name
    request_params["channel_options"]["sms"]["text"] = text_message
    request_params["channel_options"]["sms"]["alpha_name"] = ALPHA_NAME

    print(request_params)
    print(extra_id)



    # send messages and get reports
    sms = ApiMTS()
    sms.send_messages(request_params=request_params)
    sms.get_report(extra_id=extra_id)


if __name__ == "__main__":
    get_data()