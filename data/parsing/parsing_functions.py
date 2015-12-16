from gtools.parsers import NYTimesCooking
import requests
from pprint import pprint


def dict_from_html(content, parser):
    recipe = parser(content)

    result = dict()
    result['name'] = recipe.recipe_name
    result['author'] = recipe.recipe_author
    result['description'] = recipe.description
    result['ingredients'] = recipe.ingredient_dict
    result['ingredient_names'] = [item for subl in recipe.ingredients_name for item in subl]
    result['directions'] = recipe.directions
    result['categories'] = recipe.categories

    return result


if __name__ == "__main__":
    url = "http://cooking.nytimes.com/recipes/1017870-little-onion-tarts-with-gorgonzola-and-walnuts"
    html = requests.get(url)
    out = dict_from_html(html.content, NYTimesCooking)
    pprint(out)
