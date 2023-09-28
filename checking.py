import os, json
from datetime import datetime, timedelta

from dotenv import load_dotenv

from file_operations import FileOperations


class CheckReport:
    ''' this class is for checking reports and finding error messages '''
    def __init__(self) -> list:
        self.error_code_status = (1, 3)
        self.error_code_substatus = (10, 12, 24, 28, 35, 36)
        self.error_code_msg_status = (36011, 35015, 36021, 36031, 12011, 36041, 36051)
        self.fo = FileOperations()
        self.fail_messages = []
        load_dotenv()

    def job_id_fail(self, full_file_name=None):
        ''' checking reports that got using job_id '''
        if not full_file_name:
            file_name, full_file_name = self.fo.create_file_name_by_date(path_to_folder=os.getenv("SAVE_REPORTS"))
        with open(full_file_name, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        for delivering in data:
            for message in delivering["messages"]:
                if ("error_text" in message or "error_code" in message or
                   (("status" in message and message["status"] in self.error_code_status)) or
                   (("substatus" in message and message["substatus"] in self.error_code_substatus)) or
                   (("msg_status" in message and message["msg_status"] in self.error_code_msg_status))):
                    
                    self.fail_messages.append(
                        {
                            "full_file_name": full_file_name,
                            "message_id": message["message_id"],
                            "extra_id": message["extra_id"],
                            "phone_number": message["phone_number"],
                            "time": delivering["time"]
                        }
                    )
        if self.fail_messages:
            self.fo.save_data(data=self.fail_messages, path_to_folder=os.getenv("SAVE_FAIL_MESSAGES"))
        return self.fail_messages
    
    def job_id_double_mesasge(self, count_days=3):
        datetime_format = self.fo.strftime_datatime_format
        date_format = "%d.%m.%Y"
        phone_numbers_double_message = []
        for report_file_name in os.listdir(os.getenv("SAVE_REPORTS_JOB_ID")):
            full_file_name = os.getenv("SAVE_REPORTS_JOB_ID") + "\\\\" + report_file_name
            with open(full_file_name, "r", encoding="utf-8") as file:
                report_data = json.load(file)
            for delivering in report_data:
                if "messages" in delivering:
                    for message in delivering["messages"]:
                        if ("error_text" in message or "error_code" in message or
                        (("status" in message and message["status"] in self.error_code_status)) or
                        (("substatus" in message and message["substatus"] in self.error_code_substatus)) or
                        (("msg_status" in message and message["msg_status"] in self.error_code_msg_status))):
                            continue
                        else:
                            delivering_date = datetime.strptime(delivering["datetime"], datetime_format)
                            three_days_ago = datetime.now() - timedelta(days=count_days)
                            if delivering_date.strftime(date_format) != three_days_ago.strftime(date_format):
                                phone_numbers_double_message.append(message["phone_number"])
                                
                            
                            
                            
    
    def message_id_advanceed_succes(self, full_file_name=None):
        return self.fail_messages

    def message_id_simple_succes(self, full_file_name=None):
        return self.fail_messages

    def extra_id_advanceed_succes(self, full_file_name=None):
        return self.fail_messages

    def extra_id_simple_succes(self, full_file_name=None):
        return self.fail_messages
    

class CheckRequestParams:
    def __init__(self) -> None:
        pass
    # TODO: check request params




if __name__ == "__main__":
    p = CheckReport()
    p.job_id_double_mesasge()