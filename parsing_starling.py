import dateutil.parser as dp
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import math
import re
import json
from datetime import datetime
import random


def json_read(json_file):
    """Parses a YAML file and returns the resulting dictionary.
    :param yaml_file: the YAML file path, ending in .yaml."""
    json1_file = open('data/sample-starling-data.txt')
    json1_str = json1_file.read()
    return json.loads(json1_str)


def get_mine(splitwise_output, user_id=5090950):
    """Get relevant transactions for a specific person, checking that they
    have not been deleted.
    :param splitwise_output: All splitwise transactions, as returned by
    splitwise.
    :param user_id: User ID for the person whose transactions are to be
    returned.
    :return: List of dictionaries, each one corresponding to a non-deleted
    transaction the user was involved in."""
    my_transactions = []
    for transactions in splitwise_output:
        if transactions['deleted_at'] is None:
            involved = transactions['users']
            for users in involved:
                if int(users['user']['id']) == user_id and \
                        users['owed_share'] != 0. and \
                        users['owed_share'] is not None:
                    my_transactions.append(transactions)
    return my_transactions


def cleanup(data):
    """Cleans up the data. Converts costs to numbers, and datetime strings
    to dates. Returns a Pandas dataframe containing only the useful fields."""
    nice_format = []

    for transaction in data['_embedded']['transactions']:
        year = 2017
        month = random.choice(range(1, 13))
        day = random.choice(range(1, 29))
        date = datetime(year, month, day)

        if transaction['direction'] == 'OUTBOUND':
            nice_format.append(
                {'Date'       : date.date(),
                 'Description': transaction['narrative'],
                 'Cost'       : np.float(-transaction['amount']),
                 'Currency'   : transaction['currency']})
    return pd.DataFrame(nice_format)


def date_filter(transactions, date_from=None, to=None):
    """Returns the transactions dataframe filtered by date within a certain
    range.
    :param transactions: Transactions dataframe.
    :param date_from: String in format 'dd-mm-yy' or a date type. If None,
    defaults to oldest date.
    :param to: String in format 'dd-mm-yy' or a date type. If None, defaults to
    newest date, even if in the future.
    :return: Transactions dataframe within these dates."""
    if date_from is None:
        date_from = transactions['Date'].min()
    elif type(date_from) is not datetime.date:
        date_from = dp.parse(date_from, dayfirst=True).date()
    if to is None:
        to = transactions['Date'].max()
    elif type(to) is not datetime.date:
        to = dp.parse(to, dayfirst=True).date()
    mask = (transactions['Date'] >= date_from) & \
           (transactions['Date'] <= to)
    return transactions.loc[mask]
