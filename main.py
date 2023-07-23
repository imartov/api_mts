import os, json
import requests
from dotenv import load_dotenv


class ApiMTS:
    ''' Class for sending messages and getting detail reports '''

    def __init__(self) -> None:

        # get environment variables
        load_dotenv()
        self.CLIENT_ID = os.getenv("CLIENT_ID")
        self.LOGIN = os.getenv("LOGIN")
        self.PASSWORD = os.getenv("PASSWORD")
        

    def send_messages(self, request_params:dict) -> dict:
        ''' run sms sending '''
        url = f"https://api.communicator.mts.by/{self.CLIENT_ID}/json2/broadcast/sync"

        # sending sms-messages
        resp = requests.post(url=url, json=request_params, auth=(self.LOGIN, self.PASSWORD))
        print("\nResponse: ")
        print("1. HTTP code of sms-sending: ", resp.status_code)
        print("2. Return data: ", resp.json())
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
