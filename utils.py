import uuid, os, json
import datetime


class FileOperations:
    ''' class for save request params of sent messages '''
    def __init__(self, path_to_folder:str) -> None:
        self.today = datetime.date.today().strftime("%d/%m/%Y").replace("/", "_")
        self.path = path_to_folder
        self.file_name = self.today + ".json"
        self.full_file_name = self.path + "\\" + self.file_name
        self.data_list = []

    def save_data(self, data:dict) -> None:
        ''' defining if file exists and add current time '''
        data["time"] = datetime.datetime.now().strftime('%H:%M:%S')
        if self.file_name not in os.listdir(self.path):
            self.data_list.append(data)
            self.save_file(data_list=self.data_list)
        else:
            self.next_save_data(data)

    def save_file(self, data_list:list) -> None:
        ''' save list to file and run if file doesn't exist'''
        with open(self.full_file_name, "w", encoding="utf-8") as file:
            json.dump(data_list, file, ensure_ascii=False, indent=4)

    def next_save_data(self, data:dict) -> None:
        ''' run if file exists '''
        with open(self.full_file_name, "r", encoding="utf-8") as file:
            self.data_list = json.load(file)
        self.data_list.append(data)
        self.save_file(data_list=self.data_list)


def create_extra_id() -> str:
    ''' generate random UUID fot extra_id '''
    return str(uuid.uuid4())


if __name__ == "__main__":
    p = FileOperations()
    data = [
        {1: "data1"},
        {2: "data2"},
        {3: "data3"}
    ]

    for i in data:
        p.save_request_params(i)
    