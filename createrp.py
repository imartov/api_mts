import os, json
from datetime import datetime, timedelta

from dotenv import load_dotenv

from utils import create_extra_id
from file_operations import FileOperations


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
        
    def get_first_request_params_minus_double(self,
                                              request_params:dict,
                                              double_request_params:dict) -> dict:
        ''' this method returns request_params and drops recipients of double request_params '''
        double_unp_list = []
        for double_recipient in double_request_params["recipients"]:
            double_unp_list.append(double_recipient["unp"])
        
        first_recipients = []
        for recipient in request_params["recipients"]:
            if recipient["unp"] not in double_unp_list:
                first_recipients.append(recipient)
        request_params["recipients"] = first_recipients
        return request_params
    
    def get_double_request_params(self, request_params:dict, days=3, double=False) -> dict:
        ''' this method returns request_params for double message delivering with another text
         if double=True returned dict of requests params uncludes recipients that double
         message delivering was sent and they haven't to get a message on this delivering '''
        path_success = "SAVE_SUCCESS_MESSAGES_DOUBLE" if double else "SAVE_SUCCESS_MESSAGES_FIRST"
        print('path_success: ', path_success)
        files_list = os.listdir(os.getenv(path_success))
        fo = FileOperations()
        files_count = len(files_list)
        check_files_list = []
        if double:
            check_files_list = files_list
            print('check_files_list: ', check_files_list)
        else:
            now = datetime.now().date()
            check_day = now - timedelta(days=days)
            prev_days = 0
            for i in range(1, files_count+1):
                check_day = check_day - timedelta(days=prev_days)
                check_file = fo.create_file_name_by_date(date=check_day)
                if check_file in files_list:
                    check_files_list.append(check_file)
                prev_days += 1

        full_check_messages = []
        for file_name in check_files_list:
            full_file_name = os.getenv(path_success) + "\\" + file_name
            with open(full_file_name, "r", encoding="utf-8") as file:
                success_messages_list = json.load(file)
            full_check_messages += success_messages_list
            print(full_check_messages)

        exist_unp_recipients = []
        double_recipients = []
        for message in full_check_messages:
            for recipient in request_params["recipients"]:
                if message["unp"] == recipient["unp"] and message["unp"] not in exist_unp_recipients:
                    if message["payment_date"] == recipient["payment_date"]:
                        exist_unp_recipients.append(message["unp"])
                        double_recipients.append(recipient)
        print('double_recipients: ', double_recipients)
        
        if double_recipients:
            with open(os.getenv("PATH_EXAM_MASS_BRO_DOUBLE_TEXT_MESS"), "r", encoding="utf-8") as file:
                text_message = file.read()
            double_request_params = self.create(recipients=double_recipients)
            double_request_params = self.update_extra_id(request_params=double_request_params)
            double_request_params["channel_options"]["sms"]["text"] = text_message
            return double_request_params
        
    def get_first_and_double_request_params(self,
                                            request_params:dict,
                                            days=3,
                                            double=False) -> tuple:
        ''' this method calls self.get_double_request_params and
         self.get_first_request_params_minus_double and returns
         first_request_params and double_request_params '''
        double_request_params = self.get_double_request_params(request_params=request_params,
                                                               days=days,
                                                               double=double)
        first_request_params = self.get_first_request_params_minus_double(request_params=request_params,
                                                                          double_request_params=double_request_params)
        if first_request_params["recipients"]:
            return first_request_params, double_request_params
        else:
            return None, double_request_params


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
        self.request_params = set_authorization_data(request_params=self.request_params,
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


def main() -> None:
    cr = MassBroadcast()
    cr.get_request_params_minus_success_messages()

if __name__ == "__main__":
    main()
