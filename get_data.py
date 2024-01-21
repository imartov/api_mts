import json, os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from openpyxl import load_workbook
from loguru import logger

from createrp import MassBroadcast, OneMessage
from phone import PhoneOperations
from file_operations import FileOperations, report_message_form
from utils import *
from checking import CheckReportJobId
from analysis import Analysis


# logger.add("debug.log", format='{time} | {level} | {file} | {name} | {function} | {line} | {message}', level='DEBUG', rotation='1 week', compression='zip')

report_message = {
    "all_count_clients": 0,
    "full_debt_sum": 0,
    "debtor_count_after_filter": 0,
    "debtor_count_valid_number": 0,
    "debtor_count_unvalid_number": 0,
    "debt_sum_valid_number": 0,
    "debt_sum_unvalid_number": 0
}

fo = FileOperations()
load_dotenv()

class GetData:
    def __init__(self, mass_broadcast=True, one_message=False) -> None:
        if mass_broadcast:
            self.rp = MassBroadcast()
            del self.rp.request_params["recipients"][0]
        elif one_message:
            self.rp = OneMessage()

    def parse_xl(self) -> dict:
        ''' open excel file and parse it '''
        logger.info("Start 'get_data.FileOperations.parse_xl' method")
        # wb = load_workbook(filename=os.getenv("EXCEL_FILE"))
        wb = load_workbook(filename=os.getenv("EXCEL_FILE_PROD"))
        ws = wb.active
        checking = CheckReportJobId()
        analysis = Analysis()
        removestoplist = RemoveStopList()
        cfilter = Filter()

        phone_operations = PhoneOperations()
        for row in ws.iter_rows(min_row=3):
            unp = row[11]
            company_name = row[1]
            debt_sum = row[4]
            phone_number = row[10]
            payment_date = row[12]

            # end of dataframe
            if not unp.value and not company_name.value and not payment_date.value:
                break

            report_message["all_count_clients"] += 1
            
            # check if unp exist
            if not unp.value:
                continue
            
            # check if debt sum exists
            if not debt_sum.value:
                # remove from success messages if company doesn't have debt_sum
                remove_message_from_success(unp=str(unp.value))
                remove_message_from_success(unp=str(unp.value), double=True) 
                continue

            report_message["full_debt_sum"] += int(debt_sum.value)
            
            # check if payment day is earlier than define in Filter.start_date var
            if not cfilter.date_filter(date=payment_date.value):
                continue

            # check if debt sum is less than define in Filter.min_sum var
            if not cfilter.sum_filter(sum=debt_sum.value):
                continue
            
            # checking whether the debt arose in a certain period
            if not check_debt_period(payment_date=payment_date.value):
                continue

            # check if unp in stop-list
            if removestoplist.check_if_in_list(unp=unp.value):
                continue
            
            report_message["debtor_count_after_filter"] += 1

            # check valid phone number
            valid_phone_number = phone_operations.check_phone_number(
            unp=str(unp.value), company_data={
                "company_name": company_name.value,
                "payment_date": payment_date.value,
                "phone_number": phone_number.value
                }
            )
            if valid_phone_number:
                report_message["debtor_count_valid_number"] += 1
                report_message["debt_sum_valid_number"] += int(debt_sum.value)
                exist_first = checking.check_exist_success_message(
                    unp=int(unp.value),
                    payment_date=payment_date.value
                )
                exist_double = checking.check_exist_success_message(
                    unp=int(unp.value),
                    payment_date=payment_date.value, double=True
                )
                # pass debtors to virgin request params
                if not exist_first and not exist_double:
                    self.rp.create(
                        phone_number=valid_phone_number,
                        company_name=company_name.value,
                        debt_sum=debt_sum.value,
                        unp=int(unp.value),
                        payment_date=payment_date.value
                    )
            else:
                report_message["debtor_count_unvalid_number"] += 1
                report_message["debt_sum_unvalid_number"] += int(debt_sum.value)
                    
        copy_request_params = dict(self.rp.request_params)
        fo.save_data(data=copy_request_params,
                    path_to_folder=os.getenv("VIRGIN_REQ_PAR_MASS_BROAD"))
        with open("test_file.json", "w", encoding="utf-8") as file:
            json.dump(self.rp.request_params, file, indent=4, ensure_ascii=False)
        report_message_form(labels=report_message)
        logger.info("End 'get_data.FileOperations.parse_xl' method")
        return self.rp.request_params


class RemoveStopList:
    def __init__(self) -> None:
        self.unp_list = self.get_unp_list()
        self.phone_list = self.get_phone_list()

    def get_unp_list(self) -> list:
        wb = load_workbook(filename=os.getenv("STOP_CLIENTS_LIST"))
        ws = wb.active
        unp_list = []
        for row in ws.iter_rows(min_col=2, max_col=6, min_row=4):
            unp_list.append(int(row[0].value))
        return unp_list
    
    def get_phone_list(self) -> list:
        wb = load_workbook(filename=os.getenv("STOP_PHONE_LIST"))
        ws = wb.active
        phone_list = []
        for row in ws.iter_rows(min_col=2, max_col=6, min_row=4):
            phone_list.append(int(row[1].value))
        return phone_list

    def check_if_in_list(self, unp) -> bool:
        if int(unp) in self.unp_list or int(unp) in self.phone_list:
            return True
        return False
    

class Filter:
    def __init__(self) -> None:
        self.min_sum = 50
        self.start_date = datetime(2021, 1, 1).date()

    def sum_filter(self, sum) -> bool:
        if int(sum) >= self.min_sum:
            return True
        return False
    
    def date_filter(self, date:str) -> bool:
        if datetime.strptime(date, "%d.%m.%Y").date() >= self.start_date:
            return True
        return False
    

def check_debt_period(payment_date, count_days=2):
    payment_date = datetime.strptime(str(payment_date), "%d.%m.%Y").date()
    if payment_date + timedelta(days=count_days) <= datetime.now().date():
        return True
    return False


def main() -> None:
    rq = GetData().parse_xl()
    print(rq)

if __name__ == "__main__":
    main()