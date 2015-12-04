#!/usr/bin/env python

import os
import time
import numpy as np
import requests
from pymongo import MongoClient


def get_recipes(urls, tab):
    n_urls = len(urls)
    for i, url in enumerate(urls):
        url = url.strip()
        print('getting {}'.format(url))
        if not tab.find({'web_url': url}).count():
            print('url not in database. fetching.')
            html = requests.get(url)
            if html.status_code != 200:
                print('WARNING! {}'.format(html.status_code))
                # tab.insert_one({'web_url': url, 'content': 'None'})
            elif html.status_code == 200:
                tab.insert_one({'web_url': url, 'content': html.content})

            time.sleep(4. * np.random.random_sample() + 3.)

        elif tab.find({'web_url': url}).count():
            print('already have recipe')

        print("Processed {} out of {} recipes\n".format(i, n_urls))

        if i % 100 == 0:
            print("Taking a break...\n")
            time.sleep(60)

if __name__ == "__main__":

    # get a list of the urls to work on
    url_file = os.path.join(os.getenv("CAPSTONE_DIR"), 'data/nyt_urls.txt')
    with open(url_file, 'r') as f:
        urls = [line for line in f]

    client = MongoClient()
    db = client['capstone-project']
    tab = db['nyt_recipes']

    get_recipes(urls, tab)

    client.close()
