import os
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


    def get_report(self, extra_id_list:list) -> None:
        ''' get detail report '''
        for extra_id in extra_id_list:
            url = f"https://api.communicator.mts.by/{self.CLIENT_ID}/dr/external/{extra_id}/advanced"
            resp = requests.get(url=url, auth=(self.LOGIN, self.PASSWORD))
            print("\nReport request: ")
            print("1. HTTP code of report request: ", resp.status_code)
            print("2. Return data: ", resp.json())
            print(resp)


if __name__ == "__main__":
    p = ApiMTS()
    p.send_messages()
