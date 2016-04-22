import time
from app import app
from sqlite3 import dbapi2 as sqlite3
from flask import _app_ctx_stack
from werkzeug import generate_password_hash

def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    if not hasattr(_app_ctx_stack, 'sqlite_db'):
        _app_ctx_stack.sqlite_db = connect_db()
    return _app_ctx_stack.sqlite_db

def close_db(error):
    if hasattr(_app_ctx_stack, 'sqlite_db'):
        _app_ctx_stack.sqlite_db.close()

def init_db(user):
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    create_user(user[0], user[1], True)

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()

    return cur.lastrowid

def execute_many(query, args=()):
    db = get_db()
    db.executemany(query, args)
    db.commit()

def create_user(username, password, is_admin=False):
    return execute_db("insert into users (username, password, is_admin) values (?, ?, ?)", [username, generate_password_hash(password), is_admin])

def get_user(username):
    return query_db('select * from users where username = ?', [username], one=True)

def store_crawl(filepath):
    execute_db("insert into crawls (filepath, crawl_date) values (?, ?)", [filepath, time.strftime('%Y-%m-%d %H:%M:%S')])

def store_duplicates(duplicates):
    execute_many("insert into duplicates (url, duplicate, similarity) values (?, ?, ?)",
        [(duplicate['document'], duplicate['duplicate'], duplicate['sim']) for duplicate in duplicates])

def store_outlinks(url, outlinks):
    execute_many("insert into outlinks (url, outlink) values (?, ?)", [(url, outlink) for outlink in outlinks])