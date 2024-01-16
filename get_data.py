import json, os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from openpyxl import load_workbook

from createrp import MassBroadcast, OneMessage
from phone import PhoneOperations
from file_operations import FileOperations
from utils import *
from checking import CheckReportJobId
from analysis import Analysis


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
        wb = load_workbook(filename=os.getenv("EXCEL_FILE"))
        # wb = load_workbook(filename=os.getenv("EXCEL_FILE_PROD"))
        ws = wb.active
        checking = CheckReportJobId()
        analysis = Analysis()
        removestoplist = RemoveStopList()
        
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

            # check if unp exist
            if not unp.value:
                continue
            
            # check if debt sum exists
            if not debt_sum.value:
                # remove from success messages if company doesn't have debt_sum
                remove_message_from_success(unp=str(unp.value))
                remove_message_from_success(unp=str(unp.value), double=True) 
                continue

            # checking whether the debt arose in a certain period
            if not check_debt_period(payment_date=payment_date.value):
                continue

            # check if unp in stop-list
            if unp.value and removestoplist.check_if_in_list(unp=unp.value):
                continue

            # check valid phone number
            valid_phone_number = phone_operations.check_phone_number(
            unp=str(unp.value), company_data={
                "company_name": company_name.value,
                "payment_date": payment_date.value,
                "phone_number": phone_number.value
                }
            )

            if valid_phone_number:
                exist_first = checking.check_exist_success_message(
                    unp=int(unp.value),
                    payment_date=payment_date.value,
                    days=3
                )
                exist_double = checking.check_exist_success_message(
                    unp=int(unp.value),
                    payment_date=payment_date.value,
                    days=3, double=True
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
                       
        copy_request_params = dict(self.rp.request_params)
        fo.save_data(data=copy_request_params,
                     path_to_folder=os.getenv("VIRGIN_REQ_PAR_MASS_BROAD"))
        with open("test_file.json", "w", encoding="utf-8") as file:
            json.dump(self.rp.request_params, file, indent=4, ensure_ascii=False)
        return self.rp.request_params


class RemoveStopList:
    def __init__(self) -> None:
        wb = load_workbook(filename=os.getenv("STOP_LIST"))
        self.ws = wb.active
        self.unp_list = self.get_unp_list()

    def get_unp_list(self) -> list:
        unp_list = []
        for row in self.ws.iter_rows(min_col=2, max_col=6, min_row=4):
            unp_list.append(int(row[0].value))
        return unp_list

    def check_if_in_list(self, unp) -> bool:
        if int(unp) in self.unp_list:
            return True
        return False
    

def check_debt_period(payment_date, count_days=2):
    payment_date = datetime.strptime(str(payment_date), "%d.%m.%Y").date()
    if payment_date + timedelta(days=count_days) <= datetime.now().date():
        return True
    return False


def main() -> None:
    rq = GetData().parse_xl()

if __name__ == "__main__":
    main()