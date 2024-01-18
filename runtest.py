import os

from dotenv import load_dotenv
from loguru import logger

from api_mts import ApiMTS
from get_data import GetData
from file_operations import FileOperations
from checking import CheckReportJobId
from createrp import MassBroadcast
from utils import get_request_params_minus_messages


logger.add("debug.log", format='{time} | {level} | {file} | {name} | {function} | {line} | {message}', level='DEBUG', rotation='1 week', compression='zip')

@logger.catch
def runtest() -> None:
    logger.info("Start 'runtest.runtest' method")
    try:
        load_dotenv()
        fo = FileOperations()
        mb = MassBroadcast()
        gt = GetData(mass_broadcast=True)
        am = ApiMTS()
        cr = CheckReportJobId()
        
        request_params = gt.parse_xl()
        # request_params = get_request_params_minus_messages(path_file=os.getenv("PATH_UNCORRECT_PHONE_NUMBERS"),
        #                                                 request_params=request_params)
        request_params, double_request_params = mb.get_first_and_double_request_params(request_params=request_params, minus=True)
        

        # processing and send double request_params
        if double_request_params:
            double_request_params = get_request_params_minus_messages(path_file=os.getenv("SAVE_FILE_SUCCESS_MESSAGES_DOUBLE"),
                                                                      request_params=double_request_params)
            fo.save_data(data=double_request_params, path_to_folder=os.getenv("SAVE_DOUBLE_REQ_PAR_MASS_BROAD"))
            send_message = am.send_broadcast_mass_messages_and_get_report_by_job_id(request_params=double_request_params)
            if send_message:
                fo.save_data(data=send_message["resp_message"], path_to_folder=os.getenv("SAVE_RESPONSE_DATA"))
                fo.save_data(data=send_message["resp_report"], path_to_folder=os.getenv("SAVE_DOUBLE_REPORTS_JOB_ID"))
                cr.create_update_success_fail_messages(request_params=double_request_params,
                                                        report=send_message["resp_report"],
                                                        double=True)
        
        request_params = get_request_params_minus_messages(path_file=os.getenv("SAVE_FILE_SUCCESS_MESSAGES_DOUBLE"),
                                                        request_params=request_params, double=True)
        request_params = get_request_params_minus_messages(path_file=os.getenv("SAVE_FILE_SUCCESS_MESSAGES_FIRST"),
                                                        request_params=request_params, double=True)
        
        fo.save_data(data=request_params, path_to_folder=os.getenv("SAVE_FIRST_REQ_PAR_MASS_BROAD"))
        send_message = am.send_broadcast_mass_messages_and_get_report_by_job_id(request_params=request_params)
        if send_message:
            fo.save_data(data=send_message["resp_message"], path_to_folder=os.getenv("SAVE_RESPONSE_DATA"))
            fo.save_data(data=send_message["resp_report"], path_to_folder=os.getenv("SAVE_FIRST_REPORTS_JOB_ID"))
            cr.create_update_success_fail_messages(request_params=request_params, report=send_message["resp_report"])
        cr.remove_success_messages()
        cr.remove_success_messages(double=True)
        am.notice_report()
    except Exception as ex:
        am.notice_report(fail=True)
    finally:
        fo.delete_file()
        logger.info("End 'runtest.runtest' method")


def main() -> None:
    runtest()

if __name__ == "__main__":
    main()