import os, json
from datetime import datetime, timedelta

from dotenv import load_dotenv

from file_operations import FileOperations
from get_data import GetData


class CheckReportJobId:
    ''' this class is for checking reports and finding error messages '''
    def __init__(self) -> list:
        self.error_code_status = (1, 3)
        self.error_code_substatus = (10, 12, 24, 28, 35, 36)
        self.error_code_msg_status = (36011, 35015, 36021, 36031, 12011, 36041, 36051)
        self.fo = FileOperations()
        self.fail_messages = []
        self.success_messages = []
        load_dotenv()

    def job_id_fail(self, full_file_name=None):
        ''' checking reports that got using job_id '''
        if not full_file_name:
            file_name, full_file_name = self.fo.create_file_name_by_date(path_to_folder=os.getenv("SAVE_REPORTS"))
        with open(full_file_name, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        for delivering in data:
            if "messages" in delivering:
                for message in delivering["messages"]:
                    if (("status_text" in message and message["status_text"] == "SMS delivered") and
                        ("msg_status" in message and message["msg_status"] == 23011)):
                        self.success_messages.append(
                            {
                                "delivering_date": delivering["datetime"],
                                "phone_number": message["phone_number"],
                            }
                        )
                    else:
                        self.fail_messages.append(
                            {
                                "full_file_name": full_file_name,
                                "message_id": message["message_id"],
                                "extra_id": message["extra_id"],
                                "phone_number": message["phone_number"],
                                "datetime": delivering["datetime"]
                            }
                        )
                        
        if self.fail_messages:
            self.fo.save_data(data=self.fail_messages, path_to_folder=os.getenv("SAVE_FAIL_MESSAGES"))
        return self.fail_messages, self.success_messages
    
    def get_success_messages(self, request_params=None, report=None) -> list:

        def get_last_dict(path_to_folder:str) -> dict:
            file_name = self.fo.create_file_name_by_date()
            full_file_name = path_to_folder + "\\" + file_name
            if file_name in os.listdir(path_to_folder):
                with open(full_file_name, "r", encoding="utf-8") as file:
                    data = json.load(file).pop()
                return data

        if not request_params:
            request_params = get_last_dict(path_to_folder=os.getenv("SAVE_VIRGIN_REQ_PAR_MASS_BROAD"))
            if not request_params:
                return
        if not report:
            report = get_last_dict(path_to_folder=os.getenv("SAVE_REPORTS_JOB_ID"))
        
        success_messages = []
        for message in report["messages"]:
            for recipient in request_params["recipients"]:
                if message["extra_id"] == recipient["extra_id"]:
                    if (("status_text" in message and message["status_text"] == "SMS delivered") and
                        ("msg_status" in message and message["msg_status"] == 23011)):
                        data = {
                                "unp": recipient["unp"],
                                "company_name": recipient["company_name"],
                                "payment_date": recipient["payment_date"],
                                "phone_number": recipient["phone_number"]
                        }
                        self.fo.save_data(data=data, path_to_folder=os.getenv("SAVE_SUCCESS_MESSAGES"))
                        success_messages.append(data)
        return success_messages
    
    def get_double_request_params(self, request_params:dict, days=3) -> dict:
        now = datetime.now().date()
        check_day = now - timedelta(days=days)
        files_list = os.listdir(os.getenv("SAVE_SUCCESS_MESSAGES"))
        files_count = len(files_list)
        check_files_list = []
        prev_days = 0
        for i in range(1, files_count+1):
            check_day = check_day - timedelta(days=prev_days)
            check_file = self.fo.create_file_name_by_date(date=check_day)
            if check_file in files_list:
                check_files_list.append(check_file)
            prev_days += 1

        full_check_messages = []
        for file_name in check_files_list:
            full_file_name = os.getenv("SAVE_SUCCESS_MESSAGES") + file_name # maybe bag link path name in .env
            with open(full_file_name, "r", encoding="utf-8") as file:
                success_messages_list = json.load(file)
            full_check_messages += success_messages_list

        recipients = []
        for message in full_check_messages:
            for recipient in request_params["recipients"]:
                if message["unp"] == recipient["unp"]:
                    if message["payment_date"] == recipient["payment_date"]:
                        recipients.append(recipient)
        print(full_check_messages)


class CheckRequestParams:
    def __init__(self) -> None:
        pass
    # TODO: check request params


if __name__ == "__main__":
    p = CheckReportJobId().get_double_request_params(request_params={}, days=1)
    print(p)