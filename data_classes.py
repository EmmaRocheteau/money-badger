import datetime

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
        if(owed == 0 or category == "Bank"):
            self.owed = ""
        else:
            self.owed = "£" + "{0:,.2f}".format(owed)