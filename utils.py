import uuid, os, json
import datetime


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


    def delete_file(self, path_to_folder:list, count_days=30) -> None:
        ''' this method removes file that was created defined days ago '''
        delete_data = datetime.datetime.now() - datetime.timedelta(days=count_days)
        delete_file = delete_data.strftime(self.strftime) + self.file_extension
        print(delete_file)
        # TODO: to end



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


if __name__ == "__main__":
    p = FileOperations().create_file_name_by_date(path_to_folder="a")
    print(p)
    
