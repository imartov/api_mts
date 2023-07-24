import uuid, os, json
import datetime


class FileOperations:
    ''' class for save request params of sent messages '''
    def __init__(self) -> None:
        self.today = datetime.date.today().strftime("%d/%m/%Y").replace("/", "_")
        self.file_name = self.today + ".json"
        self.data_list = []

    def save_data(self, data, path_to_folder:str) -> None:
        ''' defining if file exists and add current time '''
        data["time"] = datetime.datetime.now().strftime('%H:%M:%S')
        full_file_name = path_to_folder + "\\" + self.file_name
        if self.file_name not in os.listdir(self.path):
            self.data_list.append(data)
            self.save_file(data_list=self.data_list, full_file_name=full_file_name)
        else:
            self.next_save_data(data)

    def save_file(self, data_list:list, full_file_name:str) -> None:
        ''' save list to file and run if file doesn't exist'''
        with open(full_file_name, "w", encoding="utf-8") as file:
            json.dump(data_list, file, ensure_ascii=False, indent=4)

    def next_save_data(self, data, full_file_name:str) -> None:
        ''' run if file exists '''
        with open(full_file_name, "r", encoding="utf-8") as file:
            self.data_list = json.load(file)
        self.data_list.append(data)
        self.save_file(data_list=self.data_list, full_file_name=full_file_name)


def create_extra_id() -> str:
    ''' generate random UUID fot extra_id '''
    return str(uuid.uuid4())


def make_valid_phone_number(phone_number:str) -> int:
    ''' method gets any phone number and change
    it to valid phone number for API MTS '''
    valid_phone_number = ''
    for digit in phone_number:
        if digit.isdigit():
            valid_phone_number += digit
        
    valid_phone_number = valid_phone_number[-1:-9] # TODO: fix
    # valid_phone_number = "375" + valid_phone_number
    print(valid_phone_number)


if __name__ == "__main__":
    make_valid_phone_number(phone_number="8-029-528-59-89")
    