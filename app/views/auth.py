from app import app
from app.database import get_user
from flask import flash, redirect, request, session, g, render_template, url_for
from werkzeug import check_password_hash

@app.route('/login')
def login():
    if g.user:
        return redirect(url_for('admin'))

    return render_template('auth/login.html')

@app.route('/login', methods=['POST'])
def postLogin():
    user = get_user(request.form['username'])

    if not user or not check_password_hash(user['password'], request.form['password']):
        flash('Invalid username or password', 'error')
        return redirect(url_for('login'))

    flash('You were logged in', 'success')
    session['username'] = user['username']
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    flash('You were logged out', 'success')
    session.pop('username', None)
    return redirect(url_for('index'))