from datetime import datetime
import json, os
from dotenv import load_dotenv
from file_operations import FileOperations


def test():
    load_dotenv()
    fo = FileOperations()
    fo.save_file(full_file_name="\\Bymnssrvlnk2\\sms\\api_mts\\test_file.json", data_list={})

def main() -> None:
    test()

if __name__ == "__main__":
    main()