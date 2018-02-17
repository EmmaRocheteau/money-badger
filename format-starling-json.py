import json
from pprint import pprint

json1_file = open('data/sample-starling-data.txt')
json1_str = json1_file.read()
json1_data = json.loads(json1_str)

pprint(json1_data)