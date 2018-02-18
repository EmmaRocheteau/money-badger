import pandas as pd
import copy

def get_balance(data_path, start_balance=1000):
    data = pd.read_csv(data_path)
    cost_data = data.groupby('Date')['Cost'].sum()

    idx = pd.date_range('2017-01-01', '2017-12-26')
    cost_data.index = pd.DatetimeIndex(cost_data.index)

    cost_data = cost_data.reindex(idx, fill_value=0)

    current_balance = start_balance
    balance_data = copy.deepcopy(cost_data)

    for i in range(len(cost_data)):
        current_balance -= cost_data[i]
        balance_data[i] = current_balance
    return balance_data.reset_index()


if __name__ == "__main__" :
    print(get_balance('../sample_data.csv'))

