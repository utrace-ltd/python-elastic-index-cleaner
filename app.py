# -*- coding: utf-8 -*-

from datetime import *
from dateutil.parser import *
import requests
import json
import re
import os
import logging

ELASTIC_HOST = os.environ.get("ELASTIC_HOST")
ELASTIC_USERNAME = os.environ.get("ELASTIC_USERNAME")
ELASTIC_PASSWORD = os.environ.get("ELASTIC_PASSWORD")
AMOUNT_OF_DAYS_PROD = os.environ.get("AMOUNT_OF_DAYS_PROD")
AMOUNT_OF_DAYS_MORE = os.environ.get("AMOUNT_OF_DAYS_MORE")
GET_INDICES = '/_cat/indices?format=json&pretty=true'

index_array = []
only_date = []
date_and_index_prod = []
date_and_index_more = []
oldest_dates_prod = []
oldest_dates_more = []

logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)

r = requests.request('GET', ELASTIC_HOST + GET_INDICES,
                     auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD))

pretty_json = r.json()
dumped_json = json.dumps(pretty_json)
ready_json = json.loads(dumped_json)

for indexes in ready_json:
    indexs = indexes["index"]
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

    prod_or_more = re.findall(r'prod|stage|test|dev', sssd)

    for i in range(0, len(prod_or_more)):
        if prod_or_more[i] == 'prod':
            date_and_index_prod.append(
                {"index": sssd,
                    "date": allmatches[0], "state": prod_or_more[i]}
            )
        elif prod_or_more[i] == 'stage' or 'test' or 'dev':
            date_and_index_more.append(
                {"index": sssd,
                    "date": allmatches[0], "state": prod_or_more[i]}
            )

rgx = re.compile(' days, 0:00:00| day, 0:00:00| 0:00:00')

try:
    for date_olds in date_and_index_prod:
        try:
            date_old = date_olds["date"]
            index_old = date_olds["index"]
            state_old = date_olds["state"]

            date_old = datetime.strptime(date_old, "%Y.%m.%d")
            deltas = date_now - date_old
            rrrr = rgx.sub('', str(deltas))
            rrrr = int(rrrr)
            if rrrr > int(AMOUNT_OF_DAYS_PROD):
                oldest_dates_prod.append(
                    {"index": index_old, "days": rrrr, "state": state_old}
                )
        except:
            logging.warning('Skip. The date does not meet the requirements.')
    for date_olds in date_and_index_more:
        try:
            date_old = date_olds["date"]
            index_old = date_olds["index"]
            state_old = date_olds["state"]

            date_old = datetime.strptime(date_old, "%Y.%m.%d")
            deltas = date_now - date_old
            rrrr = rgx.sub('', str(deltas))
            rrrr = int(rrrr)
            if rrrr > int(AMOUNT_OF_DAYS_MORE):
                oldest_dates_more.append(
                    {"index": index_old, "days": rrrr, "state": state_old}
                )
        except:
            logging.warning('Skip. The date does not meet the requirements.')
except:
    logging.warning('Stage not passed!')

def ind(state):
  for ind_d in state:
      index_for_delete = ind_d["index"]
      d = requests.request('DELETE', ELASTIC_HOST + '/' +
                          str(index_for_delete), auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD))
      if re.findall('200', str(d)):
        d = "Index deleted"
        print("INFO " + "[" + str(datetime.now()) + "]" + " " + index_for_delete, d)

ind(oldest_dates_prod)
ind(oldest_dates_more)

logging.info('All specified indexes removed.')
