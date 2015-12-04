#!/usr/bin/env python

import os
import time
import requests
from pymongo import MongoClient


def get_recipes(urls, tab):
    for url in urls:
        print('getting {}'.format(url))
        if not len(tab.find({'web_url': url})):
            print('url not in database. scraping.')
            html = requests.get(url)
            if html.status_code != 200:
                print('WARNING! {}'.format(html.status_code))
                tab.insert_one({'web_url': url, 'content': 'None'})
            elif html.status_code == 200:
                tab.insert_one({'web_url': url, 'content': html.content})
        time.sleep(5)


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
