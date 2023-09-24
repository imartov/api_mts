import os, json

from dotenv import load_dotenv

from file_operations import FileOperations


class CheckReport:
    ''' this class is for checking reports and finding error messages '''
    def __init__(self) -> list:
        self.code_status = (1, 3)
        self.code_substatus = (10, 12, 24, 28, 35, 36)
        self.code_msg_status = (36011, 35015, 36021, 36031, 12011, 36041, 36051)
        self.fail_messages = []
        load_dotenv()

    def job_id(self, full_file_name=None):
        ''' checking reports that got using job_id '''
        if not full_file_name:
            fo = FileOperations()
            file_name, full_file_name = fo.create_file_name_by_date(path_to_folder=os.getenv("SAVE_REPORTS"))
        with open(full_file_name, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        for delivering in data:
            for message in delivering["messages"]:
                if ("error_text" in message or "error_code" in message or
                   ("status" in message and message["status"] in self.code_status) or
                   ("substatus" in message and message["substatus"] in self.code_substatus) or
                   ("msg_status" in message and message["msg_status"] in self.code_msg_status)):
                    
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
            fo.save_data(data=self.fail_messages, path_to_folder=os.getenv("SAVE_FAIL_MESSAGES"))
        return self.fail_messages
    
    def message_id_advanceed(self, full_file_name=None):
        return self.fail_messages

    def message_id_simple(self, full_file_name=None):
        return self.fail_messages

    def extra_id_advanceed(self, full_file_name=None):
        return self.fail_messages

    def extra_id_simple(self, full_file_name=None):
        return self.fail_messages


if __name__ == "__main__":
    p = CheckReport()
    p.job_id()