import dateutil.parser as dp
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import math
import re
import json


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
        if transaction['direction'] == 'OUTBOUND':
            nice_format.append(
                {'Date'       : dp.parse(transaction['created']).date(),
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


if __name__ == '__main__':
    # Get data from file and format to a pandas dataframe.
    data = json_read('data/sample-starling-data.txt')
    #mine = get_mine(data, user_id=5090950)
    #df = cleanup(mine, user_id=5090950)
    cleaned = cleanup(data)
    print(cleaned)
    # For now, isolate to GBP.
    #df = df[df['Currency'] == 'GBP']
    #df2 = date_filter(df, date_from='11/09/2017', to='31/12/2017')
    ## categorise = df.groupby('Category').agg({'Cost': 'sum'})
    ## print(categorise)
    #df2['Day'] = [date.weekday() for date in df2['Date']]
    #wkdy = df2[df2['Day'] <= 4]
    #lnch = wkdy[wkdy['Description'].str.contains(re.compile(r'[L|l]unch'))]
    #no_pub = lnch[lnch['Description'].str.contains(re.compile(("^(
    ## ?!Pub|\\.).*")))]
    #no_pub = no_pub[
    #    no_pub['Description'].str.contains(re.compile(("^(?!Byron|\\.).*")))]
    #print(no_pub)

    #no_pub["Date"] = pd.to_datetime(df["Date"])
    #no_pub.groupby(no_pub['Date'].dt.week).agg({'Cost': 'sum'})
    #print(no_pub)

    # day_names = ['t', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
    #             'Saturday', 'Sunday']
    # day_split = df.groupby(['Category', 'Day']).agg({'Cost': 'sum'})
    # print(day_split)
    ## print(day_split.loc['Bus/train'].index.values)
    # cats = []
    # for index in day_split.index.values:
    #    cats.append(index[0])
    # cats = list(set(cats))  # get unique values#

    # series = []
    # last_series = np.zeros(7)
    # x1 = [0, 1, 2, 3, 4, 5, 6]
    # print(cats)
    # n = 30
    # colors = [plt.get_cmap('flag')(1. * i / n) for i in range(n)]
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # patterns = ('-', '+', 'x', r'\\', '*', '.', '/', '//')
    # q = 0
    # for cat in cats:
    #    if cat == 'Rent':
    #        pass
    #    else:
    #        x = day_split.loc[cat].index.values
    #        y = day_split.loc[cat]['Cost'].tolist()
    #        y1 = [0, 0, 0, 0, 0, 0, 0]
    #        j = 0
    #        for i in x:
    #            y1[i] = y[j]
    #            j += 1
    #        series.append(ax.bar(x1, y1, bottom=last_series, label=cat,
    #                             color=colors[cats.index(cat)],
    ## hatch=patterns[q]))
    #        q += 1
    #        q = q % 8
    #        last_series += np.array(y1)
    # ax.set_xticklabels(day_names, fontsize=14)
    # ax.get_yaxis().set_ticklabels([])
    # ax.set_ylabel('Cost', fontsize=14)
    # plt.legend(loc=9, fontsize=14, bbox_to_anchor=(0.5, -0.1), ncol=7)
    # plt.show()
    # for category in vals:
    #    series.append(plt.bar())
    # n = 40
    # cat = np.array(categorise).squeeze()
    # expl = (max(cat)-cat)/np.array(np.sum(categorise))
    # labels = categorise.index.values
    # colors = [plt.get_cmap('flag')(1. * i / n) for i in range(n)]
    # patches, texts = plt.pie(
    #    categorise, explode=expl, colors=colors, labels=['']*len(labels),
    #    labeldistance=1.2, startangle=20)
    # for t in texts:
    #    t.set_horizontalalignment('center')
    # plt.axis('equal')
    # for label, t in zip(labels, texts):
    #    x, y = t.get_position()
    #    angle = int(math.degrees(math.atan2(y, x)))
    #    ha = "left"
    #    va = "bottom"
#
#    if angle > 90:
#        angle -= 180
#
#    if angle < 0:
#        va = "top"
#
#    if -45 <= angle <= 0:
#        ha = "right"
#        va = "bottom"
#
#    plt.annotate(label, xy=(x, y), rotation=angle, ha=ha, va=va, size=14)
# plt.show()
