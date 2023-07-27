import uuid, os, json
from dotenv import load_dotenv


def create_extra_id() -> str:
    ''' generate random UUID fot extra_id '''
    return str(uuid.uuid4())


def make_valid_phone_number(phone_number:str):
    ''' method gets any phone number and change
    it to valid phone number for API MTS '''
    try:
        valid_phone_number = ''
        for digit in phone_number:
            if digit.isdigit():
                valid_phone_number += digit
            
        if len(valid_phone_number) >= 9:
            valid_phone_number = valid_phone_number[-1:-10:-1][::-1]
            valid_phone_number = "375" + valid_phone_number
            return valid_phone_number
        elif len(valid_phone_number) <= 8:
            text_exteption = "Телефонный номер содержит некорректный код оператора"
            notice_exception(text_exception=text_exteption)
            return None
    except Exception as text_exteption:
        notice_exception(text_exception=text_exteption)
        # TODO: message to email?


if __name__ == "__main__":
    pass
    
