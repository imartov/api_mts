from datetime import datetime, timedelta


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

    def counting(self, clist:list, key:str, var:str):
        pass


def main() -> None:
    a = Analysis()
    a.date_selection(date="01.01.2022")

if __name__ == "__main__":
    main()