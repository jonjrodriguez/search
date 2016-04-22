from flask import Flask, g, render_template, request, session, url_for

app = Flask(__name__)
app.config.from_object('config')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.before_request
def load_current_user():
    g.user = get_user(session['username']) if 'username' in session else None

@app.template_global()
def url_for_search(page=None, duplicates=None):
    url = url_for('search', q=request.args.get('q'), page=page)

    if duplicates is None:
        duplicates = request.args.has_key('duplicates')

    if duplicates:
        return url + '&duplicates'

    return url

from app.views import search
from app.views import auth
from app.views import admin

from app.database import get_user, close_db