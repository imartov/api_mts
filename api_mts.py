import os, json
import requests
from dotenv import load_dotenv
from loguru import logger


# add logger
logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='10 KB', compression='zip')

@logger.catch()
class ApiMTS:
    ''' Class for sending messages and getting reports '''
    
    def __init__(self) -> None:
        
        # get environment variables
        load_dotenv()
        self.CLIENT_ID = os.getenv("CLIENT_ID")
        self.LOGIN = os.getenv("LOGIN")
        self.PASSWORD = os.getenv("PASSWORD")


    def get_url(self, by:str, send_message=False, get_report=False, job_id=None, message_id=None, extra_id=None) -> str:
        ''' method for getting url '''
        urls_send_messages = {
            "mass_broadcast_sync": f"https://api.communicator.mts.by/{self.CLIENT_ID}/json2/broadcast/sync",
            "mass_broadcast": f"https://api.communicator.mts.by/{self.CLIENT_ID}/json2/broadcast",
            "mass_batch_sync": f"https://api.communicator.mts.by/{self.CLIENT_ID}/json2/batch/sync",
            "mass_batch": f"https://api.communicator.mts.by/{self.CLIENT_ID}/json2/batch",
            "one_message": f"https://api.communicator.mts.by/{self.CLIENT_ID}/json2/simple"
        }
        urls_get_reports = {
            "job_id": f"https://api.communicator.mts.by/{self.CLIENT_ID}/json2/job/status/{job_id}",
            "message_id_advanced": f"https://api.communicator.mts.by/{self.CLIENT_ID}/dr/{message_id}/advanced",
            "message_id_simple": f"https://api.communicator.mts.by/{self.CLIENT_ID}/dr/{message_id}/simple",
            "extra_id_advanced": f"https://api.communicator.mts.by/{self.CLIENT_ID}/dr/external/{extra_id}/advanced",
            "extra_id_simple": f"https://api.communicator.mts.by/{self.CLIENT_ID}/dr/external/{extra_id}/simple"
        }
        if send_message:
            return urls_send_messages[by]
        elif get_report:
            return urls_get_reports[by]


    def send_message(self, by:str, request_params:dict) -> dict:
        ''' method for send messages as one as mass '''
        url = self.get_url(send_message=True, by=by)
        response = requests.post(url=url, json=request_params, auth=(self.LOGIN, self.PASSWORD))
        return {"http_code": int(response.status_code), "response_json": response.json()}
    

    def get_report(self, by:str, job_id=None, message_id=None, extra_id=None) -> dict:
        ''' method for get reports '''
        url = self.get_url(get_report=True, by=by, job_id=job_id, message_id=message_id, extra_id=extra_id)
        response = requests.get(url=url, auth=(self.LOGIN, self.PASSWORD))
        return {"http_code": int(response.status_code), "response_json": response.json()}
    

    def send_broadcast_mass_messages_and_get_report_by_job_id(self, request_params:dict) -> dict:
        ''' the popular request method'''
        message = self.send_message(by="mass_broadcast", request_params=request_params)
        if message["http_code"] == 200:
            message_resp_json = message["response_json"]
            job_id = message_resp_json["job_id"]
            report = self.get_report(by="job_id", job_id=job_id)
            return {"resp_message": message_resp_json, "resp_report": report["response_json"]}
        else:
            print("\nSomething is going wrong: ")
            print(f"http-code of sending message: {message['http_code']}")
            # TODO: return

    
    def send_broadcast_sync_mass_messages_and_get_report_by_message_id(self, request_params:dict) -> dict:
        ''' another popular request method '''
        message = self.send_message(by="mass_broadcast_sync", request_params=request_params)
        if message["http_code"] == 200:
            message_resp_json = message["response_json"]
            message_id_list = []
            for message in message_resp_json["messages"]:
                message_id_list.append(message["message_id"])
            report_list = []
            for message_id in message_id_list:
                report = self.get_report(by="message_id_advanced", message_id=message_id)
                report_list.append(report["response_json"])
            return {"resp_message": message_resp_json, "resp_report": report_list}
        else:
            print("\nSomething is going wrong: ")
            print(f"http-code of sending message: {message['http_code']}")
            # TODO: return


if __name__ == "__main__":
    p = ApiMTS()
    p.get_report(by="message_id_advanced", message_id=123456789)
