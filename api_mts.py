import os, json, time
import requests
from dotenv import load_dotenv
from loguru import logger
from utils import create_extra_id
from file_operations import FileOperations


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


    def get_url(self, by:str, **kwargs) -> str:
        ''' this method is for get url
         if you get url for send message just define "by" parametr,
         if you get url for get_report define "by" and
         "job_id" or "exrta_id" or "message_id" parametrs '''
        load_dotenv()
        if locals()["kwargs"]:
            value = list(locals()["kwargs"].values())[0]
            return os.getenv(by.upper()).format(client_id=self.CLIENT_ID, key=value)
        else:
            return os.getenv(by.upper()).format(client_id=self.CLIENT_ID)


    @logger.catch()
    def send_message(self, by:str, request_params:dict) -> dict:
        ''' this method is for send messages as one as mass '''
        url = self.get_url(send_message=True, by=by)
        response = requests.post(url=url, json=request_params, auth=(self.LOGIN, self.PASSWORD))
        try:
            response.json()["status_code"] = int(response.status_code)
            return {"http_code": int(response.status_code), "response_json": response.json()}
        except Exception as text_exception:
            self.notice_exception(text_exception=text_exception)
            # TODO: email
            return {"http_code": int(response.status_code)}
    

    @logger.catch()
    def get_report(self, by:str, job_id=None, message_id=None, extra_id=None) -> dict:
        ''' method for get reports '''
        url = self.get_url(get_report=True, by=by, job_id=job_id, message_id=message_id, extra_id=extra_id)
        right_resp = False
        seconds = 0
        limit_seconds = 180
        while not right_resp:
            if seconds >= limit_seconds:
                text_exception = f"Количество секунд ожидания ответа для получения отчета превысило {limit_seconds}"
                self.notice_exception(text_exception=text_exception)
                # TODO: email
                break
            else:      
                response = requests.get(url=url, auth=(self.LOGIN, self.PASSWORD))
                if int(response.status_code) == 200:
                    right_resp = True
                else:
                    seconds += 2
                    time.sleep(2)
        try:
            response.json()["status_code"] = int(response.status_code)
            return {"http_code": int(response.status_code), "response_json": response.json()}
        except Exception as text_exception:
            self.notice_exception(text_exception=text_exception)
    

    def send_broadcast_mass_messages_and_get_report_by_job_id(self, request_params:dict) -> dict:
        ''' the popular request method for sennding mass messages using
         by broadcast and getting report by job_id for full company '''
        message = self.send_message(by="mass_broadcast", request_params=request_params)
        try:
            message_resp_json = message["response_json"]
            job_id = message_resp_json["job_id"].strip()
            report = self.get_report(by="job_id", job_id=job_id)
            return {"resp_message": message_resp_json,
                    "http_code": message["http_code"],
                    "resp_report": report["response_json"]}
        except Exception as text_exception:
            self.notice_exception(text_exception=text_exception)
            # TODO: message to email
            return {"resp_message": message_resp_json,
                    "http_code": message["http_code"]}

    
    def send_broadcast_sync_mass_messages_and_get_report_by_message_id(self, request_params:dict) -> dict:
        ''' another popular request method for sending mass messages
         using by braodcast and get report for ever message by message_id '''
        message = self.send_message(by="mass_broadcast_sync", request_params=request_params)
        try:
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
            self.notice_exception(text_exception=text_exception)
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
            self.notice_exception(text_exception=text_exception)
            return {"resp_message": message_resp_json,
                    "http_code": message["http_code"]}
        

    def notice_exception(self, text_exception:str) -> None:
        ''' this method sends to defined phone number notice 
        abut exceptions during running key methods '''
        load_dotenv()
        with open(os.getenv("NOTICE_EXCEPTION_TEXT_MESSAGE_SMS"), "r", encoding="utf-8") as file:
            text_message = file.read()
            text_message = text_message.format(text_exception=text_exception)
        
        with open(os.getenv("NOTICE_EXCEPTION_REQUEST_PARAMS_SMS"), "r", encoding="utf-8") as file:
            request_params = json.load(file)

            request_params["phone_number"] = int(os.getenv("NOTICE_EXCEPTION_PHONE_NUMBER"))
            request_params["extra_id"] = create_extra_id()
            alpha_name = os.getenv("ALPHA_NAME")
            request_params["channel_options"]["sms"]["text"] = text_message
            request_params["channel_options"]["sms"]["alpha_name"] = alpha_name

        message = self.send_one_message_and_get_report_by_message_id(request_params=request_params)

        file_operations = FileOperations()
        file_operations.save_data_using_popular_api_methods(resp_message=message["resp_message"],
                                                            resp_report=message["resp_report"],
                                                            request_params=request_params)


if __name__ == "__main__":
    pass
