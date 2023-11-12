import os
from dotenv import load_dotenv
from file_operations import FileOperations


fo = FileOperations()
load_dotenv()

class PhoneOperations:

    def __init__(self) -> None:
        pass
    
    def make_valid_phone_number(self, phone_number:str):
        ''' method gets any phone number and change
        it to valid phone number for API MTS '''
        operators_codes = ('25', '29', '33', '44')
        separators = (",", ".", ";")
        def get_int_phone_number(phone_number:str):
            int_phone_number = ''.join(x for x in phone_number if x.isdigit())
            if len(int_phone_number) == 12 and int_phone_number[:3] == '375' and int_phone_number[3:5] in operators_codes:
                return int(int_phone_number)
            elif len(int_phone_number) >= 9 and len(int_phone_number) < 12:
                int_phone_number = int_phone_number[-1:-10:-1][::-1]
                if int_phone_number[:2] in operators_codes:
                    int_phone_number = "375" + int_phone_number
                    return int(int_phone_number)
                
        
        for separator in separators:
            if separator in phone_number:
                phone_number = phone_number.replace(separator, ",")

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
            
    def update_uncorrect_phone_numbers(self, unp:str, company_data:dict) -> None:
        uncorrect_phone_numbers = fo.get_data_from_json_file(path_file=os.getenv("PATH_UNCORRECT_PHONE_NUMBERS"))
        if unp not in uncorrect_phone_numbers:
            uncorrect_phone_numbers[unp] = company_data
        fo.save_file(data_list=uncorrect_phone_numbers, full_file_name=os.getenv("PATH_UNCORRECT_PHONE_NUMBERS"))

    def check_phone_number(self, unp:str, company_data:dict) -> None:
        if not company_data["phone_number"]:
            self.update_uncorrect_phone_numbers(unp=unp, company_data=company_data)
        else:
            valid_phone_number = self.make_valid_phone_number(phone_number=str(company_data["phone_number"]))
            if valid_phone_number:
                return valid_phone_number
            else:
                self.update_uncorrect_phone_numbers(unp=unp, company_data=company_data)
            


def main() -> None:
    p = PhoneOperations()
    phone = p.make_valid_phone_number(unp="123",
                                      company_name="Test company",
                                      phone_number="8-017-207-49-75, 8-029-191-19-20; +37529-648-82-44")
    print(phone)

if __name__ == "__main__":
    main()