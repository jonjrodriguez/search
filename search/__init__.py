from flask import Flask, g, render_template

app = Flask(__name__)
app.config.from_object('config')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.before_request
def load_current_user():
    g.user = None

from search.views import search
from search.views import admin