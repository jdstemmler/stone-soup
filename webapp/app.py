from flask import Flask, request, render_template, send_from_directory

import sys
import os
import pickle
import datetime
import requests

from collections import defaultdict
from pymongo import MongoClient
from recipetools.settings import load_setting
from recipetools.search import find_recipe_with_ingredients  # , found_not_found

app = Flask(__name__)
app.debug = True

# set the location of the capstone directory
cap_dir = os.getenv("CAPSTONE_DIR", '/home/ubuntu/gschool-capstone')

# set the location of the settings file
settings_file = os.path.join(cap_dir, 'settings', 'project_settings.json')
api_file = os.path.join(cap_dir, 'settings', 'api_settings.json')

# set the pickle paths
pickle_path = os.path.join(cap_dir, 'data', 'pickles')

# load in some settings
database = load_setting(settings_file, item='db_name')

# get the google captcha api key
google_captcha_key = load_setting(api_file, item='GOOGLE_CAPTCHA')
google_site_key = load_setting(api_file, item="GOOGLE_SITEKEY")

with open(os.path.join(pickle_path, 'features.pkl'), 'rb') as f:
    features = pickle.load(f)

with open(os.path.join(pickle_path, 'topics.pkl'), 'rb') as f:
    topics = pickle.load(f)

client = MongoClient()
db = client[database]
tab = db['feedback']


@app.route('/deck')
def deck():
    return send_from_directory(os.path.join(cap_dir, 'webapp', 'presentation', 'StoneSoup'), 'index.html')


@app.route('/assets/<path:filename>')
def player(filename):
    head, tail = os.path.split(filename)
    fullpath = os.path.join(cap_dir, 'webapp/presentation/StoneSoup/assets', head)
    return send_from_directory(fullpath, tail)


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


@app.route('/advanced')
def advanced():
    return "This little light of mine..."


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['POST', 'GET'])
def contact():
    query = request.form.get('feedback', None)
    gcaptcha = request.form.get('g-recaptcha-response')
    gcaptcha_payload = {'secret': google_captcha_key,
                        'response': gcaptcha}
    captcha_response = requests.post("https://www.google.com/recaptcha/api/siteverify", data=gcaptcha_payload)
    verified = captcha_response.json()['success']

    if query is not None and verified:
        # return captcha_response.content
        tab.insert_one({'timestamp': datetime.datetime.now().strftime('%c'), 'feedback': query})

    return render_template('contact.html', google_site_key=google_site_key)


@app.route('/dashboard')
def dashboard():
    responses = tab.find({}, {'_id': 0, 'timestamp': 1, 'feedback': 1})
    feedback = []
    for response in responses:
        feedback.append(dict(response))

    return render_template('dashboard.html', feedback=feedback)

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
