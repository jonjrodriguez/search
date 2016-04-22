from app import app
from app.database import query_db
from app.search.searcher import SearchIndex
from flask import flash, redirect, request, session, g, render_template, url_for

@app.route('/')
def index():
    return render_template('search/search.html')

@app.route('/search')
def search():
	query = request.args.get('q')
	page = request.args.get('page', 1, type=int)

	duplicates = request.args.has_key('duplicates')

	if query:
		query = query.strip()

	if not query:
		flash('Please enter a search query', 'error')
		return redirect(url_for('index'))

	searcher = SearchIndex()
	totalPages, results = searcher.search(query, page, duplicates)

	start = max(1, min(totalPages-4,page-2))
	end = min(totalPages+1, start+5)

	return render_template(
		'search/results.html', 
		query=query, 
		results=results,
		pages={'start': start, 'end': end, 'total': totalPages, 'current': page}
	)