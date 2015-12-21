#!/usr/bin/env python

from pymongo import MongoClient
from collections import defaultdict
from ngram import NGram
from recipetools.settings import load_setting
from recipetools.text import tokenizer, join_ingredients, join_list

from sklearn.feature_extraction.text import CountVectorizer
import os
import pickle


def iter_table(recipe_table):
    params = {'_id': 0, 'ingredient_names': 1, 'name': 1,
              'web_url': 1, 'categories': 1, 'directions': 1}
    result = recipe_table.find({}, params)

    # since result is an iterator, I only get one pass at the data. For loop it is!
    output = defaultdict(list)

    for recipe in result:
        for k, v in recipe.items():
            if k in ("ingredient_names", "categories"):
                output[k].append(join_list(v))
            else:
                output[k].append(v)

    output['ingredients'] = output.pop('ingredient_names')
    output['names'] = output.pop('name')
    output['urls'] = output.pop('web_url')

    return output


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
    comp, compv = make_bag_of_ingredients(components['categories'])

    ng = NGram(vocab.keys())

    #  model_parts = 'ingredient_CV, ingredient_vocab, category_CV, category_vocab, components'

    model = {'ingredient_CV': wc,
             'ingredient_vocab': vocab,
             'ingredient_ngram': ng,
             'category_CV': comp,
             'category_vocab': compv,
             'components': components
             }

    pickler(model, model_pickle)

    # pickler(wc, bag_pickle)
    # pickler(vocab, vocab_pickle)
    # pickler(components, comp_pickle)


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
    # bag_pickle = os.path.join(cap_dir, 'data/pickles/bag_of_ingredients.pkl')
    # vocab_pickle = os.path.join(cap_dir, 'data/pickles/vocabulary.pkl')
    # comp_pickle = os.path.join(cap_dir, 'data/pickles/recipe_components.pkl')
    model_pickle = os.path.join(cap_dir, 'data/pickles/model.pkl')

    main(tab)
