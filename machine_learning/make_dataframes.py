#Save the csvs in the directory above money-badger. Run this script to obtain a slightly dodgy DataFrame with the info

import pandas as pd


def dataframer():
    graph_data = pd.read_csv('../graph_data.csv')
    prediction_data = pd.read_csv('../prediction_data.csv')

    df_for_plotting = pd.merge(graph_data, prediction_data, on='Date', how='outer')
    #df_for_plotting = pd.merge(df_for_plotting, actual_data, on='Date',
    # how='outer')
    return df_for_plotting
