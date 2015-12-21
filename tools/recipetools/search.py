import numpy as np


def split_query(query):
    """Split the query into its component parts"""
    terms = query.lower().split(',')
    return [t.strip() for t in terms]


def find_matches(terms, vocab):
    """return a condensed dict with only the terms and their location"""
    term_dict = {}
    for term in terms:
        term_dict[term] = vocab.get(term, None)

    return term_dict


def found_not_found(terms):
    found = [k for k, v in terms.items() if v is not None]
    not_found = [k for k, v in terms.items() if v is None]

    return found, not_found


def find_recipe_with_ingredients(query, categories, model):

    terms = split_query(query)
    ngrams = {}
    for term in terms:
        ngrams[term] = [(r[0], model.ingredient_vocab.get(r[0], None))
                        for r in model.ingredient_ngram.search(term)
                        if term in r[0]]

    recipe_sets = {}
    for k, v in ngrams.items():
        recipe_sets[k] = set()
        # print(v)
        for i, ix in v:
            recipe_sets[k] = recipe_sets[k].union(set(model.ingredient_CV[:, ix].nonzero()[0]))

    if len(categories) > 0:
        for cat in categories:
            ix = model.category_vocab.get(cat, None)
            if ix is not None:
                recipe_sets[cat] = set(model.category_CV[:, ix].nonzero()[0])

    # term_dict = find_matches(terms, model.vocab)
    # matches = [set(model.bag[:, v].nonzero()[0]) for k, v in term_dict.items() if k is not None]
    match = np.array(list(set.intersection(*recipe_sets.values())), dtype=int)

    name_url = zip(np.array(model.components['names'])[match],
                   np.array(model.components['urls'])[match],
                   np.array(model.components['categories'])[match])

    return name_url  # , term_dict
