import numpy as np


def split_query(query):
    terms = query.lower().split(',')
    return [t.strip() for t in terms]


def find_recipe_with_ingredients(query, wc, vocab, components):

    terms = split_query(query)

    found = []
    not_found = []
    matched_recipes = []

    for term in terms:
        if term not in vocab:
            not_found.append(term)
        elif term in vocab:
            found.append(term)
            term_ix = vocab[term]
            matched_recipes.append(set(wc[:, term_ix].nonzero()[0]))

    match = np.array(list(set.intersection(*matched_recipes))).astype(int)

    name_url = zip(np.array(components['names'])[match],
                   np.array(components['urls'])[match])

    return name_url, found, not_found
