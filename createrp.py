import os, json
from dotenv import load_dotenv
from utils import create_extra_id


class RequestParamsMassBroadcast:
    load_dotenv()

    def __init__(self, text_message=None, alpha_name=None, ttl=300) -> None:
        with open(os.getenv("PATH_EXAM_MASS_BRO_REQ_PAR"), "r", encoding="utf-8") as file:
            self.request_params = json.load(file)
        if not text_message:
            with open(os.getenv("PATH_EXAM_MASS_BRO_TEXT_MESS"), "r", encoding="utf-8") as file:
                text_message = file.read()
            self.request_params["channel_options"]["sms"]["text"] = text_message
        else:
            self.request_params["channel_options"]["sms"]["text"] = text_message
        if not alpha_name:
            self.request_params["channel_options"]["sms"]["alpha_name"] = os.getenv("ALPHA_NAME")
        else:
            self.request_params["channel_options"]["sms"]["alpha_name"] = alpha_name
        self.request_params["channel_options"]["sms"]["ttl"] = ttl

    def create(self, phone_number:int, company_name:str, debt_sum:str) -> dict:
        extra_id = create_extra_id()
        recipient = {
            "phone_number": phone_number,
            "extra_id": extra_id,
            "company_name": company_name,
            "debt_sum": debt_sum
        }
        self.request_params["recipients"].append(recipient)
        return self.request_params


class RequestParamsOneMessage:
    def __init__(self) -> None:
        self.request_params = None

    def create(self) -> dict:
        pass


if __name__ == "__main__":
    pass