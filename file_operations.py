import os, json, time
import datetime

from loguru import logger
from dotenv import load_dotenv


load_dotenv()

class FileOperations:
    ''' class for save request params of sent messages '''
    def __init__(self) -> None:
        self.strftime_datatime_format = "%d.%m.%Y %H:%M:%S"
        self.data_list = []

    def create_file_name_by_date(self, path_to_folder=None, date=datetime.date.today()) -> dict:
        ''' this method creates file name using defined date
        default defined date is today '''
        strftime_date = "%d/%m/%Y"
        file_extension = ".json"
        file_name = date.strftime(strftime_date).replace("/", "_") + file_extension
        if path_to_folder:
            full_file_name = path_to_folder + "\\" + file_name
            return file_name, full_file_name
        else:
            return file_name

    def save_data(self, data, path_to_folder:str) -> None:
        ''' defining if file exists and add current time '''
        copy_data = dict(data) if data.__class__ == {}.__class__ else data.copy()
        if data.__class__ == {}.__class__:
            copy_data["datetime"] = datetime.datetime.now().strftime(self.strftime_datatime_format)
        file_name, full_file_name = self.create_file_name_by_date(path_to_folder=path_to_folder)
        if file_name not in os.listdir(path_to_folder):
            self.data_list.append(copy_data)
            self.save_file(data_list=self.data_list, full_file_name=full_file_name)
        else:
            self.next_save_data(copy_data, full_file_name=full_file_name)

    def save_file(self, data_list, full_file_name:str) -> None:
        ''' this method create or rewrite json file'''
        with open(full_file_name, "w", encoding="utf-8") as file:
            json.dump(data_list, file, ensure_ascii=False, indent=4)
        self.data_list = []

    def next_save_data(self, data, full_file_name:str) -> None:
        ''' method opens exist file and rewrite it by adding new data '''
        with open(full_file_name, "r", encoding="utf-8") as file:
            self.data_list = json.load(file)
        self.data_list.append(data)
        self.save_file(data_list=self.data_list, full_file_name=full_file_name)

    def save_data_using_popular_api_methods(self, **kwargs) -> None:
        ''' this method saves data that return after using
         popular methods in api_mts.py '''
        for key, value in kwargs.items():
            path_to_folder = "SAVE_" + str(key).upper()
            self.save_data(data=value, path_to_folder=os.getenv(path_to_folder))

    def delete_file(self) -> None:
        ''' this method removes file that was created defined days ago '''
        logger.info("Start 'file_operations.FileOperations.delere_file' method")
        check_date = (datetime.datetime.now() - datetime.timedelta(days=int(os.getenv("DAYS_DELETE_FILE")))).date()
        paths_list = [
            os.getenv("FOLDER_FAIL_MESSAGES"),
            os.getenv("SAVE_FIRST_REPORTS_JOB_ID"),
            os.getenv("SAVE_DOUBLE_REPORTS_JOB_ID"),
            os.getenv("SAVE_REPORTS_ONE_MESSAGE"),
            os.getenv("SAVE_RESPONSE_DATA"),
            os.getenv("SAVE_SUCCESS_MESSAGES_FIRST"),
            os.getenv("SAVE_SUCCESS_MESSAGES_DOUBLE"),
            os.getenv("VIRGIN_REQ_PAR_MASS_BROAD"),
            os.getenv("VIRGIN_DOUBLE_REQ_PAR_MASS_BROAD"),
            os.getenv("SAVE_FIRST_REQ_PAR_MASS_BROAD"),
            os.getenv("SAVE_DOUBLE_REQ_PAR_MASS_BROAD"),
            os.getenv("SAVE_REQ_PAR_ONE_MESS"),
        ]
        exeptions = [
            "fail_mesages.json",
            "success_messages.json"
        ]
        for path in paths_list:
            files_list = os.listdir(path)
            for file in files_list:
                full_path = path + "\\" + file
                time_created = datetime.datetime.utcfromtimestamp(os.path.getctime(full_path)).date()
                if time_created <= check_date and file not in exeptions:
                    os.remove(full_path)
        logger.info("End 'file_operations.FileOperations.delere_file' method")

    def get_last_element(self, path_folder=None, path_file=None, mylist=None) -> dict:
        if path_file:
            data = self.get_data_from_json_file(path_file=path_file).pop()
            return data
        elif mylist:
            return mylist.pop()
        else:
            file_name = self.create_file_name_by_date()
            full_file_name = path_folder + "\\" + file_name
            if file_name in os.listdir(path_folder):
                data = self.get_data_from_json_file(path_file=full_file_name).pop()
                return data
        
    def get_data_from_json_file(self, path_file) -> dict:
        with open(path_file, "r", encoding="utf-8") as file:
            messages = json.load(file)
        return messages


def report_message_form(labels) -> None:
    with open(os.getenv("JSON_REPORT_MESSAGE"), "r", encoding="utf-8") as file:
        json_report_message = json.load(file)
    for key, value in labels.items():
        print(key)
        if key in json_report_message:
            json_report_message[key] = value
    with open(os.getenv("JSON_REPORT_MESSAGE"), "w", encoding="utf-8") as file:
        json.dump(json_report_message, file, indent=4, ensure_ascii=False)


def main() -> None:
    fo = FileOperations().delete_file()

if __name__ == "__main__":
    main()
