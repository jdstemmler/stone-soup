from flask import Flask, request, render_template
from collections import namedtuple
import sys
import os
import pickle
import ngram

from recipetools.search import find_recipe_with_ingredients, found_not_found

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
    query = request.form.get('ingredients', None)

    if query is not None:
        # results, terms = find_recipe_with_ingredients(query, model)
        results = find_recipe_with_ingredients(query, model)
        # fnd, nfnd = found_not_found(terms)
        return render_template('search.html', query=query, results=list(results))  # , found=fnd, not_found=nfnd)
    elif query is None:
        return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':

    if '--debug' in sys.argv:
        debug = True
    else:
        debug = False

    if '--port' in sys.argv:
        ix = sys.argv.index('--port') + 1
        port = int(sys.argv[ix])
    else:
        port = 8080

    cap_dir = os.getenv("CAPSTONE_DIR")
    pickle_path = os.path.join(cap_dir, 'data', 'pickles')
    ModelData = namedtuple('Model', 'bag, vocab, components, ng')

    with open(os.path.join(pickle_path, 'bag_of_ingredients.pkl'), 'rb') as f:
        bag = pickle.load(f)

    with open(os.path.join(pickle_path, 'vocabulary.pkl'), 'rb') as f:
        vocab = pickle.load(f)

    with open(os.path.join(pickle_path, 'recipe_components.pkl'), 'rb') as f:
        components = pickle.load(f)

    ng = ngram.NGram(vocab.keys())

    model = ModelData(bag=bag, vocab=vocab, components=components, ng=ng)

    app.run(host='0.0.0.0', port=port, debug=debug)