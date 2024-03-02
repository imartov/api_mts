import os, json

from dotenv import load_dotenv
from loguru import logger

from api_mts import ApiMTS
from get_data import GetData
from file_operations import FileOperations, report_message_form
from checking import CheckReportJobId
from createrp import MassBroadcast
from utils import get_request_params_minus_messages, CreateUpdateInvalidXlsFile
from analysis import Analysis
from repit_fail import RepitCheckFailMessagesAndSaveIfSuccess
from report import Report


# TODO: structure of daily success messages = structure of all success messages
# TODO: один раз в 15 дней повторно направлять смс по номерам, завершившимся с ошибкой, если есть долг
# TODO: send mail about sms delivering
# TODO: create excel file with debtors was send message every day
# TODO: check time if prod real data
# TODO: create test func for get_data
# TODO: delete from uncorrect correct phones

report_message = {
    "debtor_count_will_send_message": 0,
    "debt_sum_will_send_message": 0,
    "all_success_messages": 0,
    "all_unsuccess_messages": 0,
    "percent_success_messages": 0
}

logger.add("debug.log", format='{time} | {level} | {file} | {name} | {function} | {line} | {message}', level='DEBUG', rotation='1 week', compression='zip')
am = ApiMTS()
fo = FileOperations()

@logger.catch
def runtest() -> None:
    logger.info("Start 'runtest.runtest' method")
    # repitcheckfail = RepitCheckFailMessagesAndSaveIfSuccess().run()
    if fo.check_modified_date(path=os.getenv("EXCEL_FILE")):
    # if fo.check_modified_date(path=os.getenv("EXCEL_FILE_PROD")):
        load_dotenv()
        mb = MassBroadcast()
        gt = GetData(mass_broadcast=True)
        cr = CheckReportJobId()
        rep = Report()

        request_params = gt.parse_xl()
        request_params, double_request_params = mb.get_first_and_double_request_params(request_params=request_params, minus=True)
        # processing and send double request_params
        if double_request_params:
            double_request_params = get_request_params_minus_messages(path_file=os.getenv("SAVE_FILE_SUCCESS_MESSAGES_DOUBLE"),
                                                                    request_params=double_request_params)
            fo.save_data(data=double_request_params, path_to_folder=os.getenv("SAVE_DOUBLE_REQ_PAR_MASS_BROAD"))
            report_message["debtor_count_will_send_message"] += len(double_request_params["recipients"])
            report_message["debt_sum_will_send_message"] += round(Analysis().counting_sum_from_recipients(recipients=double_request_params["recipients"]), 2)
            send_message = am.send_broadcast_mass_messages_and_get_report_by_job_id(request_params=double_request_params, double=True)
            if send_message:
                fo.save_data(data=send_message["resp_message"], path_to_folder=os.getenv("SAVE_RESPONSE_DATA"))
                fo.save_data(data=send_message["resp_report"], path_to_folder=os.getenv("SAVE_DOUBLE_REPORTS_JOB_ID"))
                count_seccess, count_fail = cr.create_update_success_fail_messages(request_params=double_request_params,
                                                                                   report=send_message["resp_report"],
                                                                                   double=True)
                report_message["all_success_messages"] += count_seccess
                report_message["all_unsuccess_messages"] += count_fail
        
        request_params = get_request_params_minus_messages(path_file=os.getenv("SAVE_FILE_SUCCESS_MESSAGES_DOUBLE"),
                                                           request_params=request_params, double=True)
        request_params = get_request_params_minus_messages(path_file=os.getenv("SAVE_FILE_SUCCESS_MESSAGES_FIRST"),
                                                           request_params=request_params, double=True)
        
        fo.save_data(data=request_params, path_to_folder=os.getenv("SAVE_FIRST_REQ_PAR_MASS_BROAD"))
        report_message["debtor_count_will_send_message"] += len(request_params["recipients"])
        report_message["debt_sum_will_send_message"] += round(Analysis().counting_sum_from_recipients(recipients=request_params["recipients"]), 2)
        send_message = am.send_broadcast_mass_messages_and_get_report_by_job_id(request_params=request_params)
        if send_message:
            fo.save_data(data=send_message["resp_message"], path_to_folder=os.getenv("SAVE_RESPONSE_DATA"))
            fo.save_data(data=send_message["resp_report"], path_to_folder=os.getenv("SAVE_FIRST_REPORTS_JOB_ID"))
            count_seccess, count_fail = cr.create_update_success_fail_messages(request_params=request_params, report=send_message["resp_report"])
            report_message["all_success_messages"] += count_seccess
            report_message["all_unsuccess_messages"] += count_fail
        cr.remove_success_messages()
        cr.remove_success_messages(double=True)
        if report_message["debtor_count_will_send_message"]:
            report_message["percent_success_messages"] = round(report_message["all_success_messages"] / report_message["debtor_count_will_send_message"] * 100, 2)
        report_message_form(labels=report_message)
        fo.delete_file()
        invphones = CreateUpdateInvalidXlsFile()
        invphones.create_update_invalid_phones()
        invphones.create_update_error_phones()
        rep.run()
        logger.info("End 'runtest.runtest' method")
    else:
        am.notice_report(fail=True)


def main() -> None:
    runtest()

if __name__ == "__main__":
    main()