import os, json, time
import requests
from dotenv import load_dotenv
from loguru import logger
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


    @logger.catch()
    def send_message(self, by:str, request_params:dict) -> dict:
        ''' this method is for send messages as one as mass '''
        url = self.get_url(by=by)
        response = requests.post(url=url, json=request_params, auth=(self.LOGIN, self.PASSWORD))
        response_json = response.json()
        response_json["status_code"] = int(response.status_code)
        return {"http_code": int(response.status_code), "response_json": response_json}
    

    @logger.catch()
    def get_report(self, by:str, var:str) -> dict:
        ''' method for get reports
         you should define "by" and "job_id" or "exrta_id" or "message_id" parametrs '''
        url = self.get_url(by=by, var=var)
        right_resp = False
        seconds = 0
        limit_seconds = 180
        print("Ожидание ответа от сервера для получения отчета...")
        while not right_resp:
            if seconds >= limit_seconds:
                text_exception = f"Количество секунд ожидания ответа для получения отчета превысило {limit_seconds} секунд."
                print(text_exception)
                break
            else:      
                response = requests.get(url=url, auth=(self.LOGIN, self.PASSWORD))
                if int(response.status_code) == 200:
                    right_resp = True
                else:
                    seconds += 2
                    time.sleep(2)

        response_json = response.json()
        http_code = int(response.status_code)
        response_json["status_code"] = http_code
        return {"http_code": http_code, "response_json": response_json}
        

    def send_broadcast_mass_messages_and_get_report_by_job_id(self, request_params:dict):
        ''' the popular request method for sennding mass messages using
         by broadcast and getting report by job_id for full company '''
        _message = self.send_message(by="SM_MASS_BROADCAST", request_params=request_params)
        print(_message["http_code"], _message["response_json"])

        message_resp_json = _message["response_json"]
        job_id = message_resp_json["job_id"].strip()
        _report = self.get_report(by="GR_JOB_ID", job_id=job_id)
        return {"resp_message": message_resp_json,
                "sm_http_code": _message["http_code"],
                "resp_report": _report["response_json"],
                "gr_http_code": _report["http_code"]}

    
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
            _report = self.get_report(by="GR_MESSAGE_ID_ADVANCED", message_id=message_id)
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
        _report = self.get_report(by="GR_MESSAGE_ID_ADVANCED", message_id=message_id)
        return {"resp_message": message_resp_json,
                "sm_http_code": _message["http_code"],
                "resp_report": _report["response_json"],
                "gr_http_code": _report["http_code"]}
        

    def notice_exception(self, text_exception:str) -> None:
        ''' this method sends to defined phone number notice 
        abut exceptions during running key methods '''
        load_dotenv()
        with open(os.getenv("NOTICE_EXCEPTION_TEXT_MESSAGE_SMS"), "r", encoding="utf-8") as file:
            text_message = file.read()
            text_message = text_message.format(text_exception=text_exception)
        
        with open(os.getenv("NOTICE_EXCEPTION_REQUEST_PARAMS_SMS"), "r", encoding="utf-8") as file:
            request_params = json.load(file)

            request_params["phone_number"] = int(os.getenv("INFO_PHONE_NUMBER"))
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
