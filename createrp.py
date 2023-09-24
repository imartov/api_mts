import os, json
from dotenv import load_dotenv
from utils import create_extra_id


class RequestParams:
    load_dotenv()
    def set_authorization_data(request_params:dict,
                               alpha_name=None,
                               ttl=300) -> dict:
        if not alpha_name:
            request_params["channel_options"]["sms"]["alpha_name"] = os.getenv("ALPHA_NAME")
        else:
            request_params["channel_options"]["sms"]["alpha_name"] = alpha_name
        request_params["channel_options"]["sms"]["ttl"] = ttl
        return request_params

    class MassBroadcast:
        def __init__(self, text_message=None, alpha_name=None, ttl=300) -> None:
            with open(os.getenv("PATH_EXAM_MASS_BRO_REQ_PAR"), "r", encoding="utf-8") as file:
                self.request_params = json.load(file)
            if not text_message:
                with open(os.getenv("PATH_EXAM_MASS_BRO_TEXT_MESS"), "r", encoding="utf-8") as file:
                    text_message = file.read()
                self.request_params["channel_options"]["sms"]["text"] = text_message
            else:
                self.request_params["channel_options"]["sms"]["text"] = text_message
            self.request_params = RequestParams.set_authorization_data(request_params=self.request_params,
                                                                       alpha_name=alpha_name,
                                                                       ttl=ttl)

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
        def __init__(self, text_message=None, alpha_name=None, ttl=300) -> None:
            with open(os.getenv("PATH_EXAM_ONE_MESS"), "r", encoding="utf-8") as file:
                self.request_params = json.load(file)
            if not text_message:
                with open(os.getenv("PATH_EXAM_ONE_MESS_TEXT_MESS"), "r", encoding="utf-8") as file:
                    text_message = file.read()
                self.request_params["channel_options"]["sms"]["text"] = text_message
            else:
                self.request_params["channel_options"]["sms"]["text"] = text_message
            self.request_params = RequestParams.set_authorization_data(request_params=self.request_params,
                                                                       alpha_name=alpha_name,
                                                                       ttl=ttl)
                
        def create(self) -> dict:
            pass


if __name__ == "__main__":
    p = RequestParams.MassBroadcast()
    p.create(phone_number=123, company_name="ssdc", debt_sum="876")
    p.create(phone_number=456, company_name="LKN", debt_sum="567")
    print(p.request_params)
