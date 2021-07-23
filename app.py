# -*- coding: utf-8 -*-

from datetime import *
from dateutil.parser import *
import requests
import json
import re
import os
import logging
import urllib3

ELASTIC_HOST = os.getenv("ELASTIC_HOST", "http://elastic:9200")
ELASTIC_USERNAME = os.getenv("ELASTIC_USERNAME", "elastic")
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD", "elastic")
SSL_CERTIFICATE_VERIFY = os.getenv("SSL_CERTIFICATE_VERIFY", "true") == 'true'

AMOUNT_OF_DAYS = os.environ.get("AMOUNT_OF_DAYS")
GET_INDICES = '/_cat/indices?format=json&pretty=true'

index_array = []
index_array2 = []
only_date = []
date_and_index_more = []
oldest_dates_last = []
oldest_dates_other = []
oldest_dates_more = []
indexes_patterns = []

urllib3.disable_warnings()

logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


def indexes_patterns_from_env(index_env):
    pattern_index_name = r'(\W-\w+-\W|\W-\w+-\w+-\W|\W)='
    pattern_index_numbers = r'=(\d+)'
    index_name = re.findall(pattern_index_name, index_env)
    index_numbers = re.findall(pattern_index_numbers, index_env)
    i = len(index_name)
    for i in range(0, i):
        rgxMount = re.compile(
            '\*-|-\*'
        )

        if index_name[i] == '*':
            index_name[i] = "other"
        else:
            index_name[i] = rgxMount.sub('', index_name[i])

        indexes_patterns.append(
            {"name": index_name[i], "amount": index_numbers[i]})
    return indexes_patterns


indexes_patterns_from_env(AMOUNT_OF_DAYS)

r = requests.request('GET', ELASTIC_HOST + GET_INDICES, auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD),
                     verify=SSL_CERTIFICATE_VERIFY)

pretty_json = r.json()
dumped_json = json.dumps(pretty_json)
ready_json = json.loads(dumped_json)

for indexes in ready_json:
    index_array.append(
        indexes["index"]
    )
index_array.sort(reverse=True)

for indexes in index_array:
    indexs = indexes
    index_array2.append(
        {"index": indexs}
    )

date_now = datetime.now()
date_now = ('{:%Y.%m.%d}'.format(date_now))
date_now = parse(date_now, parserinfo=None)


for key in index_array2:
    index = key["index"]
    if re.search('\d\d\d\d.\d\d.\d\d ?', index):
        only_date.append(
            {"index": index}
        )

for keys in only_date:
    index = keys["index"]
    allmatches = re.findall(r'\d\d\d\d.\d\d.\d\d', index)

    for i in range(0, len(allmatches)):
        if allmatches[i]:
            date_and_index_more.append(
                {"index": index, "date": allmatches[0]}
            )

rgx = re.compile(' days, 0:00:00| day, 0:00:00| 0:00:00')

try:
    for date_olds in date_and_index_more:
        try:
            date_old = date_olds["date"]
            index_old = date_olds["index"]
            date_old = datetime.strptime(date_old, "%Y.%m.%d")
            deltas = date_now - date_old
            re_sub = rgx.sub('', str(deltas))
            re_sub = int(re_sub)
            oldest_dates_more.append(
                {"index": index_old, "days": re_sub}
            )
        except:
            logging.info('Skip. The date does not meet the requirements.')
except:
    logging.warning('Stage not passed!')

for ii in range(len(oldest_dates_more)):
    for i in indexes_patterns:
        serch_pattern = re.compile(i["name"])
        for keys in enumerate(oldest_dates_more):
            number_in_array = keys[0]
            index = keys[1]["index"]
            days = keys[1]["days"]
            matches = serch_pattern.findall(index)

            if matches:
                oldest_dates_last.append(
                    {"index": index, "days": days, "state": i["name"]}
                )
                del oldest_dates_more[number_in_array]

for keys in oldest_dates_last:
    for i in indexes_patterns:
        name = i["name"]
        state = keys["state"]
        days = keys["days"]
        index_for_delete = keys["index"]
        if name == state and int(days) > int(i["amount"]):
            d = requests.request('DELETE', ELASTIC_HOST + '/' +
                                 str(index_for_delete), auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD),
                                 verify=SSL_CERTIFICATE_VERIFY)
            if re.findall('200', str(d)):
                d = "Index deleted"
                print("INFO " + "   [" + str(datetime.now()
                                             ) + "]" + " " + index_for_delete, d)

for i in indexes_patterns:
    for keys in enumerate(oldest_dates_more):
        serch_pattern = re.compile("other")
        name = i["name"]
        days = keys[1]["days"]
        index_for_delete = keys[1]["index"]
        if name == "other" and int(days) > int(i["amount"]):
            d = requests.request('DELETE', ELASTIC_HOST + '/' +
                                 str(index_for_delete), auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD),
                                 verify=SSL_CERTIFICATE_VERIFY)
            if re.findall('200', str(d)):
                d = "Index deleted"
                print("INFO " + "   [" + str(datetime.now()
                                             ) + "]" + " " + index_for_delete, d)

logging.info('All specified indexes removed.')
