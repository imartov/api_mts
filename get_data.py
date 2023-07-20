import json, os
from dotenv import load_dotenv
from main import send_message


def get_data() -> None:
    ''' получение параметров для запроса '''
    with open("test_data.json", "r", encoding="utf-8") as file:
        request_params = json.load(file)

    # get text message
    with open("text_message.txt", "r", encoding="utf-8") as file:
        text_message = file.read()

    # get environment variables
    load_dotenv()
    ALPHA_NAME = os.getenv("ALPHA_NAME")

    # set text message and alfa name
    request_params["channel_options"]["sms"]["text"] = text_message
    request_params["channel_options"]["sms"]["alpha_name"] = ALPHA_NAME

    send_message(request_params=request_params)

if __name__ == "__main__":
    get_data()