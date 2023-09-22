import os, json
from dotenv import load_dotenv
from utils import create_extra_id


class CreateRequestParams:
    load_dotenv()
    # TODO: include classes

    def __init__(self, alpha_name=None, ttl=300) -> None:
        with open(os.getenv("PATH_EXAM_MASS_BRO_REQ_PAR"), "r", encoding="utf-8") as file:
            self.mass_broadcast = json.load(file)
        if not alpha_name:
            self.mass_broadcast["channel_options"]["sms"]["alpha_name"] = os.getenv("ALPHA_NAME")
        else:
            self.mass_broadcast["channel_options"]["sms"]["alpha_name"] = os.getenv("ALPHA_NAME")
        self.mass_broadcast["channel_options"]["sms"]["ttl"] = ttl

    def get_mass_broadcast(self, phone_number:int, company_name:str, debt_sum:str, text_message=None) -> dict:
        if not text_message:
            with open(os.getenv("PATH_EXAM_MASS_BRO_TEXT_MESS"), "r", encoding="utf-8") as file:
                text_message = file.read()
            self.mass_broadcast["channel_options"]["sms"]["text"] = text_message
        else:
            self.mass_broadcast["channel_options"]["sms"]["text"] = text_message

        del self.mass_broadcast["recipients"][0]
        extra_id = create_extra_id()
        recipient = {
            "phone_number": phone_number,
            "extra_id": extra_id,
            "company_name": company_name,
            "debt_sum": debt_sum
        }
        self.mass_broadcast["recipients"].append(recipient)

        print(self.mass_broadcast)


if __name__ == "__main__":
    p = CreateRequestParams()
    p.get_mass_broadcast(34534, 'sdcsdc', 987)