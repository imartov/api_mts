import json, os
from dotenv import load_dotenv
from api_mts import ApiMTS
from file_operations import FileOperations
from utils import create_extra_id


def get_data() -> None:
    ''' получение параметров для запроса '''
    with open("test_data\\broadcast\\request_params.json", "r", encoding="utf-8") as file:
        request_params = json.load(file)

    # get text message
    with open("test_data\\broadcast\\text_message.txt", "r", encoding="utf-8") as file:
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
    file_operations.save_data_using_popular_api_methods(response_data=send_messages["resp_message"],
                                                        reports=send_messages["resp_report"],
                                                        request_params=request_params)


if __name__ == "__main__":
    get_data()