import json, os
from dotenv import load_dotenv
from main import ApiMTS
from utils import create_extra_id, FileOperations


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

    # generate extra_id and set to recipients list
    extra_id_list = []
    for recipient in request_params["recipients"]:
        extra_id = create_extra_id()
        extra_id_list.append(extra_id)
        recipient["extra_id"] = extra_id

    # set text message and alfa name
    request_params["channel_options"]["sms"]["text"] = text_message
    request_params["channel_options"]["sms"]["alpha_name"] = ALPHA_NAME

    # send messages and get reports
    sms = ApiMTS()
    if sms.send_messages(request_params=request_params) == 200:
        FileOperations().save_request_params(request_params=request_params)

    sms.get_report(extra_id_list=extra_id_list)


if __name__ == "__main__":
    get_data()