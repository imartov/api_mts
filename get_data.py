import json, os
from dotenv import load_dotenv
from api_mts import ApiMTS
from utils import create_extra_id, FileOperations


def get_data() -> None:
    ''' получение параметров для запроса '''
    with open("test_data\\mass_broadcast.json", "r", encoding="utf-8") as file:
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
    send_messages = message.send_broadcast_mass_messages_and_get_report_by_job_id(request_params=request_params)

    # create instance of FileOperations
    file_operations = FileOperations()

    # save request params, response data and reports data
    file_operations.save_data(data=request_params, path_to_folder="sent_messages\\request_params")
    file_operations.save_data(data=send_messages["resp_message"], path_to_folder="sent_messages\\response_data")
    file_operations.save_data(data=send_messages["resp_report"], path_to_folder="sent_messages\\reports")

# TODO: add delete data after month


if __name__ == "__main__":
    get_data()