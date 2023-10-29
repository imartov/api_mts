import os, json
from datetime import datetime, timedelta

from dotenv import load_dotenv

from file_operations import FileOperations
from get_data import GetData


class CheckReportJobId:
    ''' this class is for checking reports and finding error messages '''
    def __init__(self) -> None:
        self.error_code_status = (1, 3)
        self.error_code_substatus = (10, 12, 24, 28, 35, 36)
        self.error_code_msg_status = (36011, 35015, 36021, 36031, 12011, 36041, 36051)
        self.fo = FileOperations()
        load_dotenv()
    
    def create_update_success_messages(self,
                                       request_params=None,
                                       report=None,
                                       double=False,
                                       days=3) -> None:
        ''' this method checks request_params and reports and
        define success messages and fail messages and:
        1. rewrite success_messages.json
        2. rewrite fail_messages.json
        3. create file by date in success messages folder and 
           pass it defined today success messages
        4. create file by date in fail messages folder and 
           pass it defined today fail messages.

        If double=True this method is apply for double delivering '''

        path_reqpar = "SAVE_DOUBLE_REQ_PAR_MASS_BROAD" if double else "SAVE_FIRST_REQ_PAR_MASS_BROAD"
        path_report = "SAVE_DOUBLE_REPORTS_JOB_ID" if double else "SAVE_FIRST_REPORTS_JOB_ID"
        path_save = "SAVE_SUCCESS_MESSAGES_DOUBLE" if double else "SAVE_SUCCESS_MESSAGES_FIRST"
        path_file = "SAVE_FILE_SUCCESS_MESSAGES_DOUBLE" if double else "SAVE_FILE_SUCCESS_MESSAGES_FIRST"
        check_day = datetime.today().date() - timedelta(days=days)

        if not request_params:
            request_params = self.fo.get_last_element(path_to_folder=os.getenv(path_reqpar))
            if not request_params:
                return
        if not report:
            report = self.fo.get_last_element(path_to_folder=os.getenv(path_report))
            if not report:
                return
        
        all_success_messages = self.fo.get_data_from_json_file(path_file=os.getenv(path_file))
        all_fail_messages = self.fo.get_data_from_json_file(path_file=os.getenv("FILE_FAIL_MESSAGES"))
        last_message_time = datetime.strftime(datetime.fromtimestamp(report["messages"][-1]["time"] / 1000),
                                              self.fo.strftime_datatime_format)
        date_time = request_params["datetime"] if "datetime" in request_params else last_message_time
        check_day = datetime.strptime(last_message_time, self.fo.strftime_datatime_format).date() - timedelta(days=days)

        for message in report["messages"]:
            for recipient in request_params["recipients"]:
                if message["extra_id"] == recipient["extra_id"]:
                    # save success messages
                    if (("status_text" in message and message["status_text"] == "SMS delivered") and
                        ("msg_status" in message and message["msg_status"] == 23011)):
                        
                        # write into file by date success messages
                        data = {}
                        data[str(recipient["unp"])] = {
                            "company_name": recipient["company_name"],
                            "payment_date": recipient["payment_date"],
                            "phone_number": recipient["phone_number"],
                            "extra_id": recipient["extra_id"],
                            "delivering_date": date_time
                        }
                        print(data)
                        self.fo.save_data(data=data, path_to_folder=os.getenv(path_save))

                        # delete from fail_messages.json the message if it was success
                        if str(recipient["unp"]) in all_fail_messages:
                            if recipient["payment_date"] == all_success_messages[str(recipient["unp"])]["payment_date"]:
                                del all_fail_messages[str(recipient["unp"])]
                            else:
                                # update message in success_messages.json if payment_date != payment_date
                                all_success_messages[str(recipient["unp"])] = {
                                    "company_name": recipient["company_name"],
                                    "payment_date": recipient["payment_date"],
                                    "phone_number": recipient["phone_number"],
                                    "extra_id": recipient["extra_id"],
                                    "delivering_date": date_time
                                }
                        
        #                 # write into success_messages.json if unp doesn't exist in success_messages.json
        #                 elif str(recipient["unp"]) not in all_success_messages:
        #                     all_success_messages[str(recipient["unp"])] = {
        #                         "company_name": recipient["company_name"],
        #                         "payment_date": recipient["payment_date"],
        #                         "phone_number": recipient["phone_number"],
        #                         "extra_id": recipient["extra_id"],
        #                         "delivering_date": date_time
        #                     }
        #             # save fail messages
        #             else:
        #                 # write into file by date fail messages
        #                 data = {}
        #                 data[str(recipient["unp"])] = {
        #                     "company_name": recipient["company_name"],
        #                     "payment_date": recipient["payment_date"],
        #                     "phone_number": recipient["phone_number"],
        #                     "extra_id": recipient["extra_id"],
        #                     "delivering_date": date_time
        #                 }
        #                 self.fo.save_data(data=data, path_to_folder=os.getenv("FOLDER_FAIL_MESSAGES"))

        #                 # delete from success_messages.json the message if it was fail
        #                 if str(recipient["unp"]) in all_success_messages:
        #                     del all_success_messages[str(recipient["unp"])]

        #                 # update message in fail_messages.json if payment_date != payment_date
        #                 if str(recipient["unp"]) in all_fail_messages:
        #                     if recipient["payment_date"] != all_fail_messages[str(recipient["unp"])]["payment_date"]:
        #                         all_fail_messages[str(recipient["unp"])] = {
        #                             "company_name": recipient["company_name"],
        #                             "payment_date": recipient["payment_date"],
        #                             "phone_number": recipient["phone_number"],
        #                             "extra_id": recipient["extra_id"],
        #                             "delivering_date": date_time
        #                         }
                        
        #                 # write into fail_messages.json if unp doesn't exist in fail_messages.json
        #                 elif str(recipient["unp"]) not in all_fail_messages:
        #                     all_fail_messages[str(recipient["unp"])] = {
        #                         "company_name": recipient["company_name"],
        #                         "payment_date": recipient["payment_date"],
        #                         "phone_number": recipient["phone_number"],
        #                         "extra_id": recipient["extra_id"],
        #                         "delivering_date": date_time
        #                     }

        # with open(os.getenv(path_file), "w", encoding="utf-8") as file:
        #     json.dump(all_success_messages, file, indent=4, ensure_ascii=False)
        # with open(os.getenv("FILE_FAIL_MESSAGES"), "w", encoding="utf-8") as file:
        #     json.dump(all_fail_messages, file, indent=4, ensure_ascii=False)


class CheckRequestParams:
    def __init__(self) -> None:
        pass


if __name__ == "__main__":
    fo = FileOperations()
    rq = fo.get_last_element(path_file="test_data\\request_params\\mass_broadcast\\double\\29_10_2023.json")
    report = fo.get_last_element(path_file="sent_messages\\reports\job_id\\double\\29_10_2023.json")
    cr = CheckReportJobId()
    cr.create_update_success_messages(request_params=rq, report=report, double=True)






    # TODO: create method for change same debtor in 3-days (first) list if updated payment_day
    # TODO: create method for to drop recipients of 3-days list when for request_params if before 3 day
