from recipetools.parsers import NYTimesCooking
from recipetools.settings import load_setting
from pymongo import MongoClient
import os


def parse_and_insert(recipe, table):
    html = recipe['content']

    try:
        parsed_recipe = NYTimesCooking(html).to_dict()
        parsed_recipe.update({'web_url': recipe['web_url']})
    except:
        print("recipe could not be parsed")
        return 0

    table.insert_one(parsed_recipe)
    return 1


def main(i, o):

    to_parse = i.find()
    success = 0
    for ix, recipe in enumerate(to_parse):
        s = parse_and_insert(recipe, o)
        success += s

    print("FINISHED. Successfully parsed {} of out {} recipes".format(success, ix))



if __name__ == "__main__":

    # set the location of the settings file
    cap_dir = os.getenv("CAPSTONE_DIR")
    settings_file = os.path.join(cap_dir, 'settings', 'project_settings.json')

    database = load_setting(settings_file, 'db_name')  # name of mongodb database
    in_table = load_setting(settings_file, 'nyt_recipe_html')
    out_table = load_setting(settings_file, 'nyt_recipe_extracted')

    # connect to the client and database/collection
    client = MongoClient()
    db = client[database]
    itab = db[in_table]
    otab = db[out_table]

    main(itab, otab)
