import dateutil.parser as dp
import numpy as np
import pandas as pd
import yaml
import datetime
import math
import re
from pprint import pprint


def yaml_read(yaml_file):
    """Parses a YAML file and returns the resulting dictionary.
    :param yaml_file: the YAML file path, ending in .yaml."""
    with open(yaml_file, 'r') as f:
        values = yaml.load(f)
    return values


def get_owed(splitwise_output, user_id=5090950):
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
                if int(users['user']['id']) == user_id:
                    #and \
                    #    users['owed_share'] != 0. and \
                    #    users['owed_share'] is not None:
                    my_transactions.append(transactions)
    return my_transactions


#def get_paid(splitwise_output, user_id=5090950):
#    """Get relevant transactions for a specific person, checking that they
#    have not been deleted.
#    :param splitwise_output: All splitwise transactions, as returned by
#    splitwise.
#    :param user_id: User ID for the person whose transactions are to be
#    returned.
#    :return: List of dictionaries, each one corresponding to a non-deleted
#    transaction the user was involved in."""
#    my_transactions = []
#    for payments in splitwise_output:
#        if payments['deleted_at'] is None:
#            involved = payments['users']
#            for user in involved:
#                if int(user['user']['id']) == user_id:
#                    if payments['payment']:
#                        my_transactions.append(payments)
#                    elif user['paid_share'] is not None:
#                        if user['paid_share'] != 0.:
#                            my_transactions.append(payments)
#                    break
#    return my_transactions


def cleanup(my_transactions, user_id=5090950):
    """Cleans up the data. Converts costs to numbers, and datetime strings
    to dates. Returns a Pandas dataframe containing only the useful fields."""
    nice_format = []
    for transaction in my_transactions:
        owed_share = None
        for users in transaction['users']:
            if int(users['user']['id']) == user_id:
                # User is me
                owed_share = users['owed_share']
                paid_share = users['paid_share']
                # Users are unique so if found, no need to search further.
                break
        nice_format.append(
            {'Date'       : dp.parse(transaction['date']).date(),
             'Description': transaction['description'],
             'Category'   : transaction['category']['name'],
             'Owe'       : owed_share,
             'Paid'       : paid_share,
             'Payment'    : transaction['payment'],
             'Currency'   : transaction['currency_code'],
             'Group ID'   : transaction['group_id']})
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
