def tokenizer(x):
    return x.lower().split(';')


def join_ingredients(x):
    return ';'.join(x['ingredient_names']).lower()