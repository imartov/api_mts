import os, json
from datetime import datetime, timedelta

from dotenv import load_dotenv
from loguru import logger

from file_operations import FileOperations, report_message_form


# logger.add("debug.log", format='{time} | {level} | {file} | {name} | {function} | {line} | {message}', level='DEBUG', rotation='1 week', compression='zip')

report_message = {
    "count_success_first_messages": 0,
    "count_success_double_messages": 0,
    "count_unsuccess_first_messages": 0,
    "count_unsuccess_double_messages": 0,
    "all_success_messages": 0,
    "all_unsuccess_messages": 0,
    "percent_success_messages": 0
}

fo = FileOperations()

class CheckReportJobId:
    ''' this class is for checking reports and finding error messages '''
    def __init__(self) -> None:
        self.error_code_status = (1, 3)
        self.error_code_substatus = (10, 12, 24, 28, 35, 36)
        self.error_code_msg_status = (36011, 35015, 36021, 36031, 12011, 36041, 36051)
        load_dotenv()
    
    def create_update_success_fail_messages(self,
                                            request_params=None,
                                            report=None,
                                            double=False,
                                            days=2) -> None:
        ''' this method checks request_params and reports and
        define success messages and fail messages and:
        1. rewrite success_messages.json
        2. rewrite fail_messages.json
        3. create file by date in success messages folder and 
           pass it defined today success messages
        4. create file by date in fail messages folder and 
           pass it defined today fail messages.

        If double=True this method is apply for double delivering '''

        logger.info("Start 'checking.CheckReportJobId.create_update_success_fail_messages' method")
        path_reqpar = "SAVE_DOUBLE_REQ_PAR_MASS_BROAD" if double else "SAVE_FIRST_REQ_PAR_MASS_BROAD"
        path_report = "SAVE_DOUBLE_REPORTS_JOB_ID" if double else "SAVE_FIRST_REPORTS_JOB_ID"

        if not request_params:
            request_params = fo.get_last_element(path_to_folder=os.getenv(path_reqpar))
            if not request_params:
                return
        if not report:
            report = fo.get_last_element(path_to_folder=os.getenv(path_report))
            if not report:
                return

        last_message_time = datetime.strftime(datetime.fromtimestamp(report["messages"][-1]["time"] / 1000),
                                              fo.strftime_datatime_format)
        date_time = request_params["datetime"] if "datetime" in request_params else last_message_time
        # check_day = datetime.strptime(date_time, fo.strftime_datatime_format).date() - timedelta(days=days)

        temp_success_messages = {}
        temp_fail_messages = {}
        
        for message in report["messages"]:
            for recipient in request_params["recipients"]:
                str_unp = str(recipient["unp"])
                if message["extra_id"] == recipient["extra_id"]:
                    # save success messages
                    if (("status_text" in message and message["status_text"] == "SMS delivered") and
                        ("msg_status" in message and message["msg_status"] == 23011)):
                        temp_success_messages[str_unp] = {
                            "company_name": recipient["company_name"],
                            "payment_date": recipient["payment_date"],
                            "phone_number": recipient["phone_number"],
                            "extra_id": recipient["extra_id"],
                            "delivering_date": date_time
                        }
                    # save fail messages
                    else: # TODO: добавить код ошибки и сообщение об ошибке
                        temp_fail_messages[str_unp] = {
                            "company_name": recipient["company_name"],
                            "payment_date": recipient["payment_date"],
                            "phone_number": recipient["phone_number"],
                            "extra_id": recipient["extra_id"],
                            "delivering_date": date_time
                        }

        fo.save_file(data_list=temp_success_messages, full_file_name=os.getenv("TEMP_SENT_SUCCESS_MESSAGES"))
        fo.save_file(data_list=temp_fail_messages, full_file_name=os.getenv("TEMP_SENT_FAIL_MESSAGES"))

        path_save = "SAVE_SUCCESS_MESSAGES_DOUBLE" if double else "SAVE_SUCCESS_MESSAGES_FIRST"
        path_file = "SAVE_FILE_SUCCESS_MESSAGES_DOUBLE" if double else "SAVE_FILE_SUCCESS_MESSAGES_FIRST"

        # pass, update and delete all_success_messages (success_messages.json)
        all_success_messages = fo.get_data_from_json_file(path_file=os.getenv(path_file))
        for unp, deliv_data in temp_success_messages.items():

            if double:
                report_message["count_success_double_messages"] += 1
            else:
                report_message["count_success_first_messages"] += 1

            fo.save_data(data={unp: deliv_data}, path_to_folder=os.getenv(path_save))
            all_success_messages[unp] = deliv_data
        os.remove(os.getenv("TEMP_SENT_SUCCESS_MESSAGES"))
        
        all_fail_messages = fo.get_data_from_json_file(path_file=os.getenv("FILE_FAIL_MESSAGES"))
        for unp, deliv_data in temp_fail_messages.items():

            if double:
                report_message["count_unsuccess_double_messages"] += 1
            else:
                report_message["count_unsuccess_first_messages"] += 1

            # write into file by date fail messages (create file)
            fo.save_data(data={unp: deliv_data}, path_to_folder=os.getenv("FOLDER_FAIL_MESSAGES"))
            all_fail_messages[str_unp] = deliv_data
        os.remove(os.getenv("TEMP_SENT_FAIL_MESSAGES"))

        fo.save_file(data_list=all_success_messages, full_file_name=os.getenv(path_file))
        fo.save_file(data_list=all_fail_messages, full_file_name=os.getenv("FILE_FAIL_MESSAGES"))

        # form of report message
        report_message["all_success_messages"] = report_message["count_success_first_messages"] + report_message["count_success_double_messages"]
        report_message["all_unsuccess_messages"] = report_message["count_unsuccess_first_messages"] + report_message["count_unsuccess_double_messages"]
        with open(os.getenv("JSON_REPORT_MESSAGE"), "r", encoding="utf-8") as file:
            debtor_count_will_send_message = json.load(file)["debtor_count_will_send_message"]
        report_message["percent_success_messages"] = report_message["all_success_messages"] / debtor_count_will_send_message * 100
        report_message_form(labels=report_message)
        logger.info("End 'checking.CheckReportJobId.create_update_success_fail_messages' method")


    def check_exist_success_message(self, unp:str, payment_date:str, days=2, double=None) -> bool:
        ''' this method checks if debtor exists in success_messages
        if method returns True the debtor exists in success_messages and it shouldn't pass to request_params
        if method returns False debtor doesn't exist in success_messages or it exists in first_success_messages
        but it must be get a double message '''
        success_messages_file_name = "SAVE_FILE_SUCCESS_MESSAGES_DOUBLE" if double else "SAVE_FILE_SUCCESS_MESSAGES_FIRST"
        success_messages = fo.get_data_from_json_file(path_file=os.getenv(success_messages_file_name))
        check_day = datetime.now().date() - timedelta(days=days)
        if unp in success_messages:
            rq_payment_date = datetime.strptime(payment_date, "%d.%m.%Y").date()
            sm_payment_date = datetime.strptime(success_messages[unp]["payment_date"], "%d.%m.%Y").date()
            if rq_payment_date > sm_payment_date:
                return False
            else:
                delivering_date = datetime.strptime(success_messages[unp]["delivering_date"],
                                                    fo.strftime_datatime_format).date()
                if not double and check_day >= delivering_date:
                    return False
                return True
            
    def remove_success_messages(self, double=False) -> None:
        ''' this method compares messages of first_success_messages.json
        and double_success_messages.json and if one recipient is in both 
        messages the method removes that have earlier delivering_date'''
        logger.info("Start 'checking.CheckReportJobId.remove_success_messages' method")
        path_success_file_name_save = "SAVE_FILE_SUCCESS_MESSAGES_DOUBLE" if double else "SAVE_FILE_SUCCESS_MESSAGES_FIRST"
        path_success_file_name_remove = "SAVE_FILE_SUCCESS_MESSAGES_DOUBLE" if not double else "SAVE_FILE_SUCCESS_MESSAGES_FIRST"
        
        success_messages_save = fo.get_data_from_json_file(path_file=os.getenv(path_success_file_name_save))
        success_messages_remove = fo.get_data_from_json_file(path_file=os.getenv(path_success_file_name_remove))

        for unp, success_data_save in success_messages_save.items():
            if unp in success_messages_remove:
                deliv_date_save = datetime.strptime(success_data_save["delivering_date"], fo.strftime_datatime_format).date()
                deliv_date_remove = datetime.strptime(success_messages_remove[unp]["delivering_date"], fo.strftime_datatime_format).date()
                if deliv_date_save > deliv_date_remove:
                    del success_messages_remove[unp]
        fo.save_file(data_list=success_messages_remove, full_file_name=os.getenv(path_success_file_name_remove))
        logger.info("End 'checking.CheckReportJobId.remove_success_messages' method")


class CheckRequestParams:
    def __init__(self) -> None:
        pass


def main():
    pass

if __name__ == "__main__":
    main()
