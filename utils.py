import uuid, os, json, re
from dotenv import load_dotenv
from file_operations import FileOperations


def create_extra_id() -> str:
    ''' generate random UUID fot extra_id '''
    return str(uuid.uuid4())

def get_request_params_minus_messages(path_file=None,
                                      data=None,
                                      request_params=None,
                                      double=False) -> dict:
        fo = FileOperations()
        if not request_params:
            request_params = fo.get_last_element(path_folder=os.getenv("VIRGIN_REQ_PAR_MASS_BROAD"))
        if path_file:
            data = fo.get_data_from_json_file(path_file=path_file)
        recipients = []
        for recipient in request_params["recipients"]:
            if str(recipient["unp"]) not in data:
                recipients.append(recipient)
            else:
                 if double:
                      if recipient["payment_date"] != data[str(recipient["unp"])]["payment_date"]:
                           recipients.append(recipient)
        request_params["recipients"] = recipients
        return request_params


if __name__ == "__main__":
    pass
    
