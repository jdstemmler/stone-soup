import numpy as np
from sklearn.cluster import KMeans

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


def find_recipe_with_ingredients(query, categories, features, topics):

    terms = split_query(query)
    ngrams = {}
    for term in terms:
        ngrams[term] = [(r[0], features['ingredient_vocab'].get(r[0], None))
                        for r in features['ingredient_ngram'].search(term)
                        if term in r[0] and ('broth' not in r[0] and 'stock' not in r[0])]

    recipe_sets = {}
    for k, v in ngrams.items():
        recipe_sets[k] = set()
        # print(v)
        for i, ix in v:
            recipe_sets[k] = recipe_sets[k].union(set(features['ingredient_CV'][:, ix].nonzero()[0]))

    if len(categories) > 0:
        for cat in categories:
            ix = features['category_vocab'].get(cat, None)
            if ix is not None:
                recipe_sets[cat] = set(features['category_CV'][:, ix].nonzero()[0])

    # term_dict = find_matches(terms, model.vocab)
    # matches = [set(model.bag[:, v].nonzero()[0]) for k, v in term_dict.items() if k is not None]
    match = np.array(list(set.intersection(*recipe_sets.values())), dtype=int)

    if len(match) <= 12:
        final_match = match
    else:
        recipe_topics = topics['W'][match, :]
        km = KMeans(n_clusters=4)
        km.fit(recipe_topics)
        distances = km.transform(recipe_topics)
        sorted_recipes_per_topic = np.argsort(distances, axis=0).ravel()
        final_set = set()
        ix = 0

        while len(final_set) < 12:
            final_set.add(match[sorted_recipes_per_topic[ix]])
            ix += 1
            if ix > 40:
                break

        final_match = np.array(list(final_set))

    out_array = zip(np.array(features['components']['names'])[final_match],
                    np.array(features['components']['urls'])[final_match],
                    np.array(features['components']['categories'])[final_match],
                    np.array(features['components']['img_url'])[final_match])

    return out_array
