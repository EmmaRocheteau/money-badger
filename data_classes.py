import datetime
import pandas as pd
import matchup as m

class Debtor():
    def __init__(self, name, amount):
        self.name = str(name)
        self.amount = "£" + "{0:,.2f}".format(amount)

class Record():
    def __init__(self, date, desc, amount, category, source, owed=0):
        self.date = date.strftime("%Y/%m/%d")
        self.description = desc
        self.amount = "£" + "{0:,.2f}".format(amount)
        self.category = str(category)
        self.source = str(source)
        if owed == 0 or category == "Bank":
            self.owed = ""
        else:
            self.owed = "£" + "{0:,.2f}".format(owed)


def create_records(sample_data):
    records = []
    print(sample_data)
    for i in range(len(sample_data)):
        row = sample_data.iloc[i]
        print(row)
        records.append(Record(row['Date'].date(), row['Description'],
                              row['Cost'],
                              row['Category'], row['Source'], row['Owe']))
    return records


if __name__ == '__main__':
    df = m.get_sample_data()
    print(len(create_records(df)))