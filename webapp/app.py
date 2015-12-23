from flask import Flask, request, render_template

import sys
import os
import pickle

from recipetools.search import find_recipe_with_ingredients, found_not_found

app = Flask(__name__)
app.debug = True

cap_dir = os.getenv("CAPSTONE_DIR", '/home/ubuntu/gschool-capstone')
pickle_path = os.path.join(cap_dir, 'data', 'pickles')

with open(os.path.join(pickle_path, 'features.pkl'), 'rb') as f:
    features= pickle.load(f)

with open(os.path.join(pickle_path, 'topics.pkl'), 'rb') as f:
    topics = pickle.load(f)


@app.route('/', methods=['POST', 'GET'])
def index():
    query = request.form.get('ingredients', None)
    if query is not None and len(query) == 0:
        query = None

    categories = request.form.getlist('category')

    if query is not None:
        results = find_recipe_with_ingredients(query, categories, features, topics)
        return render_template('search.html', query=query, results=list(results), form=categories)
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

    app.run(host='0.0.0.0', port=port, debug=debug)
