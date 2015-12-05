#!/usr/bin/env python

import os
import time
import numpy as np
import requests
from pymongo import MongoClient


def get_single_recipe(url, verbose=True):
    """Get a single recipe from a URL"""

    # fetch the url
    html = requests.get(url)

    # check status code for successful result
    if html.status_code != 200:
        if verbose:
            print("Warning: Status Code {}".format(html.status_code))
        return None  # return None if result is not successful
    elif html.status_code == 200:
        return {'web_url': url, 'content': html.content}  # return the url and content if successful


def get_recipes_from_list(urls, tab, verbose=False):
    """Get all recipes from a list of URLs"""

    n_urls = len(urls)  # length of the url list
    for i, url in enumerate(urls):
        url = url.strip()  # strip \n chars
        if verbose: print('getting {}'.format(url))

        # look for an existing entry in the database for the recipe
        if not tab.find({'web_url': url}).count():
            # no matches in the database, fetch the result
            if verbose: print('url not in database. fetching.')

            content = get_single_recipe(url, verbose)
            if content is not None:
                # insert into the db if the content is not None
                tab.insert_one(content)

            # sleep a few seconds before hitting the site again for another recipe
            time.sleep(4. * np.random.random_sample() + 3.)

        elif tab.find({'web_url': url}).count():
            # found a match in the database, skip it.
            if verbose: print('already have recipe')

        # status message for output
        if verbose: print("Processed {} out of {} recipes\n".format(i+1, n_urls))

        # take a longer break every 100 recipes
        if i % 100 == 0:
            if verbose: print("Taking a break...\n")
            time.sleep(60)

if __name__ == "__main__":

    # get a list of the urls to work on
    url_file = os.path.join(os.getenv("CAPSTONE_DIR"), 'data/nyt_urls.txt')
    with open(url_file, 'r') as f:
        urls = [line for line in f]

    # connect to the client and database/collection
    client = MongoClient()
    db = client['capstone-project']
    tab = db['nyt_recipes']

    # get all the recipes from the url list
    get_recipes_from_list(urls, tab)

    client.close()
