import os
from dotenv import load_dotenv
from loguru import logger
from api_mts import ApiMTS
from get_data import GetData
from file_operations import FileOperations


# add logger
logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='100 KB', compression='zip')


class Run:
    def __init__(self) -> None:
        pass


    def get_data_send_message_and_save_data(self, path_to_request_params:str, text:str) -> None:
        ''' this method is recomented if you use
         run methods in run.py for automatic saving 
          request_params, response and reports '''
        load_dotenv()
        message = ApiMTS()
        file_operations = FileOperations()
        request_params = GetData().get_request_params_one_message(path_to_request_params=path_to_request_params,
                                                                  text=text,
                                                                  phone_number=int(os.getenv("INFO_PHONE_NUMBER")))
        send_message = message.send_one_message_and_get_report_by_message_id(request_params=request_params)
        file_operations.save_data_using_popular_api_methods(request_params = request_params,
                                                            response_data=send_message["resp_message"],
                                                            reports=send_message["resp_report"])


    @logger.catch()
    def run_mass_broadcast(self, sync=False) -> None:
        ''' this method defines queues of methods
        for running mass broadcast delivering '''
        try:
            request_params = GetData().get_request_params_mass_broadcast(sync=sync)
            message = ApiMTS()
            if sync:
                send_messages = message.send_broadcast_sync_mass_messages_and_get_report_by_message_id(request_params=request_params)
            else:
                send_messages = message.send_broadcast_mass_messages_and_get_report_by_job_id(request_params=request_params)
                print(send_messages)
            
            response_data = send_messages["resp_message"]
            reports = send_messages["resp_report"]
            file_operations = FileOperations()
            file_operations.save_data_using_popular_api_methods(request_params = request_params,
                                                                response_data=response_data,
                                                                reports=reports)
            
            load_dotenv()
            with open(os.getenv("SUCCES_ONE_MESSAGE_TEXT"), "r", encoding="utf-8") as file:
                text = file.read()
            self.get_data_send_message_and_save_data(path_to_request_params=os.getenv("PATH_REQUEST_PARAMS_SUCCESS"),
                                                     text=text)
        except Exception as text_exception:
            with open(os.getenv("NOTICE_EXCEPTION_TEXT_MESSAGE_SMS"), "r", encoding="utf-8") as file:
                text = file.read()
            text = text.format(text_exception=text_exception)
            self.get_data_send_message_and_save_data(path_to_request_params=os.getenv("PATH_REQUEST_PARAMS_EXCEPTION"),
                                                     text=text)


if __name__ == "__main__":
    p = Run()
    p.run_mass_broadcast()
    # TODO: test