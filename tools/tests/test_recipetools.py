import unittest

from sklearn.feature_extraction.text import CountVectorizer
from collections import namedtuple

from recipetools.search import split_query, find_recipe_with_ingredients, found_not_found
from recipetools.text import tokenizer, join_ingredients
from recipetools.parsers import NYTimesCooking


class SearchTest(unittest.TestCase):

    def setUp(self):
        ingredients = [
            ['Spam', 'bacon', 'eggs'],
            ['ham', 'eggs', 'Bacon', 'French bread'],
            ['bacon', 'olives', 'Tomato Juice', 'Tabasco']
        ]

        names = [
            ['Spamtastic Breakfast'],
            ['Eggcellent Breakfast'],
            ['Boring Bloody Mary']
        ]

        web_urls = [
            ['www.example.com/spamtastic-breakfast'],
            ['www.example.com/eggcellent-breakfast'],
            ['www.example.com/boring-bloody-mary']
        ]

        self.recipes = [{'ingredient_names': i, 'names': n, 'web_url': u}
                        for i, n, u in zip(ingredients, names, web_urls)]

        self.query = 'Bacon, eggs'

        self.joined_ingredients = [join_ingredients(x) for x in self.recipes]
        self.tokenized_ingredients = [tokenizer(x) for x in self.joined_ingredients]

        cv = CountVectorizer(tokenizer=tokenizer)
        wc = cv.fit_transform(self.joined_ingredients)

        self.wc = wc
        self.vocab = cv.vocabulary_
        components = {'ingredients': ingredients, 'names': names, 'urls': web_urls}

        ModelData = namedtuple('Model', 'bag, vocab, components')

        self.model = ModelData(bag=self.wc, vocab=self.vocab, components=components)

    def test_query_split(self):
        split = split_query(self.query)
        self.assertEqual(split, ['bacon', 'eggs'])

    def test_join(self):
        expected = [
            'spam;bacon;eggs',
            'ham;eggs;bacon;french bread',
            'bacon;olives;tomato juice;tabasco'
        ]
        self.assertEqual(self.joined_ingredients, expected)

    def test_tokenize(self):
        expected = [
            ['spam', 'bacon', 'eggs'],
            ['ham', 'eggs', 'bacon', 'french bread'],
            ['bacon', 'olives', 'tomato juice', 'tabasco']
        ]
        self.assertEqual(self.tokenized_ingredients, expected)

    def test_search(self):
        results, terms = find_recipe_with_ingredients(self.query, self.model)
        fnd, nfnd = found_not_found(terms)
        for name, url in results:
            self.assertTrue(name in self.model.components['names'])
            self.assertTrue(url in self.model.components['urls'])

        excluded = 'Boring Bloody Mary'
        self.assertTrue(excluded not in zip(*results))

    def tearDown(self):
        pass


class NYTParsingTest(unittest.TestCase):

    def setUp(self):
        # self.url = 'http://cooking.nytimes.com/recipes/8096-grilled-pineapple-salsa'
        # html = requests.get(self.url)
        with open('nyt_test_recipe.html', 'r') as f:
            self.result = NYTimesCooking(f)

    def test_name(self):
        self.assertEqual(self.result.recipe_name, 'Grilled Pineapple Salsa')

    def test_ingredients(self):
        self.assertTrue('Option No 1' in self.result.ingredient_dict)
        self.assertTrue('Option No 2' in self.result.ingredient_dict)
        self.assertTrue('Option No 3' in self.result.ingredient_dict)


if __name__ == "__main__":
    unittest.main()
