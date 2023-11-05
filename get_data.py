import json, os
from datetime import datetime

from dotenv import load_dotenv
from openpyxl import load_workbook

from createrp import MassBroadcast, OneMessage
from phone import PhoneOperations
from file_operations import FileOperations
from utils import *
from checking import CheckReportJobId


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
        wb = load_workbook(filename=os.getenv("PATH_FILE_NAME_XL"))
        ws = wb.active
        checking = CheckReportJobId()
        
        phone_operations = PhoneOperations()
        for row in ws.iter_rows(min_row=3):
            unp = row[11]
            company_name = row[1]
            debt_sum = row[4]
            phone_number = row[10]
            payment_date = row[12]
            if not unp.value and not company_name.value and not payment_date.value:
                break

            valid_payment_date = datetime.strptime(str(payment_date.value), "%d.%m.%Y")
            compare_date = bool(valid_payment_date <= datetime.now())
            company_data = {
                "company_name": company_name.value,
                "payment_date": payment_date.value,
                "phone_number": phone_number.value
            }

            # if (debt sum exists and if it is more than 1 BYN and if due date equal to today or less):
            if debt_sum.value and int(debt_sum.value) >= 1 and compare_date:
                valid_phone_number = phone_operations.check_phone_number(unp=str(unp.value),
                                                                         company_data=company_data)
                if valid_phone_number:
                    exist_first = checking.check_exist_success_message(unp=int(unp.value),
                                                                        payment_date=payment_date.value,
                                                                        days=3)
                    exist_double = checking.check_exist_success_message(unp=int(unp.value),
                                                                        payment_date=payment_date.value,
                                                                        days=3, double=True)
                    # pass debtors to virgin request params
                    if not exist_first and not exist_double:
                        self.rp.create(phone_number=valid_phone_number,
                                        company_name=company_name.value,
                                        debt_sum=debt_sum.value,
                                        unp=int(unp.value),
                                        payment_date=payment_date.value)
            else:
                # remove from success messages if company doesn't have debt_sum
                remove_message_from_success(unp=str(unp.value))
                remove_message_from_success(unp=str(unp.value), double=True)
                    
        copy_request_params = dict(self.rp.request_params)
        fo.save_data(data=copy_request_params,
                     path_to_folder=os.getenv("VIRGIN_REQ_PAR_MASS_BROAD"))
        return self.rp.request_params


def main() -> None:
    rq = GetData().parse_xl()

if __name__ == "__main__":
    main()