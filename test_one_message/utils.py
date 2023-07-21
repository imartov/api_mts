import uuid, os, json
from datetime import date


class FileOperations:
    ''' class for save request params of sent messages '''
    def __init__(self) -> None:
        self.today = date.today().strftime("%d/%m/%Y").replace("/", "_")
        self.path = "test_one_message\\sent_messages"
        self.file_name = self.today + ".json"
        self.full_file_name = self.path + "\\" + self.file_name
        self.messages_list = []

    def save_request_params(self, request_params:dict) -> None:
        ''' defining if file exists '''
        if self.file_name not in os.listdir(self.path):
            self.messages_list.append(request_params)
            self.save_file(list_request_params=self.messages_list)
        else:
            self.next_save_request_params(request_params)

    def save_file(self, list_request_params:list) -> None:
        ''' save list to file and run if file doesn't exist'''
        with open(self.full_file_name, "w", encoding="utf-8") as file:
            json.dump(list_request_params, file, ensure_ascii=False, indent=4)

    def next_save_request_params(self, request_params:dict) -> None:
        ''' run if file exists '''
        with open(self.full_file_name, "r", encoding="utf-8") as file:
            self.messages_list = json.load(file)
        self.messages_list.append(request_params)
        self.save_file(list_request_params=self.messages_list)


if __name__ == "__main__":
    p = FileOperations()
    data = [
        {1: "data1"},
        {2: "data2"},
        {3: "data3"}
    ]

    for i in data:
        p.save_request_params(i)
    