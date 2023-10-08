import os, json

from dotenv import load_dotenv

from file_operations import FileOperations


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
    
    def get_success_messages(self,
                             request_params=None,
                             report=None,
                             double=None) -> list:

        def get_last_dict(path_to_folder:str) -> dict:
            file_name = self.fo.create_file_name_by_date()
            full_file_name = path_to_folder + "\\" + file_name
            if file_name in os.listdir(path_to_folder):
                with open(full_file_name, "r", encoding="utf-8") as file:
                    data = json.load(file).pop()
                return data

        path_reqpar = "SAVE_DOUBLE_VIRGIN_REQ_PAR_MASS_BROAD" if double else "SAVE_FIRST_VIRGIN_REQ_PAR_MASS_BROAD"
        path_report = "SAVE_DOUBLE_REPORTS_JOB_ID" if double else "SAVE_FIRST_REPORTS_JOB_ID"
        path_save = "SAVE_SUCCESS_MESSAGES_DOUBLE" if double else "SAVE_SUCCESS_MESSAGES_FIRST"

        if not request_params:
            request_params = get_last_dict(path_to_folder=os.getenv(path_reqpar))
            if not request_params:
                return
        if not report:
            report = get_last_dict(path_to_folder=os.getenv(path_report))
            if not report:
                return
        
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
                        self.fo.save_data(data=data, path_to_folder=os.getenv(path_save))
                        success_messages.append(data)
        return success_messages


class CheckRequestParams:
    def __init__(self) -> None:
        pass


if __name__ == "__main__":
    p = CheckReportJobId().get_success_messages(double=True)
    print(p)
    # TODO: create method for change same debtor in 3-days (first) list if updated payment_day
    # TODO: create method for to drop recipients of 3-days list when for request_params if before 3 day
