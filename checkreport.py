import os, json

from dotenv import load_dotenv

from file_operations import FileOperations


class CheckReport:
    def job_id(self, full_file_name=None):
        if not full_file_name:
            load_dotenv()
            fo = FileOperations()
            file_name, full_file_name = fo.create_file_name_by_date(path_to_folder=os.getenv("SAVE_REPORTS"))
        with open(full_file_name, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        for delivering in data:
            for message in delivering["messages"]:
                print(message)


if __name__ == "__main__":
    p = CheckReport()
    p.job_id()