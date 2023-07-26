import uuid, os, json
import datetime
from dotenv import load_dotenv
from api_mts import ApiMTS


class FileOperations:
    ''' class for save request params of sent messages '''
    def __init__(self) -> None:
        self.strftime_time = "%H:%M:%S"
        self.data_list = []

    def create_file_name_by_date(self, path_to_folder:str, data=datetime.date.today()) -> dict:
        ''' this method creates file name using defined data
        default defined data is today '''
        strftime_date = "%d/%m/%Y"
        file_extension = ".json"
        file_name = data.strftime(strftime_date).replace("/", "_") + file_extension
        full_file_name = path_to_folder + "\\" + file_name
        return file_name, full_file_name


    def save_data(self, data, path_to_folder:str) -> None:
        ''' defining if file exists and add current time '''
        data["time"] = datetime.datetime.now().strftime(self.strftime_time)
        file_name, full_file_name = self.create_file_name_by_date(path_to_folder=path_to_folder)
        if file_name not in os.listdir(path_to_folder):
            self.data_list.append(data)
            self.save_file(data_list=self.data_list, full_file_name=full_file_name)
        else:
            self.next_save_data(data, full_file_name=full_file_name)


    def save_file(self, data_list:list, full_file_name:str) -> None:
        ''' save list to file and run if file doesn't exist'''
        with open(full_file_name, "w", encoding="utf-8") as file:
            json.dump(data_list, file, ensure_ascii=False, indent=4)
        self.data_list = []


    def next_save_data(self, data, full_file_name:str) -> None:
        ''' method opens exist file and rewrite it by adding new data '''
        with open(full_file_name, "r", encoding="utf-8") as file:
            self.data_list = json.load(file)
        self.data_list.append(data)
        self.save_file(data_list=self.data_list, full_file_name=full_file_name)


    def delete_file(self, paths_to_folders:list, count_days=30) -> None:
        ''' this method removes file that was created defined days ago '''
        delete_data = datetime.datetime.now() - datetime.timedelta(days=count_days)
        for path_to_folder in paths_to_folders:
            delete_file_tuple = self.create_file_name_by_date(path_to_folder=path_to_folder, data=delete_data)
            if os.path.isfile(delete_file_tuple[1]):
                os.remove(delete_file_tuple[1])


def create_extra_id() -> str:
    ''' generate random UUID fot extra_id '''
    return str(uuid.uuid4())


def make_valid_phone_number(phone_number:str):
    ''' method gets any phone number and change
    it to valid phone number for API MTS '''
    valid_phone_number = ''
    for digit in phone_number:
        if digit.isdigit():
            valid_phone_number += digit
        
    if len(valid_phone_number) >= 9:
        valid_phone_number = valid_phone_number[-1:-10:-1][::-1]
        valid_phone_number = "375" + valid_phone_number
        return valid_phone_number
    elif len(valid_phone_number) <= 8:
        print("\nТелефонный номер содержит некорректный код оператора")
        # TODO: notice to phone
        return None


def notice_exception(text_exception:str) -> None:
    ''' this method sends to defined phone number notice 
     abut exceptions during running key methods '''
    load_dotenv()
    with open(os.getenv("NOTICE_EXCEPTION_TEXT_MESSAGE"), "r", encoding="utf-8") as file:
        text_message = file.read()
    
    with open(os.getenv("NOTICE_EXCEPTION_REQUEST_PARAMS"), "r", encoding="utf-8") as file:
        request_params = json.load(file)

        request_params["phone_number"] = int(os.getenv("NOTICE_EXCEPTION_PHONE_NUMBER"))
        request_params["extra_id"] = create_extra_id()
        alpha_name = os.getenv("ALPHA_NAME")
        request_params["channel_options"]["sms"]["text"] = text_message
        request_params["channel_options"]["sms"]["alpha_name"] = alpha_name
        request_params["channel_options"]["viber"]["text"] = text_message
        request_params["channel_options"]["viber"]["alpha_name"] = alpha_name

    message = ApiMTS().send_one_message_and_get_report_by_message_id(by="one_message", request_params=request_params)

    file_operations = FileOperations()
    file_operations.save_data(data=message["response_json"], path_to_folder=os.getenv("SAVE_REQUEST_PARAMS"))
    file_operations.save_data(data=message["response_json"], path_to_folder=os.getenv("SAVE_REQUEST_PARAMS"))


if __name__ == "__main__":
    paths_to_folders = [
        "a\\aa",
        "b\\bb",
        "c\\cc"
    ]
    p = FileOperations().delete_file(paths_to_folders=paths_to_folders)
    
