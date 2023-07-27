import json, os
from dotenv import load_dotenv
from api_mts import ApiMTS
from file_operations import FileOperations
from utils import create_extra_id


def get_data_mass_broadcast(sync=False) -> dict:
    ''' this method connetcs to database and get data for mass broadcast delivering '''
    with open("test_data\\broadcast\\request_params.json", "r", encoding="utf-8") as file:
        request_params = json.load(file)

    # get text message
    with open("test_data\\broadcast\\text_message.txt", "r", encoding="utf-8") as file:
        text_message = file.read()

    # get environment variables and generate extra_id and set to recipients list
    load_dotenv()
    extra_id_list = []
    for recipient in request_params["recipients"]:
        extra_id = create_extra_id()
        extra_id_list.append(extra_id)
        recipient["extra_id"] = extra_id

    # set text message and alfa name
    request_params["channel_options"]["sms"]["text"] = text_message
    request_params["channel_options"]["sms"]["alpha_name"] = os.getenv("ALPHA_NAME")

    # saving request params
    file_operations = FileOperations()
    file_operations.save_data_using_popular_api_methods(request_params=request_params)
    return request_params


if __name__ == "__main__":
    get_data_mass_broadcast()