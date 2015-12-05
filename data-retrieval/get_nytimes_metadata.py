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
    """Format the api call for getting recipes given an api key"""
    url = 'http://api.nytimes.com/svc/search/v2/articlesearch.json'
    fields = ['_id', 'headline', 'byline', 'document_type', 'web_url', 'pub_date', 'lead_paragraph', 'snippet']
    params = {'fq': 'type_of_material:("Recipe")',
              'api-key': api_key,
              'fl': ','.join(fields),
              'sort': 'newest',
              'page': 0}
    return url, params


def query_api(url, params):
    """send the URL and the parameters to the api, return the response"""
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print('WARNING', response.status_code)
        return response
    else:
        return response


def get_number_of_results(response):
    """get the number of results returned by the api query"""
    json = getattr(response, 'json')
    if json() is None:
        return None
    n_results = json()['response']['meta']['hits']
    return n_results


def parse_api_response(response):
    """parse the api query to get out the documents"""
    json = getattr(response, 'json')
    if json is None:
        return None
    docs = json()['response']['docs']
    if not len(docs):
        return None
    return docs


def insert_into_mongo(table, rows):
    """insert a list of rows into mongo, checking that the rows don't already exist"""
    for row in rows:
        try:
            table.insert_one(row)
        except DuplicateKeyError:
            continue


def get_single_query(key, tab, page=0):
    """send the results of a single query (one page) into the mongoDB"""
    url, params = format_api_url(key)
    params['page'] = page

    response = query_api(url, params)
    docs = parse_api_response(response)
    insert_into_mongo(tab, docs)
    return docs


def paginate(key, tab, sleep=5, verbose=True, **kwargs):
    """paginate through the api results while there are still documents"""

    prior_tab_len = tab.find().count()  # number of current docs prior to pagination

    # get the first page of results
    url, params = format_api_url(key)
    params.update(kwargs)
    response = query_api(url, params)

    while response.status_code == 200:
        # if a valid response, check for documents
        if verbose: print("Getting Page {}".format(params['page']))
        docs = parse_api_response(response)
        if docs is None:
            # break out if no documents
            break

        # if we have documents, insert them into mongo
        insert_into_mongo(tab, docs)

        params['page'] += 1  # increment page number
        time.sleep(sleep)    # take a small break before next query

        # get the next response
        response = query_api(url, params)

    final_tab_len = tab.find().count()  # number of docs after pagination

    if verbose:
        print("Inserted {} new metadata rows".format(final_tab_len - prior_tab_len))
        print("Current Table Size: {} entries\n".format(final_tab_len))


def paginate_by_date(key, tab, start_date='19000101', init_window=0, verbose=True):
    """does most of the heaving lifting, paging through a date range
    Inputs:
        :param key: the api key for reaching NYTimes
        :param tab: the table to insert the documents into
        :param start_date: the date to start searching
        :param init_window: size of window (in days) to start searching
        :param verbose:

    """
    # initialize date settings
    window = datetime.timedelta(days=init_window)
    dfmt = '%Y%m%d'
    start = datetime.datetime.strptime(start_date, dfmt)
    end = start + window
    if verbose:  # print some information
        print("Starting with {}".format(start))
        print("End Date: {}".format(end))
        print("Window Size of {} Days\n".format(window.days))

    # don't query for date ranges after the current date and time
    while start <= datetime.datetime.today():

        # send an ititial query to the api and get a response
        url, params = format_api_url(key)
        params.update(begin_date=start.strftime(dfmt),
                      end_date=end.strftime(dfmt))
        response = query_api(url, params)

        # test to see how many total results. can only paginate up to 1000 results.
        while get_number_of_results(response) > 1000:
            # if more than 1000 results, cut the window in two
            window = datetime.timedelta(days=(window / 2).days)
            if verbose: print("Reducing Window to {} Days".format(window.days))

            # set the new end date
            end = start + window
            if verbose: print("New End Date: {}\n".format(end))

            # perform the query with the new dates and check number of results
            url, params = format_api_url(key)
            params.update(begin_date=start.strftime(dfmt),
                          end_date=end.strftime(dfmt))
            response = query_api(url, params)

        # we can now paginate and get all the results
        paginate(key, tab, verbose=verbose,
                 begin_date=start.strftime(dfmt),
                 end_date=end.strftime(dfmt)
                 )

        # set the new start and end dates
        start += window
        end = start + window

        if verbose:
            print("New Start Date: {}".format(start))
            print("New End Date: {}".format(end))
            print("Window: {} Days\n".format(window.days))

        time.sleep(10)  # take a short nap

    print("Complete")


def main(start_date):
    """called by the script to do the processing"""

    # set the location of the settings file
    settings_file = os.path.join(os.getenv("CAPSTONE_DIR"), 'settings.json')

    # set some settings
    database = load_setting(settings_file, 'db_name')  # name of mongodb database
    nyt_api_key = load_setting(settings_file, 'NYT_API_KEY')  #NYTimes API Key

    # open the connection to the database, get the table
    client = MongoClient()
    db = client[database]
    table = db['recipe-metadata']

    # paginate through the search results
    # starting at the start date specified at runtime and a 2000 day initial window
    paginate_by_date(nyt_api_key, table, start_date=start_date, init_window=2000)

    # close the connection to the client
    client.close()


if __name__ == "__main__":
    # set the start date to be today
    start_date = datetime.date.today().strftime('%Y%m%d')

    # check for additional inputs. If present, set the new start date
    if len(sys.argv) > 1:
        start_date = sys.argv[-1]

    # run main, passing in the start date
    main(start_date=start_date)
