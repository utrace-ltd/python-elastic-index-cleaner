from datetime import *
from dateutil.parser import *
import requests
import json
import re
import os

ELASTIC_HOST = os.environ.get("ELASTIC_HOST")
ELASTIC_USERNAME = os.environ.get("ELASTIC_USERNAME")
ELASTIC_PASSWORD = os.environ.get('ELASTIC_PASSWORD')
AMOUNT_OF_DAYS = os.environ.get('AMOUNT_OF_DAYS')
GET_INDICES = '/_cat/indices?format=json&pretty=true'

r = requests.request('GET', ELASTIC_HOST + GET_INDICES, auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD))

pretty_json = r.json()
dumped_json = json.dumps(pretty_json)
ready_json = json.loads(dumped_json)

index_array = []
only_date = []
date_and_index = []
oldest_dates = []

for indexes in ready_json:
  indexs =  indexes["index"]
  index_array.append(
    {"index": indexs}
  )

date_now = datetime.now()
date_now = ('{:%Y.%m.%d}'.format(date_now))
date_now = parse(date_now, parserinfo=None)

for key in index_array:
  ssd = key["index"]
  if re.search('\d\d\d\d.\d\d.\d\d ?', ssd): 
    only_date.append(
    {"index": ssd}
  )

for keys in only_date:
  sssd = keys["index"]
  allmatches = re.findall(r'\d\d\d\d.\d\d.\d\d', sssd)
  if allmatches:
    date_and_index.append(
      {"index": sssd, "date": allmatches[0]}
    )

rgx = re.compile(' days, 0:00:00| day, 0:00:00| 0:00:00')

try:
  for date_olds in date_and_index:
    try:
      date_old = date_olds["date"]
      index_old = date_olds["index"]
      date_old = datetime.strptime(date_old, "%Y.%m.%d")
      deltas = date_now - date_old
      rrrr = rgx.sub('', str(deltas))
      rrrr = int(rrrr)
      if rrrr >= int(AMOUNT_OF_DAYS):
        oldest_dates.append(
          {"index": index_old, "days": rrrr}
        )
    except:
      print('Skip. The date does not meet the requirements.')
except:
  print('Stage not passed!')

for ind_d in oldest_dates:
  index_for_delete = ind_d["index"]
  d = requests.request('DELETE', ELASTIC_HOST + '/' + str(index_for_delete), auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD))
  print(index_for_delete, d)

print('Indexes deleted.')
