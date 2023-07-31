import json, os
from dotenv import load_dotenv
from api_mts import ApiMTS
from file_operations import FileOperations
from utils import create_extra_id


class GetData:
    def __init__(self) -> None:
        pass
    

    def get_request_params_mass_broadcast(self, sync=False) -> dict:
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
        return request_params


    def get_request_params_one_message(self, text:str, phone_number:int) -> dict:
        ''' this method if for getting data for send message about success messages-delivering '''
        with open("test_data\\success\\request_params.json", "r", encoding="utf-8") as file:
            request_params = json.load(file)

        # get environment variables and generate extra_id and set data for request params
        load_dotenv()
        request_params["phone_number"] = phone_number
        request_params["channel_options"]["sms"]["text"] = text
        request_params["extra_id"] = create_extra_id()
        request_params["channel_options"]["sms"]["alpha_name"] = os.getenv("ALPHA_NAME")
        return request_params


if __name__ == "__main__":
    p = GetData().get_request_params_one_message(text="random", phone_number=123)
    print(p)