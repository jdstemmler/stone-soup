#!/usr/bin/env python

import datetime
import os
import sys
import time

import requests
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from gtools.settings import load_setting


def format_api_url(api_key):
    params = {}
    url = 'http://api.nytimes.com/svc/search/v2/articlesearch.json'
    fields = ['_id', 'headline', 'byline', 'document_type', 'web_url', 'pub_date', 'lead_paragraph', 'snippet']
    params = {'fq': 'type_of_material:("Recipe")',
              'api-key': api_key,
              'fl': ','.join(fields),
              'sort': 'newest',
              'page': 0}
    return url, params


def query_api(url, params):
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print('WARNING', response.status_code)
        return response
    else:
        return response


def get_number_of_results(response):
    json = getattr(response, 'json')
    if json() is None:
        return None
    n_results = json()['response']['meta']['hits']
    return n_results


def parse_api_response(response):
    json = getattr(response, 'json')
    if json is None:
        return None
    docs = json()['response']['docs']
    if not len(docs):
        return None
    return docs


def get_single_query(key, tab, page=0):
    url, params = format_api_url(key)
    params['page'] = page

    response = query_api(url, params)
    docs = parse_api_response(response)
    insert_into_mongo(tab, docs)
    return docs


def paginate(key, tab, sleep=5, **kwargs):
    prior_tab_len = tab.find().count()
    url, params = format_api_url(key)
    params.update(kwargs)
    response = query_api(url, params)
    #print(response.url)
    while response.status_code == 200:
        print("Getting Page {}".format(params['page']))
        docs = parse_api_response(response)
        if docs is None:
            break
        insert_into_mongo(tab, docs)
        params['page'] += 1
        time.sleep(sleep)
        response = query_api(url, params)
    final_tab_len = tab.find().count()
    print("Inserted {} new metadata rows".format(final_tab_len - prior_tab_len))
    print("Current Table Size: {} entries\n".format(final_tab_len))


def paginate_by_date(key, tab, start_date='19000101', init_window=0):
    window = datetime.timedelta(days=init_window)
    dfmt = '%Y%m%d'
    start = datetime.datetime.strptime(start_date, dfmt)
    end = start + window
    print("Starting with {}".format(start))
    print("Window Size of {} Days".format(window.days))
    while start <= datetime.datetime.today():
        # test the window. can get max 1000 hits
        url, params = format_api_url(key)
        params.update(begin_date=start.strftime(dfmt),
                      end_date=end.strftime(dfmt))
        response = query_api(url, params)

        while get_number_of_results(response) > 1000:
            window = datetime.timedelta(days=(window / 2).days)
            print("Reducing Window to {} Days".format(window.days))
            end = start + window
            url, params = format_api_url(key)
            params.update(begin_date=start.strftime(dfmt),
                          end_date=end.strftime(dfmt))
            response = query_api(url, params)

        paginate(key, tab,
                 begin_date=start.strftime(dfmt),
                 end_date=end.strftime(dfmt))
        start += window
        print("New Start Date: {}".format(start))
        print("Window: {} Days".format(window.days))
        time.sleep(30)

    # for i in range(20):
    #     startd = endd - datetime.timedelta(days=window)
    #
    #     st = startd.strftime('%Y%m%d')
    #     en = endd.strftime('%Y%m%d')
    #     print("{} to {}".format(st, en))
    #
    #     paginate(key, tab, begin_date=st, end_date=en)
    #
    #     endd -= datetime.timedelta(days=window+1)
    #
    #     time.sleep(30)


def insert_into_mongo(table, rows):
    for row in rows:
        try:
            table.insert_one(row)
        except DuplicateKeyError:
            continue


def main(start_date):
    client = MongoClient()
    db = client['capstone-database']
    table = db['recipe-metadata']

    settings_file = os.path.join(os.getenv("CAPSTONE_DIR"), 'settings.json')
    nyt_api_key = load_setting(settings_file, 'NYT_API_KEY')

    paginate_by_date(nyt_api_key, table, start_date=start_date, init_window=1000)

    client.close()


if __name__ == "__main__":
    start_date = datetime.date.today().strftime('%Y%m%d')

    if len(sys.argv) > 1:
        start_date = sys.argv[-1]

    main(start_date=start_date)
