from bs4 import BeautifulSoup
from collections import OrderedDict


class BaseParser:
    """Class for parsing recipes from cooking.nytimes.com"""

    def __init__(self, content):

        self.content = content
        self.soup = BeautifulSoup(content, "html.parser")

        self._get_name()
        self._get_author()
        self._get_time_yield()
        self._get_description()
        self._get_ingredients()
        self._get_instructions()
        self._get_topics()
        self._get_notes()
        self._get_nutrition()
        self._get_image_url()

    def _get_name(self):
        self.recipe_name = None

    def _get_author(self):
        self.recipe_author = None

    def _get_time_yield(self):
        self.time_yield = None

    def _get_description(self):
        self.description = None

    def _get_ingredients(self):
        self.ingredient_headers = None
        self.ingredients_full = None
        self.ingredients_name = None
        self.ingredient_dict = OrderedDict()
        for h, i in zip(self.ingredient_headers, self.ingredients_full):
            self.ingredient_dict[h] = i

    def _get_instructions(self):
        self.directions = None

    def _get_topics(self):
        self.categories = None

    def _get_notes(self):
        self.notes = None

    def _get_nutrition(self):
        self.servings = None
        self.nutrition = None

    def _get_image_url(self):
        self.img_url = None

    def to_dict(self):
        result = dict()

        result['name'] = self.recipe_name
        result['author'] = self.recipe_author
        result['description'] = self.description
        result['ingredients'] = self.ingredient_dict
        result['ingredient_names'] = [item for subl in self.ingredients_name for item in subl]
        result['directions'] = self.directions
        result['categories'] = self.categories

        return result

    def __repr__(self):
            """Pretty Formatting of the recipe"""
            ingredient_string = '\n\n'.join(["{}\n{}".format(k.upper(), '  '+'\n  '.join(v))
                                             if k != 'main'
                                             else '\n'.join(v)
                                             for k, v in self.ingredient_dict.items()])+'\n'
            strings = [
                "Name".upper(),
                "----",
                "{}\n".format(self.recipe_name),
                "Author".upper(),
                "------",
                "{}\n".format(self.recipe_author),
                "Description".upper(),
                "-----------",
                "{}\n".format(self.description),
                "Ingredients".upper(),
                "-----------",
                # "\n".join(self.ingredients_full) + "\n",
                ingredient_string,
                "Directions".upper(),
                "----------",
                "\n\n".join(self.directions) + "\n",
                "Notes".upper(),
                "-----",
                "\n".join(self.notes),
                "Nutrition Information".upper(),
                "---------------------",
                "\n  ".join([self.servings] + self.nutrition.split(';'))
            ]

            return '\n'.join(strings)
