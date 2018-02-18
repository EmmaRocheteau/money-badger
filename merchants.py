from app.views import get_starling
from pprint import pprint
import json

json1_file = open('card_transactions.json')
json1_str = json1_file.read()
data = json.loads(json1_str)
#card_transacts = []
#for transaction in data['_embedded']['transactions']:
#    if transaction['source'] == 'MASTER_CARD':
#        getreq = str(transaction['_links']['detail']['href'])
#        trans = getreq.split('/')[-1]
#        card_transacts.append(get_starling(
#
## "idBjil3J7CS0ZCa1wqSN4vReAiM3oq2Sl0iaE6MY1MN9Bj0B0skZBxdd3X7vMRKY",
#            'transactions/mastercard/', transactionUid=trans))

merchants = []
for transaction in data['_embedded']['transactions']:
    if 'merchantLocation' in transaction['_links']:
        getreq = str(transaction['_links']['merchantLocation']['href'])
        merchant_loc = str(getreq.split('/')[-1])
        merchant = str(getreq.split('/')[-3])
        merchants.append(get_starling(
            "idBjil3J7CS0ZCa1wqSN4vReAiM3oq2Sl0iaE6MY1MN9Bj0B0skZBxdd3X7vMRKY",
            'merchants/{}/locations/{}'.format(
                merchant, merchant_loc)))

place_ids = []
for merchant in merchants:
    place_ids.append(merchant['googlePlaceId'])

print(place_ids)
