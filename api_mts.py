import os, json, time
import ssl
import certifi
import requests
from dotenv import load_dotenv
from file_operations import FileOperations
from utils import create_extra_id
from createrp import OneMessage


class ApiMTS:
    ''' Class for sending messages and get reports '''
    
    def __init__(self) -> None:
        
        # get environment variables
        load_dotenv()
        self.CLIENT_ID = os.getenv("CLIENT_ID")
        self.LOGIN = os.getenv("LOGIN")
        self.PASSWORD = os.getenv("PASSWORD")


    def get_url(self, by:str, var=None) -> str:
        ''' this method is for get url
         if you get url for send message just define "by" parametr,
         if you get url for get_report define "by" and
         "job_id" or "exrta_id" or "message_id" parametrs '''
        load_dotenv()
        if var:
            return os.getenv(by.upper()).format(client_id=self.CLIENT_ID, var=var)   
        else:
            return os.getenv(by.upper()).format(client_id=self.CLIENT_ID)
            

    def send_message(self, by:str, request_params:dict) -> dict:
        ''' this method is for send messages as one as mass '''
        # url = self.get_url(by=by)
        # response = requests.post(url=url, json=request_params, auth=(self.LOGIN, self.PASSWORD), verify=os.getenv("PATH_CA"))
        # response_json = response.json()
        # response_json["status_code"] = int(response.status_code)
        # print('\nThe message delivering script was succesfully.')
        # return {"http_code": int(response.status_code), "response_json": response_json}
        pass
    

    def get_report(self, by:str, var:str) -> dict:
        ''' method for get reports
         you should define "by" and "job_id" or "exrta_id" or "message_id" parametrs '''
        # url = self.get_url(by=by, var=var)
        # right_resp = False
        # seconds = 0
        # limit_seconds = 180
        # print("Waiting response from server for get delivering report...")
        # while not right_resp:
        #     if seconds >= limit_seconds:
        #         text_exception = f"The seconds count waiting for a response to receive a report has exceeded {limit_seconds} seconds."
        #         print(text_exception)
        #         break
        #     else:
        #         response = requests.get(url=url, auth=(self.LOGIN, self.PASSWORD), verify=os.getenv("PATH_CA"))
        #         if int(response.status_code) == 200:
        #             right_resp = True
        #             print("The report recieving script was succesfully.")
        #         else:
        #             seconds += 2
        #             time.sleep(2)

        # response_json = response.json()
        # http_code = int(response.status_code)
        # response_json["status_code"] = http_code
        # return {"http_code": http_code, "response_json": response_json}
        pass
        

    def send_broadcast_mass_messages_and_get_report_by_job_id(self, request_params:dict):
        ''' the popular request method for sennding mass messages using
         by broadcast and get report by job_id for full company '''
        # if not request_params["recipients"]:
        #     print("Recipients don't exist")
        #     return
        # _message = self.send_message(by="SM_MASS_BROADCAST", request_params=request_params)
        # message_resp_json = _message["response_json"]
        # job_id = message_resp_json["job_id"].strip()
        # _report = self.get_report(by="GR_JOB_ID", var=job_id)
        # return {"resp_message": message_resp_json,
        #         "sm_http_code": _message["http_code"],
        #         "resp_report": _report["response_json"],
        #         "gr_http_code": _report["http_code"]}
        pass

    
    def send_broadcast_sync_mass_messages_and_get_report_by_message_id(self, request_params:dict) -> dict:
        ''' another popular request method for sending mass messages
         using by braodcast and get report for ever message by message_id '''
        _message = self.send_message(by="SM_MASS_BROADCAST_SYNC", request_params=request_params)
        message_resp_json = _message["response_json"]
        message_id_list = []
        for messages in message_resp_json["messages"]:
            message_id_list.append(messages["message_id"])
        report_list = []
        for message_id in message_id_list:
            _report = self.get_report(by="GR_MESSAGE_ID_ADVANCED", var=message_id)
            report_list.append(_report["response_json"])
        return {"resp_message": message_resp_json,
                "sm_http_code": _message["http_code"],
                "resp_report": report_list,
                "gr_http_code": _report["http_code"]}


    def send_one_message_and_get_report_by_message_id(self, request_params:dict) -> dict:
        ''' another popular method for sending one message and get report by message_id'''
        _message = self.send_message(by="SM_ONE_MESSAGE", request_params=request_params)
        message_resp_json = _message["response_json"]
        message_id = message_resp_json["message_id"].strip()
        _report = self.get_report(by="GR_MESSAGE_ID_ADVANCED", var=message_id)
        return {"resp_message": message_resp_json,
                "sm_http_code": _message["http_code"],
                "resp_report": _report["response_json"],
                "gr_http_code": _report["http_code"]}
        

    def notice_report(self, fail=False) -> None:
        ''' this method sends to defined phone number notice 
        abut exceptions during running key methods '''
        path_text_file_name = "NOTICE_SMS_FAIL_TEXT" if fail else "NOTICE_SMS_SUCCESS_TEXT"
        with open(os.getenv(path_text_file_name), "r", encoding="utf-8") as file:
            text = file.read()
        onemes = OneMessage(text_message=text)
        request_params = onemes.create()
        send_message = self.send_one_message_and_get_report_by_message_id(request_params=request_params)
        fo = FileOperations()
        fo.save_data(data=request_params, path_to_folder=os.getenv("SAVE_REQ_PAR_ONE_MESS"))
        fo.save_data(data=send_message["resp_message"], path_to_folder=os.getenv("SAVE_RESPONSE_DATA"))
        fo.save_data(data=send_message["resp_report"], path_to_folder=os.getenv("SAVE_REPORTS_ONE_MESSAGE"))


def main() -> None:
    apimts = ApiMTS()
    apimts.notice_report()

if __name__ == "__main__":
    main()
