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

        def create(self, phone_number:int, company_name:str, debt_sum:str, unp:int, payment_date:str) -> dict:
            extra_id = create_extra_id()
            recipient = {
                "phone_number": phone_number,
                "extra_id": extra_id,
                "company_name": company_name,
                "debt_sum": debt_sum,
                "unp": unp,
                "payment_date": payment_date
            }
            self.request_params["recipients"].append(recipient)
            return self.request_params
    
    class OneMessage:
        def __init__(self, text_message=None, alpha_name=None, ttl=300) -> None:
            with open(os.getenv("PATH_EXAM_ONE_MESS_REQ_PAR"), "r", encoding="utf-8") as file:
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
        def create(self, phone_number=None) -> dict:
            if not phone_number:
                phone_number = os.getenv("INFO_PHONE_NUMBER")
                self.request_params["phone_number"] = phone_number
            else:
                self.request_params["phone_number"] = phone_number
            self.request_params["extra_id"] = create_extra_id()
            return self.request_params


if __name__ == "__main__":
    p = RequestParams.MassBroadcast().create()
