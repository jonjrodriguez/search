from search import app
from search.database import query_db
from flask import flash, redirect, request, session, g, render_template, url_for

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
	query = request.args.get('q').strip()

	if not query:
		flash('Please enter a search query')
		return redirect(url_for('index'))

	return render_template('search.html', query=query)

@app.route('/admin')
def admin():
	return "Admin"

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            return log_the_user_in(request.form['username'])
        else:
            error = 'Invalid username/password'

    return render_template('login.html', error=error)