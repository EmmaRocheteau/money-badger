import parsing_splitwise as sp
import parsing_starling as st

# Get data from starling and format to a pandas dataframe.
stdata = st.json_read('data/sample-starling-data.txt')
cleaned = st.cleanup(stdata)


# Get data from spltwise and format to a pandas dataframe.
spdata = sp.yaml_read('.\data\expenses.yaml')
mine = sp.get_owed(spdata, user_id=5090950)
df = sp.cleanup(mine, user_id=5090950)

# For now, isolate to GBP.
df = df[df['Currency'] == 'GBP']
df2 = sp.date_filter(df, date_from='15/07/2017', to='15/07/2017')

print(df2[['Category', 'Currency', 'Date', 'Description', 'Paid', 'Payment']])


