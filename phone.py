import uuid, os, json, re
from dotenv import load_dotenv


class PhoneOperations:

    def __init__(self) -> None:
        pass

    def save_uncorrect_phone_number(self, unp:str, company_name:str, phone_number:str):
        load_dotenv()
        with open(os.getenv("PATH_UNCORRECT_PHONE_NUMBERS"), "r", encoding="utf-8") as file:
            uncorrect_phone_numbers = json.load(file)
            unp_list = []
            for company_data in uncorrect_phone_numbers:
                unp_list.append(company_data[0])
            if unp not in unp_list:
                uncorrect_phone_numbers.append((unp, company_name, phone_number))

            with open(os.getenv("PATH_UNCORRECT_PHONE_NUMBERS"), "w", encoding="utf-8") as file:
                json.dump(uncorrect_phone_numbers, file, indent=4, ensure_ascii=False)
    
    def make_valid_phone_number(self, unp:str, company_name:str, phone_number:str):
        ''' method gets any phone number and change
        it to valid phone number for API MTS '''
        operators_codes = ['25', '29', '33', '44']
        def get_int_phone_number(phone_number:str):
            int_phone_number = ''.join(x for x in phone_number if x.isdigit())
            if len(int_phone_number) == 12 and int_phone_number[:3] == '375' and int_phone_number[3:5] in operators_codes:
                return int(int_phone_number)
            elif len(int_phone_number) >= 9 and len(int_phone_number) < 12:
                int_phone_number = int_phone_number[-1:-10:-1][::-1]
                if int_phone_number[:2] in operators_codes:
                    int_phone_number = "375" + int_phone_number
                    return int(int_phone_number)
            else:
                self.save_uncorrect_phone_number(unp=unp, company_name=company_name, phone_number=company_name)
                
        if ',' in phone_number:
            list_phones = phone_number.split(',')
            for phone_of_list in list_phones:
                int_phone_number = get_int_phone_number(phone_number=phone_of_list)
                if int_phone_number:
                    return int(int_phone_number)
        else:
            int_phone_number = get_int_phone_number(phone_number=phone_number)
            if int_phone_number:
                return int(int_phone_number)