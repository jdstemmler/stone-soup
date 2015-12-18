from flask import Flask, request, render_template
from collections import namedtuple
import os
import pickle

from recipetools.search import find_recipe_with_ingredients, found_not_found

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
    query = request.form.get('ingredients', None)

    if query is not None:
        results, terms = find_recipe_with_ingredients(query, model)
        fnd, nfnd = found_not_found(terms)
        return render_template('search.html', query=query, results=results, found=fnd, not_found=nfnd)
    elif query is None:
        return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':

    cap_dir = os.getenv("CAPSTONE_DIR")
    pickle_path = os.path.join(cap_dir, 'data', 'pickles')
    ModelData = namedtuple('Model', 'bag, vocab, components')

    with open(os.path.join(pickle_path, 'bag_of_ingredients.pkl'), 'rb') as f:
        bag = pickle.load(f)

    with open(os.path.join(pickle_path, 'vocabulary.pkl'), 'rb') as f:
        vocab = pickle.load(f)

    with open(os.path.join(pickle_path, 'recipe_components.pkl'), 'rb') as f:
        components = pickle.load(f)

    model = ModelData(bag=bag, vocab=vocab, components=components)

    app.run(host='0.0.0.0', port=8080, debug=True)