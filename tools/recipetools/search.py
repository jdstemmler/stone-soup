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


def find_recipe_with_ingredients(query, model):

    terms = split_query(query)

    term_dict = find_matches(terms, model.vocab)
    matches = [set(model.bag[:, v].nonzero()[0]) for k, v in term_dict.items() if k is not None]
    match = np.array(list(set.intersection(*matches)), dtype=int)

    name_url = zip(np.array(model.components['names'])[match],
                   np.array(model.components['urls'])[match])

    return name_url, term_dict
