import os
from dotenv import load_dotenv
from api_mts import ApiMTS
from get_data import GetData
from file_operations import FileOperations


def run_mass_broadcast(sync=False) -> None:
    ''' this method defines queues of methods
     for running mass broadcast delivering '''
    # try:
    #     request_params = GetData().get_request_params_mass_broadcast(sync=sync)
    message = ApiMTS()
    #     if sync:
    #         print("sync")
    #         send_messages = message.send_broadcast_sync_mass_messages_and_get_report_by_message_id(request_params=request_params)
    #     else:
    #         print("no sync")
    #         send_messages = message.send_broadcast_mass_messages_and_get_report_by_job_id(request_params=request_params)
    #         print(send_messages)
        
    #     response_data = send_messages["resp_message"]
    #     reports = send_messages["resp_report"]
    #     file_operations = FileOperations()
    #     file_operations.save_data_using_popular_api_methods(request_params = request_params,
    #                                                         response_data=response_data,
    #                                                         reports=reports)
        
    load_dotenv()
    with open(os.getenv("SUCCES_ONE_MESSAGE_TEXT"), "r", encoding="utf-8") as file:
        text = file.read()
    request_params_info = GetData().get_request_params_one_message(text=text, phone_number=int(os.getenv("INFO_PHONE_NUMBER")))
    print(request_params_info)
    message.send_one_message_and_get_report_by_message_id(request_params=request_params_info)
        
    # except Exception as text_exception:

        # TODO: message about successfully message-sending
        # TODO: message about mistake during message-sending


if __name__ == "__main__":
    run_mass_broadcast()