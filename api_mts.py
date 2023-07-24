import os, json
import requests
from dotenv import load_dotenv


class ApiMTS:
    ''' Class for sending messages and getting reports '''

    def __init__(self) -> None:
        self.job_id = None
        self.message_id = None
        self.extra_id = None

        # get environment variables
        load_dotenv()
        self.CLIENT_ID = os.getenv("CLIENT_ID")
        self.LOGIN = os.getenv("LOGIN")
        self.PASSWORD = os.getenv("PASSWORD")

        # api urls for send messages
        self.urls_send_messages = {
            "mass_broadcast_sync": f"https://api.communicator.mts.by/{self.CLIENT_ID}/json2/broadcast/sync",
            "mass_broadcast": f"https://api.communicator.mts.by/{self.CLIENT_ID}/json2/broadcast",
            "mass_batch_sync": f"https://api.communicator.mts.by/{self.CLIENT_ID}/json2/batch/sync",
            "mass_batch": f"https://api.communicator.mts.by/{self.CLIENT_ID}/json2/batch",
            "one_message": f"https://api.communicator.mts.by/{self.CLIENT_ID}/json2/simple"
        }
        
        # api urls for get reports
        self.urls_get_reports = {
            "by_job_id": f"https://api.communicator.mts.by/{self.CLIENT_ID}/json2/job/status/{self.job_id}",
            "by_message_id_advanced": f"https://api.communicator.mts.by/{self.CLIENT_ID}/dr/{self.message_id}/advanced",
            "by_message_id_simple": f"https://api.communicator.mts.by/{self.CLIENT_ID}/dr/{self.message_id}/simple",
            "by_extra_id_advanced": f"https://api.communicator.mts.by/{self.CLIENT_ID}/dr/external/{self.extra_id}/advanced",
            "by_extra_id_simple": f"https://api.communicator.mts.by/{self.CLIENT_ID}/dr/external/{self.extra_id}/simple"
        }


    def send_message(self, url:str, request_params:dict) -> dict:
        ''' function for send messages as one as mass '''
        response = requests.post(url=url, json=request_params, auth=(self.LOGIN, self.PASSWORD))
        return {"http_code": int(response.status_code), "resp_json": response.json()}
    

    def get_report(self, url:str, ) -> dict:
        ''' function for get reports '''
        response = requests.get(url=url, auth=(self.LOGIN, self.PASSWORD))





    def send_messages_broadcast_sync(self, request_params:dict) -> dict:
        ''' this method is for mass-sending and returns detail response '''
        url = f"https://api.communicator.mts.by/{self.CLIENT_ID}/json2/broadcast/sync"

        # sending sms-messages
        resp = requests.post(url=url, json=request_params, auth=(self.LOGIN, self.PASSWORD))
        return {"http_code": int(resp.status_code), "resp_json": resp.json()}


    def send_messages_broadcast(self, request_params:dict) -> dict:
        ''' this method is for mass-sending and returns short response - job_id '''
        url = f"https://api.communicator.mts.by/{self.CLIENT_ID}/json2/broadcast"

        # sending sms-messages
        resp = requests.post(url=url, json=request_params, auth=(self.LOGIN, self.PASSWORD))
        return {"http_code": int(resp.status_code), "resp_json": resp.json()}


    def get_report_by_message_id(self, path_to_file:str) -> None:
        ''' get detail report by message_id'''
        with open(path_to_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        reports_list = []
        for message_delivery in data:
            for message in message_delivery["messages"]:
                message_id = message["message_id"]

                url = f"https://api.communicator.mts.by/{self.CLIENT_ID}/dr/{message_id}/advanced"
                resp = requests.get(url=url, auth=(self.LOGIN, self.PASSWORD))
                reports_list.append(resp.json())
                print("\nReport request: ")
                print("1. HTTP code of report request: ", resp.status_code)
                print("2. Return data: ", resp.json())
        return reports_list


    # def get_report_by_message_id(self, message_id:str) -> None:
    #     ''' get detail report '''
    #     url = f"https://api.communicator.mts.by/{self.CLIENT_ID}/dr/{message_id}/advanced"
    #     resp = requests.get(url=url, auth=(self.LOGIN, self.PASSWORD))
    #     print("\nReport request: ")
    #     print("1. HTTP code of report request: ", resp.status_code)
    #     print("2. Return data: ", resp.json())
    #     print(resp)


if __name__ == "__main__":
    p = ApiMTS()
    p.get_report_by_message_id(path_to_file="sent_messages\\response_data\\23_07_2023.json")
