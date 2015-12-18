#!/usr/bin/env python

from pymongo import MongoClient
from recipetools.settings import load_setting
from recipetools.text import tokenizer, join_ingredients
from sklearn.feature_extraction.text import CountVectorizer
import os
import pickle


def iter_table(recipe_table):
    params = {'_id': 0, 'ingredient_names': 1, 'name': 1, 'web_url': 1}
    result = recipe_table.find({}, params)

    # since result is an iterator, I only get one pass at the data. For loop it is!
    ingredients = []
    names = []
    urls = []

    for recipe in result:
        ingredients.append(join_ingredients(recipe))
        names.append(recipe['name'])
        urls.append(recipe['web_url'])

    return {'ingredients': ingredients, 'names': names, 'urls': urls}


def make_bag_of_ingredients(ingredients):
    cv = CountVectorizer(tokenizer=tokenizer)
    wc = cv.fit_transform(ingredients)
    vocab = cv.vocabulary_

    return wc, vocab


def pickler(obj, pkl):
    with open(pkl, 'wb') as f:
        pickle.dump(obj, f)


def main(recipe_table):
    components = iter_table(recipe_table)
    wc, vocab = make_bag_of_ingredients(components['ingredients'])

    pickler(wc, bag_pickle)
    pickler(vocab, vocab_pickle)
    pickler(components, comp_pickle)


if __name__ == "__main__":

    # set the location of the settings file
    cap_dir = os.getenv("CAPSTONE_DIR")
    settings_file = os.path.join(cap_dir, 'settings', 'project_settings.json')

    # load in the tables to use
    database = load_setting(settings_file, 'db_name')  # name of mongodb database
    table = load_setting(settings_file, 'nyt_recipe_extracted')

    # connect to the client and database/collection
    client = MongoClient()
    db = client[database]
    tab = db[table]

    # name the pickles
    bag_pickle = os.path.join(cap_dir, 'data/pickles/bag_of_ingredients.pkl')
    vocab_pickle = os.path.join(cap_dir, 'data/pickles/vocabulary.pkl')
    comp_pickle = os.path.join(cap_dir, 'data/pickles/recipe_components.pkl')

    main(tab)
