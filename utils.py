import uuid, os, json, re
from datetime import datetime

from dotenv import load_dotenv

from file_operations import FileOperations


fo = FileOperations()

def create_extra_id() -> str:
    ''' generate random UUID fot extra_id '''
    return str(uuid.uuid4())


def get_request_params_minus_messages(path_file=None,
                                      data=None,
                                      request_params=None,
                                      double=False) -> dict:
        ''' this method removes from request_params any data in format:
        {
            unp: {
                "payment_date": "%d.%m.%Y",
                any...
            }
        }
        Define double=True for saving in request_params recicpent
        if payment_date of request_params > payment_date of FIRST_SUCCESS_MESSAGES '''
        if not request_params:
            request_params = fo.get_last_element(path_folder=os.getenv("VIRGIN_REQ_PAR_MASS_BROAD"))
        if path_file:
            data = fo.get_data_from_json_file(path_file=path_file)
        recipients = []
        for recipient in request_params["recipients"]:
            str_unp = str(recipient["unp"])
            if str_unp not in data:
                recipients.append(recipient)
            else:
                rq_pay_date = datetime.strptime(recipient["payment_date"], "%d.%m.%Y").date()
                data_pay_date = datetime.strptime(data[str_unp]["payment_date"], "%d.%m.%Y").date()
                if double and rq_pay_date > data_pay_date:
                    recipients.append(recipient)
        request_params["recipients"] = recipients
        return request_params


def remove_message_from_success(unp=None, unp_list=None, double=None) -> None:
    success_file_name =  "SAVE_FILE_SUCCESS_MESSAGES_DOUBLE" if double else "SAVE_FILE_SUCCESS_MESSAGES_FIRST"
    success_messages = fo.get_data_from_json_file(os.getenv(success_file_name))
    if unp:
        if unp in success_messages:
            del success_messages[unp]
    if unp_list:
        for unp in unp_list:
            if unp in success_messages:
                del success_messages[unp]
    fo.save_file(data_list=success_messages, full_file_name=os.getenv(success_file_name))


def main() -> None:
    pass

if __name__ == "__main__":
    pass
    
