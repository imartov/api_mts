import os, json

from dotenv import load_dotenv

from file_operations import FileOperations


class CheckReportJobId:
    ''' this class is for checking reports and finding error messages '''
    def __init__(self) -> None:
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
    
    def create_update_success_messages(self,
                                       request_params=None,
                                       report=None,
                                       double=False) -> list:

        path_reqpar = "SAVE_DOUBLE_REQ_PAR_MASS_BROAD" if double else "SAVE_FIRST_REQ_PAR_MASS_BROAD"
        path_report = "SAVE_DOUBLE_REPORTS_JOB_ID" if double else "SAVE_FIRST_REPORTS_JOB_ID"
        path_save = "SAVE_SUCCESS_MESSAGES_DOUBLE" if double else "SAVE_SUCCESS_MESSAGES_FIRST"
        path_file = "SAVE_FILE_SUCCESS_MESSAGES_DOUBLE" if double else "SAVE_FILE_SUCCESS_MESSAGES_FIRST"

        if not request_params:
            request_params = self.fo.get_last_dict(path_to_folder=os.getenv(path_reqpar))
            if not request_params:
                return
        if not report:
            report = self.fo.get_last_dict(path_to_folder=os.getenv(path_report))
            if not report:
                return
        
        all_success_messages = self.fo.get_data_from_json_file(path_to_file=path_file)
        all_fail_messages = self.fo.get_data_from_json_file(path_to_file=os.getenv("FILE_FAIL_MESSAGES"))

        success_messages = []
        for message in report["messages"]:
            for recipient in request_params["recipients"]:
                if message["extra_id"] == recipient["extra_id"]:
                    # save success messages
                    if (("status_text" in message and message["status_text"] == "SMS delivered") and
                        ("msg_status" in message and message["msg_status"] == 23011)):
                        data = {
                                "unp": recipient["unp"],
                                "company_name": recipient["company_name"],
                                "payment_date": recipient["payment_date"],
                                "phone_number": recipient["phone_number"]
                        }
                        self.fo.save_data(data=data, path_to_folder=os.getenv(path_save))

                        if str(recipient["unp"]) in all_success_messages:
                            if recipient["payment_date"] != all_success_messages[str(recipient["unp"])]["payment_date"]:
                                all_success_messages[str(recipient["unp"])]["payment_date"] = recipient["payment_date"]
                        
                        elif str(recipient["unp"]) not in all_success_messages:
                            all_success_messages[str(recipient["unp"])] = {
                                "company_name": recipient["company_name"],
                                "payment_date": recipient["payment_date"],
                                "phone_number": recipient["phone_number"]
                            }
                        success_messages.append(data)
                    # save fail messages
                    else:
                        data = {
                                "unp": recipient["unp"],
                                "company_name": recipient["company_name"],
                                "payment_date": recipient["payment_date"],
                                "phone_number": recipient["phone_number"]
                        }
                        self.fo.save_data(data=data, path_to_folder=os.getenv(path_save))

                        if str(recipient["unp"]) in all_success_messages:
                            if recipient["payment_date"] != all_success_messages[str(recipient["unp"])]["payment_date"]:
                                all_success_messages[str(recipient["unp"])]["payment_date"] = recipient["payment_date"]
                        
                        elif str(recipient["unp"]) not in all_success_messages:
                            all_success_messages[str(recipient["unp"])] = {
                                "company_name": recipient["company_name"],
                                "payment_date": recipient["payment_date"],
                                "phone_number": recipient["phone_number"]
                            }
                        success_messages.append(data)

        with open(os.getenv(path_file), "w", encoding="utf-8") as file:
            json.dump(all_success_messages, file, indent=4, ensure_ascii=False)


class CheckRequestParams:
    def __init__(self) -> None:
        pass


if __name__ == "__main__":
    p = CheckReportJobId().get_success_messages(double=True)
    print(p)
    # TODO: create method for change same debtor in 3-days (first) list if updated payment_day
    # TODO: create method for to drop recipients of 3-days list when for request_params if before 3 day
