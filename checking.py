import os, json
from datetime import datetime, timedelta

from dotenv import load_dotenv
from loguru import logger

from file_operations import FileOperations, report_message_form


success_statuses = {
    "msg_status": 23011,
    "substatus": 23,
    "status": 2,
    "status_text": "SMS delivered"
}

error_statuses = {
    "msg_status": [36011, 35015, 36021, 36031, 12011, 36041, 36051],
    "substatus": [10, 12, 24, 28, 35, 36],
    "status": [1, 3]
}

# logger.add("debug.log", format='{time} | {level} | {file} | {name} | {function} | {line} | {message}', level='DEBUG', rotation='1 week', compression='zip')
fo = FileOperations()
load_dotenv()

class CheckReportJobId:
    ''' this class is for checking reports and finding error messages '''
    def __init__(self) -> None:
        pass
    
    def create_update_success_fail_messages(self, request_params=None,
                                            report=None, double=False) -> None:
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
        if not request_params:
            path_reqpar = "SAVE_DOUBLE_REQ_PAR_MASS_BROAD" if double else "SAVE_FIRST_REQ_PAR_MASS_BROAD"
            request_params = fo.get_last_element(path_to_folder=os.getenv(path_reqpar))
            if not request_params:
                return
        if not report:
            path_report = "SAVE_DOUBLE_REPORTS_JOB_ID" if double else "SAVE_FIRST_REPORTS_JOB_ID"
            report = fo.get_last_element(path_to_folder=os.getenv(path_report))
            if not report:
                return

        last_message_time = datetime.strftime(datetime.fromtimestamp(report["messages"][-1]["time"] / 1000),
                                              fo.strftime_datatime_format)
        date_time = request_params["datetime"] if "datetime" in request_params else last_message_time

        temp_success_messages = {}
        temp_fail_messages = {}
        
        for message in report["messages"]:
            for recipient in request_params["recipients"]:
                str_unp = str(recipient["unp"])
                if message["extra_id"] == recipient["extra_id"]:
                    # save success messages
                    if self.check_success_status(msg_report=message):
                        temp_success_messages[str_unp] = {
                            "company_name": recipient["company_name"],
                            "payment_date": recipient["payment_date"],
                            "phone_number": recipient["phone_number"],
                            "extra_id": recipient["extra_id"],
                            "delivering_date": date_time
                        }
                    # save fail messages
                    else:
                        temp_fail_messages[str_unp] = {
                            "company_name": recipient["company_name"],
                            "payment_date": recipient["payment_date"],
                            "phone_number": recipient["phone_number"],
                            "extra_id": recipient["extra_id"],
                            "delivering_date": date_time
                        }

        fo.save_file(data_list=temp_success_messages, full_file_name=os.getenv("TEMP_SENT_SUCCESS_MESSAGES"))
        fo.save_file(data_list=temp_fail_messages, full_file_name=os.getenv("TEMP_SENT_FAIL_MESSAGES"))

        count_success = len(temp_success_messages)
        count_fail = len(temp_fail_messages)

        path_save = "SAVE_SUCCESS_MESSAGES_DOUBLE" if double else "SAVE_SUCCESS_MESSAGES_FIRST"
        path_file = "SAVE_FILE_SUCCESS_MESSAGES_DOUBLE" if double else "SAVE_FILE_SUCCESS_MESSAGES_FIRST"

        # pass, update and delete all_success_messages (success_messages.json)
        all_success_messages = fo.get_data_from_json_file(path_file=os.getenv(path_file))
        all_success_messages.update(temp_success_messages)
        with open(os.getenv(path_file), "w", encoding="utf-8") as file:
            json.dump(all_success_messages, file, indent=4, ensure_ascii=False)
        fo.save_data(data=temp_success_messages, path_to_folder=os.getenv(path_save))
        os.remove(os.getenv("TEMP_SENT_SUCCESS_MESSAGES"))
        
        # pass, update and delete all_fail_messages
        all_fail_messages = fo.get_data_from_json_file(path_file=os.getenv("FILE_FAIL_MESSAGES"))
        all_fail_messages.update(temp_fail_messages)
        with open(os.getenv("FILE_FAIL_MESSAGES"), "w", encoding="utf-8") as file:
            json.dump(all_fail_messages, file, indent=4, ensure_ascii=False)
        fo.save_data(data=temp_fail_messages, path_to_folder=os.getenv("FOLDER_FAIL_MESSAGES"))
        os.remove(os.getenv("TEMP_SENT_FAIL_MESSAGES"))
        logger.info("End 'checking.CheckReportJobId.create_update_success_fail_messages' method")
        return count_success, count_fail


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
                payment_date_save = datetime.strptime(success_data_save["payment_date"], "%d.%m.%Y").date()
                payment_date_remove = datetime.strptime(success_messages_remove[unp]["payment_date"], "%d.%m.%Y").date()
                if deliv_date_save > deliv_date_remove or payment_date_save > payment_date_remove:
                    del success_messages_remove[unp]
        fo.save_file(data_list=success_messages_remove, full_file_name=os.getenv(path_success_file_name_remove))
        logger.info("End 'checking.CheckReportJobId.remove_success_messages' method")


    def check_success_status(self, msg_report:dict) -> bool:
        ''' метод проверяет статус доставки сообщения
        при успешной доставке метод возвращает True, иначе - None '''
        if "msg_status" in msg_report and "substatus" in msg_report and "status" in msg_report:
            if msg_report["msg_status"] == success_statuses["msg_status"] and\
            msg_report["substatus"] == success_statuses["substatus"] and\
            msg_report["status"] == success_statuses["status"]:
                return True
        return
    

    def check_error_status(self, msg_report:dict) -> bool:
        ''' метод проверяет статус доставки сообщения
        при неуспешной доставке метод возвращает True, иначе - None '''
        if "error_code" in msg_report:
            return True
        return

    
    def check_count_messages(self, messages:list, recipients=None, double=False) -> bool:
        ''' this method checks if count of recipients equal count of messages of report
            the method will return False if values not equal and True if equal
        '''
        logger.info("Start 'checking.CheckReportJobId.check_count_messages' method")
        if not recipients:
            path_folder = os.getenv("SAVE_DOUBLE_REQ_PAR_MASS_BROAD") if double else os.getenv("SAVE_FIRST_REQ_PAR_MASS_BROAD")
            recipients = fo.get_last_element(path_folder=path_folder)["recipients"]
        logger.info("End 'checking.CheckReportJobId.check_count_messages' method")
        if len(messages) != len(recipients):
            return False
        return True

    def get_missing_messages(self, messages:list, recipients=None, double=False) -> list:
        if not recipients:
            path_folder = os.getenv("SAVE_DOUBLE_REQ_PAR_MASS_BROAD") if double else os.getenv("SAVE_FIRST_REQ_PAR_MASS_BROAD")
            recipients = fo.get_last_element(path_folder=path_folder)["recipients"]
        messages_extra_id_list = []
        recipients_extra_id_list = []
        for recipient in recipients:
            recipients_extra_id_list.append(recipient["extra_id"])
        for message in messages:
            messages_extra_id_list.append(message["extra_id"])
        missing_extra_id_list = []
        for recipient_extra_id in recipients_extra_id_list:
            if recipient_extra_id not in messages_extra_id_list:
                missing_extra_id_list.append(recipient_extra_id)
        print(len(missing_extra_id_list))
        return missing_extra_id_list


class CheckRequestParams:
    def __init__(self) -> None:
        pass


def main():
    pass

if __name__ == "__main__":
    main()
