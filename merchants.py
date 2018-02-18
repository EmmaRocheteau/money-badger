from app.views import get_starling
from parsing_starling import json_read

data = json_read('card_transactions.json')
card_transacts = []
for transaction in data['_embedded']['transactions']:
    if transaction['source'] == 'MASTER_CARD':
        getreq = str(transaction['_links']['detail']['href'])
        getreq = getreq.split('/')[2:]
        getreq[-1] = 'transactionUid' + getreq[-1]
        getreq = '/'.join(getreq)
        card_transacts.append(get_starling(
            "idBjil3J7CS0ZCa1wqSN4vReAiM3oq2Sl0iaE6MY1MN9Bj0B0skZBxdd3X7vMRKY",
            getreq))

print(card_transacts)