import json, os
from datetime import datetime

from loguru import logger

from file_operations import FileOperations
from api_mts import ApiMTS
from checking import CheckReportJobId


fo = FileOperations()
am = ApiMTS()
ch = CheckReportJobId()

class RepitCheckFailMessagesAndSaveIfSuccess:
    ''' класс имеет методы для повторного получения отчета о доставке сообещений,
     отправка которых завершилась с ошибкой '''
    def __init__(self) -> None:
        pass

    def get_extra_ids_from_fail_messages(self) -> list:
        ''' метод формирует и возвращает список из extra_id сообщений,
        завершившихся с ошибкой '''
        logger.info("Start")
        files_list = fo.get_files_list_in_folder(env="FOLDER_FAIL_MESSAGES")
        exeption_files = [os.getenv("FOLDER_FAIL_MESSAGES") + "\\" + "fail_mesages.json"]
        extra_ids_list = []
        for file in files_list:
            if file not in exeption_files:
                with open(file, "r", encoding="utf-8") as file:
                    fail_messages = json.load(file)
                for message in fail_messages:
                    for unp_key, company_data in message.items():
                        if unp_key != "datetime":
                            extra_ids_list.append(message[unp_key]["extra_id"])
        logger.info("End")
        return extra_ids_list

    def get_reports_by_extra_ids_list(self, extra_ids_list:list) -> None:
        ''' метод запрашивает отчет о доставке по extra_id,
        находящихся в списке, передаваемого в качестве аргумента '''
        logger.info("Start")
        reports_list = []
        for extra_id in extra_ids_list:
            report = am.get_report(by="GR_EXTRA_ID_SIMPLE", var=extra_id)
            reports_list.append(report["response_json"])
        # TODO: save reports
        logger.info("End")
        return reports_list

    def get_success_from_reports_list(self, reports_list:list) -> list:
        ''' метод проверяет список из отчетов и возвращает список extra_id
        успешно доставленных сообщений '''
        logger.info("Start")
        success_extra_ids = []
        for report in reports_list:
            if ch.check_success_status(msg_report=report):
                success_extra_ids.append(report["extra_id"])
        # TODO: save success_repit_reports
        logger.info("End")
        return success_extra_ids

    def form_messages_by_extra_ids(self, extra_ids_list:list, double=False) -> dict:
        ''' метод принимает список из extra_id, находит совпадения в request_params
        и формирует и возвращает словарь из структуры, предсатвленной ниже '''
        logger.info("Start")
        temp_success_messages = {}
        path_request_params = "SAVE_DOUBLE_REQ_PAR_MASS_BROAD" if double else "SAVE_FIRST_REQ_PAR_MASS_BROAD"
        files_list = fo.get_files_list_in_folder(env=path_request_params)
        for file in files_list:
            with open(file, "r", encoding="utf-8") as file:
                request_params_list = json.load(file)
            for request_params in request_params_list:
                for recipient in request_params["recipients"]:
                    if recipient["extra_id"] in extra_ids_list:
                        temp_success_messages[recipient["unp"]] = {
                            "company_name": recipient["company_name"],
                            "payment_date": recipient["payment_date"],
                            "phone_number": recipient["phone_number"],
                            "extra_id": recipient["extra_id"],
                            "delivering_date": datetime.now().strftime(fo.strftime_datatime_format)
                        }
        # TODO: save
        logger.info("End")
        return temp_success_messages

    def update_success_messages(self, messages, double=False) -> None:
        ''' метод принимает словарь из сообщений в структуре для success_messages
        и обновляет файлы success_messages '''
        logger.info("Start")
        path_success = "SAVE_FILE_SUCCESS_MESSAGES_DOUBLE" if double else "SAVE_FILE_SUCCESS_MESSAGES_FIRST"
        with open(os.getenv(path_success), "r", encoding="utf-8") as file:
            success_messages = json.load(file)
        success_messages.update(messages)
        with open(os.getenv(path_success), "w", encoding="utf-8") as file:
            json.dump(success_messages, file, indent=4, ensure_ascii=False)
        logger.info("End")

    def run(self) -> None:
        ''' метод упорядочивает выполнение методов класса для повторгого получения
         отчетов о доставке сообщений, отправка которых завершилась с ошибкой и
         сохранения их в случае успшной доставки '''
        logger.info("Start")
        extra_ids_list = self.get_extra_ids_from_fail_messages()
        reports_list = self.get_reports_by_extra_ids_list(extra_ids_list=extra_ids_list)
        success_extra_ids = self.get_success_from_reports_list(reports_list=reports_list)
        if success_extra_ids:
            first_repit_success_messages = self.form_messages_by_extra_ids(extra_ids_list=success_extra_ids)
            self.update_success_messages(messages=first_repit_success_messages)
            double_repit_success_messages = self.form_messages_by_extra_ids(extra_ids_list=success_extra_ids, double=True)
            self.update_success_messages(messages=double_repit_success_messages, double=True)
        logger.info("End")


def main() -> None:
    pass
    # repitcheckfail = RepitCheckFailMessagesAndSaveIfSuccess().run()

if __name__ == "__main__":
    main()