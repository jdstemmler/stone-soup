#!/usr/bin/env python

import os
import sys
from pymongo import MongoClient

from gtools.settings import load_setting


def main(fileout):

    # set the location of the settings file
    settings_file = os.path.join(os.getenv("CAPSTONE_DIR"), 'settings.json')

    # set some settings
    database = load_setting(settings_file, 'db_name')  # name of mongodb database

    # open the connection to the database, get the table
    client = MongoClient()
    db = client[database]
    table = db['nyt-recipe-metadata']

    # get all results in the table
    results = table.find()
    with open(fileout, 'w') as f:
        for result in results:
            f.write(result['web_url'] + '\n')


if __name__ == "__main__":
    file_out = 'nyt_urls.txt'
    if len(sys.argv) > 1:
        file_out = sys.argv[0]

    outfile = os.path.join(os.getenv("CAPSTONE_DIR"), 'data', file_out)

    main(outfile)
