from os.path import basename
from functools import wraps
from app import app
from app.database import query_db, execute_db, create_user
from flask import redirect, request, g, render_template, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@login_required
def admin():
	crawls = query_db("select * from crawls order by crawl_date desc", [])
	crawls = [{
		'crawl_date': crawl['crawl_date'],
		'filepath': basename(crawl['filepath'])
	} for crawl in crawls]

	return render_template('admin/dashboard.html', crawls=crawls)

@app.route('/admin/duplicates')
@login_required
def duplicates():
	filter_type = request.args.get('type', 'near')

	where = ''
	if filter_type == 'exact':
		where = 'where similarity = 1'
	elif filter_type == 'near':
		where = 'where similarity < 1'

	duplicates = query_db("Select * from duplicates " + where + " order by similarity desc")

	return render_template('admin/duplicates.html',
		duplicates=duplicates,
		type=filter_type)

@app.route('/admin/details')
@login_required
def details():
	url = request.args.get('url')

	if not url:
		return redirect(url_for('admin'))

	inlinks = query_db("Select * from outlinks where outlink = (?)", [url])
	outlinks = query_db("Select * from outlinks where url = (?)", [url])

	return render_template('admin/details.html',
		url=url,
		inlinks=inlinks,
		outlinks=outlinks)

@app.route('/admin/users', methods=['GET', 'POST', 'DELETE'])
@login_required
def users():
	if not g.user['is_admin']:
		return redirect(url_for('admin'))

	if request.method == 'POST':
		create_user(request.form['username'], request.form['password'], request.form.get('admin', False))
		return redirect(url_for('users'))

	users = query_db("select * from users", [])

	return render_template('admin/users.html', users=users)

@app.route('/admin/users/delete', methods=['POST'])
@login_required
def delete_user():
	if not g.user['is_admin']:
		return redirect(url_for('admin'))

	if request.method == 'POST':
		execute_db("DELETE FROM users WHERE id = (?)", [request.form['user_id']])

	return redirect(url_for('users'))