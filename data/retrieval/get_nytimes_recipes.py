#!/usr/bin/env python

import os
import sys
import time
import numpy as np
import requests
from pymongo import MongoClient

from recipetools.settings import load_setting


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


def get_recipes_from_metadata(meta, recipe, verbose=False):
    metadata = meta.find({}, {'web_url': 1})
    n_urls = metadata.count()

    for i, record in metadata:
        url = record['web_url'].strip()
        if verbose: print('getting {}'.format(url))

        if not recipe.find({'web_url': url}).count():
            content = get_single_recipe(url, verbose)
            if content is not None:
                recipe.insert_one(content)
            elif content is None:
                meta.drop_index(record['_id'])

            time.sleep(4. * np.random.random_sample() + 3.)
        elif recipe.find({'web_url': url}).count():
            if verbose: print('already have the recipe')

        # status message for output
        if verbose: print("Processed {} out of {} recipes\n".format(i+1, n_urls))

        # take a longer break every 100 recipes
        if i % 100 == 0:
            if verbose: print("Taking a break...\n")
            time.sleep(60)


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

    # set the location of the settings file
    cap_dir = os.getenv("CAPSTONE_DIR")
    settings_file = os.path.join(cap_dir, 'settings', 'project_settings.json')
    database = load_setting(settings_file, 'db_name')  # name of mongodb database
    recipe_tab = load_setting(settings_file, 'nyt_recipe_html')
    metadata_tab = load_setting(settings_file, 'nyt-recipe-metadata')
    url_filename = load_setting(settings_file, 'nyt_url_file')

    # get a list of the urls to work on

    url_file = os.path.join(cap_dir, 'data', url_filename)
    with open(url_file, 'r') as f:
        urls = [line for line in f]

    # connect to the client and database/collection
    client = MongoClient()
    db = client[database]
    rtab = db[recipe_tab]
    mtab = db[metadata_tab]

    get_recipes_from_metadata(mtab, rtab, verbose=True)

    # get all the recipes from the url list
    # if '--verbose' in sys.argv:
    #     get_recipes_from_list(urls, tab, verbose=True)
    # else:
    #     get_recipes_from_list(urls, tab)

    client.close()
