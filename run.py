from api_mts import ApiMTS
from get_data import get_data_mass_broadcast
from file_operations import FileOperations



def run_mass_broadcast(sync=False) -> None:
    ''' this method defines queues of methods
     for running mass broadcast delivering '''
    request_params = get_data_mass_broadcast(sync=sync)
    message = ApiMTS()
    if sync:
        send_messages = message.send_broadcast_sync_mass_messages_and_get_report_by_message_id(request_params=request_params)
    else:
        send_messages = message.send_broadcast_mass_messages_and_get_report_by_job_id(request_params=request_params)
    
    resp_json = send_messages["resp_message"]
    file_operations = FileOperations()
    file_operations.save_data_using_popular_api_methods(response_data=resp_json,
                                                        reports=send_messages["resp_report"])


if __name__ == "__main__":
    run_mass_broadcast()
