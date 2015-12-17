from flask import Flask, request, render_template, Markup
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/about')
def about():
    return render_template('about.html', img='../static/gfys.jpg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)