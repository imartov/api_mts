from datetime import datetime
import json, os
from dotenv import load_dotenv


def test(unp):
    load_dotenv()
    path_file = "SAVE_FILE_SUCCESS_MESSAGES_FIRST"
    with open(os.getenv(path_file), "r", encoding="utf-8") as file:
        all_success_messages = json.load(file)

    if str(unp) not in all_success_messages:
        print("unp is not exist")
        all_success_messages[str(unp)] = {
            "company_name": "company_name",
            "payment_date": "payment_date",
            "phone_number": "phone_number"
        }
        with open(os.getenv(path_file), "w", encoding="utf-8") as file:
            json.dump(all_success_messages, file, indent=4, ensure_ascii=False)
    else:
        print("unp is exist")

if __name__ == "__main__":
    test(unp=1000564284)