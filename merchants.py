
import json
import pandas as pd


class Merchant:
    def __init__(self, name, location_name, place_id, amount):
        self.title = '{} {}'.format(name, location_name)
        self.place_id = place_id
        self.amount = amount





if __name__ == '__main__':
    file_name = 'card_transactions.json'
    get_merchants(file_name)