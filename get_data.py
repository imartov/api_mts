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

    # send messages
    message = ApiMTS()
    send_messages = send_messages(request_params=request_params)

    # create instance of FileOperations
    file_operations = FileOperations()

    # save request params
    if send_messages["http_code"] == 200:
        file_operations.save_data(data=request_params, path_to_folder="sent_messages\\request_params")
    else:
        file_operations.save_data(data=request_params, path_to_folder="sent_messages\\request_params_error")

    # save response data
    file_operations.save_data(data=send_messages["resp_json"], path_to_folder="sent_messages\\response_data")

    # get advanced report
    report = message.get_report_by_message_id(extra_id_list=extra_id_list)
    file_operations.save_data(data=report, path_to_folder="sent_messages\\reports\\advanced")

# TODO: add delete data after month
# TODO: delete sync and do report-request


if __name__ == "__main__":
    get_data()