#!/usr/bin/env python

from bs4 import BeautifulSoup
from collections import OrderedDict


class NYTimesCooking:
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
        """Get the name of the recipe"""
        try:
            recipe_name = self.soup.find('h1', {'class': 'recipe-title title name'}).text.strip()
        except AttributeError:
            recipe_name = ''

        self.recipe_name = recipe_name

    def _get_author(self):
        """Get the author of the recipe"""
        try:
            recipe_author = self.soup.find('span', {'class': 'byline-name', 'itemprop': 'author'}).text.strip()
        except AttributeError:
            recipe_author = ''

        self.recipe_author = recipe_author

    def _get_time_yield(self):
        """Get the cooking time and the yield of the recipe"""
        try:
            time_yield = [ty.text.strip()
                          for ty in self.soup.find('ul', {'class': 'recipe-time-yield'})
                          .findAll('li')]
        except AttributeError:
            time_yield = []

        self.time_yield = time_yield

    def _get_ingredients(self):
        """Get the ingredients"""

        ingredient_wrap = self.soup.find('section', {'class': 'recipe-ingredients-wrap'})

        try:
            headers = [t.text.strip().replace('.', '') for t in ingredient_wrap.findAll('h4', {'class': 'part-name'})]
        except AttributeError:
            headers = []

        if not len(headers):
            headers = ['main']

        try:
            full = [[t.text.strip().replace('\n', ' ')
                     for t in l.findAll('li', {'itemprop': 'recipeIngredient'})
                     ]
                    for l in ingredient_wrap.findAll('ul', {'class': 'recipe-ingredients'})
                    ][:len(headers)]

            name = [[t.text.strip().replace('\n', ' ')
                     for t in l.findAll('span', {'itemprop': 'name'})
                     ]
                    for l in ingredient_wrap.findAll('ul', {'class': 'recipe-ingredients'})
                    ][:len(headers)]

        except AttributeError:
            full = []
            name = []
            # headers = []

        self.ingredient_headers = headers
        self.ingredients_full = full
        self.ingredients_name = name
        self.ingredient_dict = OrderedDict()
        for h, i in zip(headers, full):
            self.ingredient_dict[h] = i

    def _get_instructions(self):
        """Get the recipe instructions"""
        try:
            directions = [l.text
                          for l in self.soup.find('ol', {'class': 'recipe-steps'})
                          .findAll('li')]
        except AttributeError:
            directions = []

        self.directions = directions

    def _get_description(self):
        """Get the recipe description"""
        try:
            description = self.soup.find('div', {'itemprop': 'description'}).text.strip()
        except AttributeError:
            description = ''

        self.description = description

    def _get_notes(self):
        """Get any notes from the recipe"""
        try:
            notes = [l.text.strip()
                     for l in self.soup.find('ul', {'class': 'recipe-notes'})
                     .findAll('li')]
        except AttributeError:
            notes = []

        self.notes = notes

    def _get_topics(self):
        """Get associated recipe topics"""
        try:
            categories = [a.text
                          for a in self.soup.find('p', {'class': 'special-diets tag-block'})
                          .findAll('a')]
        except AttributeError:
            categories = []

        self.categories = categories

    def _get_nutrition(self):
        """Get nutrition information from the recipe"""
        try:
            servings = self.soup.find('div', {'class': 'nutrition-tooltip'}).find('h5').text.strip()
            nutrition = self.soup.find('span', {'class': 'description', 'itemprop': 'nutrition'}).text.strip()
        except AttributeError:
            servings, nutrition = '', ''

        self.servings = servings
        self.nutrition = nutrition

    def _get_image_url(self):
        """Get the URL for an attached image, if available"""
        try:
            img_url = self.soup.find('div', {'class': 'recipe-intro'}).find('img')['src']
        except (AttributeError, TypeError):
            img_url = None

        self.img_url = img_url

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


class FoodNetwork:
    def __init__(self):
        pass
