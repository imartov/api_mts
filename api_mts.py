import os, json, time
import requests
from dotenv import load_dotenv
from loguru import logger
# from utils import notice_exception


# add logger
logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='100 KB', compression='zip')

class ApiMTS:
    ''' Class for sending messages and getting reports '''
    
    def __init__(self) -> None:
        
        # get environment variables
        load_dotenv()
        self.CLIENT_ID = os.getenv("CLIENT_ID")
        self.LOGIN = os.getenv("LOGIN")
        self.PASSWORD = os.getenv("PASSWORD")


    def get_url(self, by:str, job_id=None, message_id=None, extra_id=None) -> str:
        ''' method for get url '''
        load_dotenv()
        urls_get_reports = {
            "job_id": os.getenv("GR_JOB_ID").format(client_id=self.CLIENT_ID, job_id=job_id),
            "message_id_advanced": os.getenv("GR_MESSAGE_ID_ADVANCED").format(client_id=self.CLIENT_ID, message_id=message_id),
            "message_id_simple": os.getenv("GR_MESSAGE_ID_SIMPLE").format(client_id=self.CLIENT_ID, message_id=message_id),
            "extra_id_advanced": os.getenv("GR_EXTRA_ID_ADVANCED").format(client_id=self.CLIENT_ID, extra_id=extra_id),
            "extra_id_simple": os.getenv("GR_EXTRA_ID_SIMPLE").format(client_id=self.CLIENT_ID, extra_id=extra_id)
        }
        return os.getenv(by.upper()).format(client_id=self.CLIENT_ID)
        # TODO: get active params of method, maybe __namemethod__


    @logger.catch()
    def send_message(self, by:str, request_params:dict) -> dict:
        ''' method for send messages as one as mass '''
        url = self.get_url(send_message=True, by=by)
        response = requests.post(url=url, json=request_params, auth=(self.LOGIN, self.PASSWORD))
        print(f"\nresp_json: {response.json()}")
        return {"http_code": int(response.status_code), "response_json": response.json()}
    

    @logger.catch()
    def get_report(self, by:str, job_id=None, message_id=None, extra_id=None) -> dict:
        ''' method for get reports '''
        url = self.get_url(get_report=True, by=by, job_id=job_id, message_id=message_id, extra_id=extra_id)
        right_resp = False
        seconds = 0
        while not right_resp:
            if seconds >= 120:
                # TODO: notice 
                break
            else:      
                response = requests.get(url=url, auth=(self.LOGIN, self.PASSWORD))
                if int(response.status_code) == 200:
                    right_resp = True
                else:
                    seconds += 2
                    time.sleep(2)
        return {"http_code": int(response.status_code), "response_json": response.json()}
    

    def send_broadcast_mass_messages_and_get_report_by_job_id(self, request_params:dict) -> dict:
        ''' the popular request method for sennding mass messages using
         by broadcast and getting report by job_id for full company '''
        try:
            message = self.send_message(by="mass_broadcast", request_params=request_params)
            message_resp_json = message["response_json"]
            job_id = message_resp_json["job_id"].strip()
            report = self.get_report(by="job_id", job_id=job_id)
            print("\nresp_message", message_resp_json)
            print("resp_report", report["response_json"])
            return {"resp_message": message_resp_json, "resp_report": report["response_json"]}
        except Exception as text_exception:
            notice_exception(text_exception=text_exception)
            # TODO: message to email
            return {"resp_message": message_resp_json,
                    "http_code": message["http_code"]}

    
    def send_broadcast_sync_mass_messages_and_get_report_by_message_id(self, request_params:dict) -> dict:
        ''' another popular request method for sending mass messages
         using by braodcast and get report for ever message by message_id '''
        try:
            message = self.send_message(by="mass_broadcast_sync", request_params=request_params)
            message_resp_json = message["response_json"]
            message_id_list = []
            for message in message_resp_json["messages"]:
                message_id_list.append(message["message_id"])
            report_list = []
            for message_id in message_id_list:
                report = self.get_report(by="message_id_advanced", message_id=message_id)
                report_list.append(report["response_json"])
            return {"resp_message": message_resp_json,
                    "http_code": message["http_code"],
                    "resp_report": report_list}
        except Exception as text_exception:
            notice_exception(text_exception=text_exception)
            return {"resp_message": message_resp_json,
                    "http_code": message["http_code"]}


    def send_one_message_and_get_report_by_message_id(self, request_params:dict) -> dict:
        ''' another popular method for sending one message and get report by message_id'''
        try:
            message = self.send_message(by="one_message", request_params=request_params)
            message_resp_json = message["response_json"]
            message_id = message_resp_json["message_id"].strip()
            report = self.get_report(by="message_id_advanced", message_id=message_id)
            return {"resp_message": message_resp_json,
                    "http_code": message["http_code"],
                    "resp_report": report["response_json"]}
        except Exception as text_exception:
            notice_exception(text_exception=text_exception)
            return {"resp_message": message_resp_json,
                    "http_code": message["http_code"]}
            # TODO: try message with viber with image and links, why vuber is not allowed?
            # TODO: save to data http-code


if __name__ == "__main__":
    p = ApiMTS().get_url(by="SM_MASS_BROADCAST_SYNC")
    print(p)
