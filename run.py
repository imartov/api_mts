import os

from dotenv import load_dotenv
from loguru import logger

from api_mts import ApiMTS
from get_data import GetData
from file_operations import FileOperations
from checking import CheckReportJobId
from createrp import OneMessage


# add logger
# logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='100 KB', compression='zip')


class Run:
    def __init__(self) -> None:
        load_dotenv()

    @logger.catch()
    def run_mass_broadcast(self, sync=False) -> None:
        ''' this method defines queues of methods
        for running mass broadcast delivering '''

        def get_save_req_par_and_send_mes(cl_rq, send_mes=False):
            request_params = cl_rq
            request_params_copy = dict(request_params)
            file_operations.save_data(data=request_params_copy,
                                      path_to_folder=os.getenv("SAVE_VIRGIN_REQ_PAR_ONE_MESS"))
            if send_mes:
                message.send_one_message_and_get_report_by_message_id(request_params=request_params)
            else:
                return request_params

        message = ApiMTS()
        file_operations = FileOperations()
        # try:
        request_params = GetData(mass_broadcast=True).parse_xl()
        if sync:
            send_messages = message.send_broadcast_sync_mass_messages_and_get_report_by_message_id(request_params=request_params)
        else:
            send_messages = message.send_broadcast_mass_messages_and_get_report_by_job_id(request_params=request_params)
        response_data = send_messages["resp_message"]
        reports = send_messages["resp_report"]
        file_operations.save_data_using_popular_api_methods(response_data=response_data)
        file_operations.save_data(path_to_folder=os.getenv("SAVE_REPORTS_JOB_ID"))
        
        cr = CheckReportJobId()
        fail_messages = cr.job_id_fail()[0]
        if fail_messages:
            get_save_req_par_and_send_mes(cl_rq=OneMessage().create(), send_mes=True)
        else:
            text = "Message delivering was succesfully"
            get_save_req_par_and_send_mes(cl_rq=OneMessage(text_message=text).create(), send_mes=True)
        # except:
        #     get_save_req_par_and_send_mes(cl_rq=OneMessage().create(), send_mes=True)


if __name__ == "__main__":
    p = Run()
    p.run_mass_broadcast()
