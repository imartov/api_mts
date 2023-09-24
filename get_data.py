import json, os

from dotenv import load_dotenv
from openpyxl import load_workbook

from createrp import RequestParamsMassBroadcast, RequestParamsOneMessage
from phone import PhoneOperations
from utils import create_extra_id


class GetData:
    def __init__(self, mass_broadcast=False, one_message=False) -> None:
        if mass_broadcast:
            self.rp = RequestParamsMassBroadcast()
            del self.rp.request_params["recipients"][0]
        elif one_message:
            self.rp = RequestParamsOneMessage()
    

    def get_request_params_mass_broadcast(self, sync=False) -> dict:
        ''' this method connetcs to database and get data for mass broadcast delivering '''
        with open("test_data\\broadcast\\request_params.json", "r", encoding="utf-8") as file:
            request_params = json.load(file)

        # get text message
        with open("test_data\\broadcast\\text_message.txt", "r", encoding="utf-8") as file:
            text_message = file.read()

        # get environment variables and generate extra_id and set to recipients list
        load_dotenv()
        extra_id_list = []
        for recipient in request_params["recipients"]:
            extra_id = create_extra_id()
            extra_id_list.append(extra_id)
            recipient["extra_id"] = extra_id

        # set text message and alfa name
        request_params["channel_options"]["sms"]["text"] = text_message
        request_params["channel_options"]["sms"]["alpha_name"] = os.getenv("ALPHA_NAME")
        return request_params


    def get_request_params_one_message(self, path_to_request_params:str, text:str, phone_number:int) -> dict:
        ''' this method if for getting data for send message about success messages-delivering '''
        with open(path_to_request_params, "r", encoding="utf-8") as file:
            request_params = json.load(file)

        # get environment variables and generate extra_id and set data for request params
        load_dotenv()
        request_params["phone_number"] = phone_number
        request_params["channel_options"]["sms"]["text"] = text
        request_params["extra_id"] = create_extra_id()
        request_params["channel_options"]["sms"]["alpha_name"] = os.getenv("ALPHA_NAME")
        return request_params
    

    def get_test_request_params_for_exe(self):
        ''' this method is test method for exe '''
        load_dotenv()
        with open(os.getenv("PATH_EXAM_MASS_BRO_REQ_PAR"), "r", encoding="utf-8") as file:
            request_params = json.load(file)

        # get text message
        with open(os.getenv("PATH_EXAM_MASS_BRO_TEXT_MESS"), "r", encoding="utf-8") as file:
            text_message = file.read()

        # get environment variables and generate extra_id and set to recipients list
        extra_id_list = []
        for recipient in request_params["recipients"]:
            extra_id = create_extra_id()
            extra_id_list.append(extra_id)
            recipient["extra_id"] = extra_id

        # set text message and alfa name
        request_params["channel_options"]["sms"]["text"] = text_message
        request_params["channel_options"]["sms"]["alpha_name"] = os.getenv("ALPHA_NAME")
        return request_params
    

    def parse_xl(self) -> dict:
        ''' open excel file and parse it '''
        wb = load_workbook(filename=os.getenv("PATH_FILE_NAME_XL"))
        ws = wb.active
        
        phone_operations = PhoneOperations()
        for row in ws.iter_rows(min_row=3):
            unp = row[0]
            company_name = row[1]
            debt_sum = row[4]
            phone_number = row[10]

            # payment_date = row[12]
            # valid_payment_date = datetime.strptime(payment_date.value, "%d.%m.%Y")

            if debt_sum.value and int(debt_sum.value) >= 1 and not phone_number.value:
                phone_operations.save_uncorrect_phone_number(unp=unp.value, company_name=company_name.value, phone_number=phone_number.value)

            elif debt_sum.value and int(debt_sum.value) >= 1 and phone_number.value:
                valid_phone_number = phone_operations.make_valid_phone_number(unp=unp.value, company_name=company_name.value, phone_number=phone_number.value)
                if not valid_phone_number:
                    phone_operations.save_uncorrect_phone_number(unp=unp.value, company_name=company_name.value, phone_number=phone_number.value)
                else:
                    self.rp.create(phone_number=valid_phone_number, company_name=company_name.value, debt_sum=debt_sum.value)

        return self.rp.request_params
    

if __name__ == "__main__":
    load_dotenv()
    p = GetData(mass_broadcast=True).parse_xl()