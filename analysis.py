from datetime import datetime, timedelta
import os, json

from file_operations import FileOperations


fo = FileOperations()

class Analysis():
    def __init__(self) -> None:
        self.debtors_count = 0
        self.debt_sum = 0

    def debtors_counting(self) -> None:
        self.debtors_count += 1

    def debt_summation(self, debt:float) -> None:
        if debt:
            self.debt_sum += float(debt)

    def date_selection(self, date:str, debt:str) -> None:
        valid_date = datetime.strptime(date, "%d.%m.%Y").date()
        compare_date = (datetime.now() - timedelta(days=30)).date()
        if valid_date >= compare_date:
            self.debtors_counting()
            self.debt_summation(debt=float(debt))

    def debt_selection(self, debt:float) -> None:
        compare_sum = 1
        if float(debt) > compare_sum:
            self.debt_summation(debt=float(debt))
            self.debtors_counting()

    def counting_sum_from_recipients(self, recipients:list) -> int:
        for recipient in recipients:
            self.debt_sum += recipient["debt_sum"]
        return self.debt_sum
    
    def update_daily_stat(self) -> None:
        file_name, full_file_name = fo.create_file_name_by_date(path_to_folder=os.getenv("FOLDER_STAT"))
        daily_stat = fo.get_data_from_json_file(path_file=os.getenv("JSON_REPORT_MESSAGE"))
        with open(full_file_name, "w", encoding="utf-8") as file:
            json.dump(daily_stat, file, indent=4, ensure_ascii=False)
        today_stat = {}
        key = file_name.replace(".json", "")
        today_stat[key] = daily_stat
        with open(os.getenv("STAT_FILE"), "r", encoding="utf-8") as file:
            all_daily_stat = json.load(file)
        all_daily_stat.update(today_stat)
        with open(full_file_name, "w", encoding="utf-8") as file:
            json.dump(all_daily_stat, file, indent=4, ensure_ascii=False)




def main() -> None:
    a = Analysis()
    a.date_selection(date="01.01.2022")

if __name__ == "__main__":
    main()