import json, os
from datetime import datetime

from dotenv import load_dotenv
from openpyxl import load_workbook

from createrp import MassBroadcast, OneMessage
from phone import PhoneOperations
from file_operations import FileOperations


class GetData:
    def __init__(self, mass_broadcast=True, one_message=False) -> None:
        if mass_broadcast:
            self.rp = MassBroadcast()
            del self.rp.request_params["recipients"][0]
        elif one_message:
            self.rp = OneMessage()
        load_dotenv()

    def parse_xl(self) -> dict:
        ''' open excel file and parse it '''
        fo = FileOperations()
        wb = load_workbook(filename=os.getenv("PATH_FILE_NAME_XL"))
        ws = wb.active
        
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

            uncorrect_phone_numbers = {}
            if debt_sum.value and int(debt_sum.value) >= 1:
                if compare_date:
                    if not phone_number.value:
                        uncorrect_phone_numbers[str(unp.value)] = {
                            "company_name": company_name.value,
                            "payment_date": payment_date.value,
                            "phone_number": phone_number.value
                        }

                    else:
                        valid_phone_number = phone_operations.make_valid_phone_number(unp=unp.value,
                                                                                      company_name=company_name.value,
                                                                                      phone_number=str(phone_number.value))
                        if not valid_phone_number:
                            uncorrect_phone_numbers[unp.value] = {
                                "company_name": company_name.value,
                                "payment_date": payment_date.value,
                                "phone_number": phone_number.value
                            }
                        else:
                            self.rp.create(phone_number=valid_phone_number,
                                           company_name=company_name.value,
                                           debt_sum=debt_sum.value,
                                           unp=int(unp.value),
                                           payment_date=payment_date.value)
                    
        with open(os.getenv("PATH_UNCORRECT_PHONE_NUMBERS"), "w", encoding="utf-8") as file:
            json.dump(uncorrect_phone_numbers, file, indent=4, ensure_ascii=False)

        copy_request_params = dict(self.rp.request_params)
        fo.save_data(data=copy_request_params,
                     path_to_folder=os.getenv("VIRGIN_REQ_PAR_MASS_BROAD"))
        return self.rp.request_params
    
    def get_success_messages(self, double=False):
        file_success_messages = "SAVE_FILE_SUCCESS_MESSAGES_DOUBLE" if double else "SAVE_FILE_SUCCESS_MESSAGES_FIRST"
        with open(os.getenv(file_success_messages), "r", encoding="utf-8") as file:
            success_messages = json.load(file)
        return success_messages


def main() -> None:
    rq = GetData().parse_xl()
    print(rq)

if __name__ == "__main__":
    main()