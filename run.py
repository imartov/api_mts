import os

from dotenv import load_dotenv
from loguru import logger

from api_mts import ApiMTS
from get_data import GetData
from file_operations import FileOperations
from checking import CheckReport
from createrp import RequestParams


# add logger
logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='100 KB', compression='zip')


class Run:
    def __init__(self) -> None:
        pass

    @logger.catch()
    def run_mass_broadcast(self, sync=False) -> None:
        ''' this method defines queues of methods
        for running mass broadcast delivering '''
        message = ApiMTS()
        file_operations = FileOperations()
        try:
            request_params = GetData(mass_broadcast=True).parse_xl()
            file_operations.save_data_using_popular_api_methods(request_params=request_params)
            if sync:
                send_messages = message.send_broadcast_sync_mass_messages_and_get_report_by_message_id(request_params=request_params)
            else:
                send_messages = message.send_broadcast_mass_messages_and_get_report_by_job_id(request_params=request_params)
            response_data = send_messages["resp_message"]
            reports = send_messages["resp_report"]
            file_operations.save_data_using_popular_api_methods(response_data=response_data,
                                                                reports=reports)
            cr = CheckReport()
            fail_messages = cr.job_id()
            if fail_messages:
                request_params_fail = RequestParams.OneMessage().create()
                message.send_one_message_and_get_report_by_message_id(request_params=request_params_fail)
            else:
                request_params_fail = RequestParams.OneMessage(text_message="Message delivering was succesfully").create()
                message.send_one_message_and_get_report_by_message_id(request_params=request_params_fail)
        except:
            request_params_fail = RequestParams.OneMessage().create()
            message.send_one_message_and_get_report_by_message_id(request_params=request_params_fail)


if __name__ == "__main__":
    message = ApiMTS()
    request_params_fail = RequestParams.OneMessage().create()
    print(request_params_fail)
    message.send_one_message_and_get_report_by_message_id(request_params=request_params_fail)
