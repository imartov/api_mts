from datetime import datetime
import json, os
from dotenv import load_dotenv
from file_operations import FileOperations
from createrp import OneMessage
from api_mts import ApiMTS


def test():
    load_dotenv()
    fo = FileOperations()
    # fo.save_file(full_file_name="test_file.json", data_list={})
    fo.save_file(full_file_name=os.getenv("TEST_FILE_CREATE"), data_list={})
    print(os.getenv("TEST_FILE_CREATE"))


def test_send() -> None:
    phone = 375298273591
    om = OneMessage(text_message="Хватит сидеть в своих телефонах!")
    rq = om.create(phone_number=phone)

    am = ApiMTS()
    am.send_one_message_and_get_report_by_message_id(request_params=rq)


def main() -> None:
    test()

if __name__ == "__main__":
    main()