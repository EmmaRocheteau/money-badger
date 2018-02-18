from app.views import get_starling
import json
import pandas as pd


class Merchant:
    def __init__(self, name, location_name, place_id, amount):
        self.title = '{} {}'.format(name, location_name)
        self.place_id = place_id
        self.amount = amount


def get_merchants(file_name):
    json1_file = open(file_name)
    json1_str = json1_file.read()
    data = json.loads(json1_str)

    merchants = []
    for transaction in data['_embedded']['transactions']:
        amount = -transaction['amount']
        if 'merchantLocation' in transaction['_links']:
            getreq = str(transaction['_links']['merchantLocation']['href'])
            merchant_loc = str(getreq.split('/')[-1])
            merchant = str(getreq.split('/')[-3])
            merchant_data = get_starling(
                "idBjil3J7CS0ZCa1wqSN4vReAiM3oq2Sl0iaE6MY1MN9Bj0B0skZBxdd3X7vMRKY",
                'merchants/{}/locations/{}'.format(merchant, merchant_loc))
            print(merchant_data)
            merchants.append([merchant_data['merchantName'], merchant_data[
                'locationName'], merchant_data['googlePlaceId'], amount])
    merchants = pd.DataFrame(merchants, columns=[
        'Merchant Name', 'Location Name', 'Place ID', 'Cost']).groupby(
        ['Merchant Name', 'Location Name', 'Place ID'])['Cost'].agg('sum')
    merchants = merchants.to_frame(name='Cost').reset_index()

    ms = []
    for index, row in merchants.iterrows():
        ms.append(Merchant(row['Merchant Name'], row['Location Name'],
                           row['Place ID'], row['Cost']))

    return ms


if __name__ == '__main__':
    file_name = 'card_transactions.json'
    get_merchants(file_name)