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
    
    def get_success_messages(self, request_params=None, report=None):
        if not request_params:
            file_name, full_file_name = self.fo.create_file_name_by_date(path_to_folder=os.getenv("SAVE_VIRGIN_REQ_PAR_MASS_BROAD"))
            with open(full_file_name, "r", encoding="utf-8") as file:
                request_params = json.load(file).pop()
        if not report:
            file_name, full_file_name = self.fo.create_file_name_by_date(path_to_folder=os.getenv("SAVE_REPORTS_JOB_ID"))
            with open(full_file_name, "r", encoding="utf-8") as file:
                report = json.load(file).pop()

        success_messages = []
        for message in report["messages"]:
            for recipient in request_params["recipients"]:
                if message["extra_id"] == recipient["extra_id"]:
                    if (("status_text" in message and message["status_text"] == "SMS delivered") and
                        ("msg_status" in message and message["msg_status"] == 23011)):
                        file_name = datetime.strptime(request_params["datetime"], self.fo.strftime_datatime_format)
                        file_name = file_name.strftime("%d_%m_%Y") + ".json"
                        full_file_name = os.getenv("SAVE_SUCCESS_MESSAGES") + file_name
                        print(full_file_name)
                        # success_messages.append(
                        #     {
                        #         valid_date: {

                        #         }
                        #     }
                        # )

            
    
    def job_id_double_mesasge(self, days=3):
        ''' this method checks all job_id reports and rewrite file of success mass delivering '''
        compare_date_format = "%d.%m.%Y"
        for report_file_name in os.listdir(os.getenv("SAVE_REPORTS_JOB_ID")):
            full_file_name = os.getenv("SAVE_REPORTS_JOB_ID") + "\\\\" + report_file_name
            self.job_id_fail(full_file_name=full_file_name)[1]
        self.fo.save_file(data_list=self.success_messages, full_file_name=os.getenv("SAVE_SUCCESS_MESSAGES"))

        request_params = GetData(mass_broadcast=True).parse_xl_double(success_messages=self.success_messages)
        for recipient in request_params["recipients"]:
            for message in self.success_messages:
                valid_delivering_date = datetime.strptime(message["delivering_date"], self.fo.strftime_datatime_format).date()
                delivering_date_sum_days = valid_delivering_date + timedelta(days=days)
                today = datetime.now().date()
                if (delivering_date_sum_days >= today and
                    int(message["phone_number"]) == int(recipient["phone_number"])):
                    print(True)

                # print(delivering_date_sum_days, delivering_date_sum_days.__class__, today, today.__class__)


                # if delivering_date_sum_days >= 
                # print(delivering_date_sum_days)
                # print(valid_delivering_date, date_sum_days)


                # date_sum_days = valid_delivering_date.strftime("%d.%m.%Y")
                # today = datetime.now().strftime("%d.%m.%Y")
                # print(valid_delivering_date, valid_delivering_date.__class__, today, today.__class__)
                # print(valid_delivering_date, datetime.now())
                # if int(message["phone_number"]) == int(recipient["phone_number"]):
                #     print("True")
    

class CheckRequestParams:
    def __init__(self) -> None:
        pass
    # TODO: check request params


if __name__ == "__main__":
    p = CheckReportJobId().get_success_messages()
    print(p)