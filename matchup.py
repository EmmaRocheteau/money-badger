import parsing_splitwise as sp
import parsing_starling as st
import numpy as np
#from flask import session
import pandas as pd
from itertools import combinations
from datetime import timedelta as td


def get_sample_data():

    # Get data from starling and format to a pandas dataframe.
    stdata = st.json_read('data/sample-starling-data.txt')
    cleaned = st.cleanup(stdata)

    # Get data from spltwise and format to a pandas dataframe.
    spdata = sp.yaml_read('./data/expenses.yaml')
    #spdata = session['expenses']
    mine = sp.get_owed(spdata, user_id=5090950)
    df = sp.cleanup(mine, user_id=5090950)

    # For now, isolate to GBP.
    df = df[df['Currency'] == 'GBP']
    df2 = sp.date_filter(df, date_from='01/01/2017', to='26/12/2017')

    df3 = df2.rename(index=str, columns={"Paid": "Cost"})

    def compare_and_merge(df1, df2):
        df1['Category'] = np.nan
        df1['Group ID'] = np.nan
        df1['Payment'] = False
        df1['Owe'] = df1['Cost']
        df1['Source'] = 'Starling'
        df2['Source'] = 'Splitwise'
        combined = pd.concat([df1, df2])
        sorted = combined.sort_values('Date')
        unique_costs = np.unique(pd.to_numeric(sorted['Cost']))
        rows_to_delete = []
        rows_to_both = []
        for cost in unique_costs:
            repeats = np.where(sorted['Cost'] == cost)[0]
            if len(repeats) >= 2:
                for pair in list(combinations(repeats, 2)):
                    if sorted.iloc[pair[0], 2] - td(days=5) <= sorted.iloc[pair[1], 2] <= sorted.iloc[pair[0], 2] + td(days=5):
                        # repeated transaction
                        if sorted.iloc[pair[0], -1] == 'starling':
                            #sorted = sorted.drop(sorted.index[pair[0]])
                            #sorted.iloc[pair[1], -1] = 'both'
                            rows_to_delete.append(pair[0])
                            rows_to_both.append(pair[1])
                        else:
                            #sorted = sorted.drop(sorted.index[pair[1]])
                            #sorted.iloc[pair[0], -1] = 'both'
                            rows_to_delete.append(pair[1])
                            rows_to_both.append(pair[0])
        sorted.iloc[rows_to_both, -1] = 'both'
        rows_to_delete.sort(reverse=True)
        sorted = np.delete(np.array(sorted), rows_to_delete, 0)
        return pd.DataFrame(sorted, columns=['Category', 'Cost', 'Currency',
                                             'Date', 'Description',
                                             'Group ID', 'Owe', 'Payment',
                                             'Source'])
    return compare_and_merge(cleaned, df3)


if __name__=="__main__":
    df = get_sample_data()
    #df.to_csv('sample_data.csv')
    print(df)
