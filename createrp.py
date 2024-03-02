import os, json
from datetime import datetime, timedelta

from dotenv import load_dotenv
from loguru import logger

from utils import create_extra_id, get_request_params_minus_messages
from file_operations import FileOperations


# logger.add("debug.log", format='{time} | {level} | {file} | {name} | {function} | {line} | {message}', level='DEBUG', rotation='1 week', compression='zip')

fo = FileOperations()
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
        self.request_params = set_authorization_data(request_params=self.request_params,
                                                    alpha_name=alpha_name,
                                                    ttl=ttl)

    def create(self, phone_number=None,
                company_name=None,
                debt_sum=None, unp=None,
                payment_date=None,
                recipients=None) -> dict:
        if recipients:
            self.request_params["recipients"] = recipients
        else:
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
    
    
    def empty_create(self, **kwargs) -> dict:
        return self.request_params
    

    def update_extra_id(self, request_params=None, recipients=None):
        ''' this method updates extra_id in list of recipients '''
        if request_params:
            for recipient in request_params["recipients"]:
                recipient["extra_id"] = create_extra_id()
            return request_params
        if recipients:
            for recipient in recipients:
                recipient["extra_id"] = create_extra_id()
            return recipients
    
    def get_first_and_double_request_params(self, request_params:dict, days=2, minus=True) -> dict:
        ''' this method returns first request_params and double request params.
        If minus=True the method will return first request_param minus double request params '''
        logger.info("Start 'createrp.MassBroadcast.get_first_and_double_request_params' method")
        all_first_success_messages = fo.get_data_from_json_file(path_file=os.getenv("SAVE_FILE_SUCCESS_MESSAGES_FIRST"))
        check_day = datetime.today().date() - timedelta(days=days)
        minus_recipients = {}
        double_recipients = []
        for recipient in request_params["recipients"]:
            str_unp = str(recipient["unp"])
            if str_unp in all_first_success_messages:
                if recipient["payment_date"] == all_first_success_messages[str_unp]["payment_date"]:
                    delivering_date = datetime.strptime(all_first_success_messages[str_unp]["delivering_date"],
                                                        fo.strftime_datatime_format).date()
                    if delivering_date <= check_day:
                        double_recipients.append(recipient)
                        if minus:
                            minus_recipients[str_unp] = {
                                "company_name": recipient["company_name"],
                                "payment_date": recipient["payment_date"],
                                "phone_number": recipient["phone_number"],
                                "extra_id": recipient["extra_id"]
                            }
        
        with open(os.getenv("SAVE_FILE_SUCCESS_MESSAGES_FIRST"), "w", encoding="utf-8") as file:
            json.dump(all_first_success_messages, file, indent=4, ensure_ascii=False)
        
        if minus:
            request_params = get_request_params_minus_messages(request_params=request_params,
                                                               data=minus_recipients)
        if double_recipients:
            with open(os.getenv("PATH_EXAM_MASS_BRO_DOUBLE_TEXT_MESS"), "r", encoding="utf-8") as file:
                text_message = file.read()
            double_request_params = self.create(recipients=double_recipients)
            double_request_params = self.update_extra_id(request_params=double_request_params)
            double_request_params["channel_options"]["sms"]["text"] = text_message
            fo.save_data(data=double_request_params, path_to_folder=os.getenv("VIRGIN_DOUBLE_REQ_PAR_MASS_BROAD"))
            logger.info("Start 'createrp.MassBroadcast.get_first_and_double_request_params' method")
            return request_params, double_request_params
        else:
            logger.info("End 'createrp.MassBroadcast.get_first_and_double_request_params' method")
            return request_params, None


class OneMessage:
    def __init__(self, text_message=None, alpha_name=None, ttl=300) -> None:
        self.request_params = fo.get_data_from_json_file(path_file=os.getenv("PATH_EXAM_ONE_MESS_REQ_PAR"))    
        if not text_message:
            with open(os.getenv("PATH_EXAM_ONE_MESS_TEXT_MESS"), "r", encoding="utf-8") as file:
                text_message = file.read()
            self.request_params["channel_options"]["sms"]["text"] = text_message
        else:
            self.request_params["channel_options"]["sms"]["text"] = text_message
        self.request_params = set_authorization_data(request_params=self.request_params,
                                                     alpha_name=alpha_name,
                                                     ttl=ttl)
    
    def create(self, phone_number=None) -> dict:
        if not phone_number:
            phone_number = int(os.getenv("INFO_PHONE_NUMBER"))
            self.request_params["phone_number"] = phone_number
        else:
            self.request_params["phone_number"] = phone_number
        self.request_params["extra_id"] = create_extra_id()
        return self.request_params


def main() -> None:
    pass

if __name__ == "__main__":
    main()
