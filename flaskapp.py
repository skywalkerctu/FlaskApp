# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 15:42:54 2022

@author: Hanniel Shih
"""

from collections import Counter
import sqlite3
from flask import Flask, request, g, render_template, url_for, flash, redirect, session, send_file
import os
app = Flask(__name__)

DATABASE = 'database.db'

app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'qwerty'
app.config['UPLOAD_FOLDER'] = 'files/'


def connect_to_database():
    return sqlite3.connect(app.config['DATABASE'])

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = connect_to_database()
    return db

messages = [{'title': 'Message One',
             'content': 'Message One Content'},
            {'title': 'Message Two',
             'content': 'Message Two Content'}
            ]

def organize_users(rows):
    users = []
    for row in rows:
        users.append(
            {'username': row[2], 
             'password': row[3],
             'firstname': row[4],
             'lastname': row[5], 
             'email': row[6]}
            )
    return users

@app.route('/download')
def download():
    username = session['username']
    filename = os.path.join(app.config['UPLOAD_FOLDER'], f'{username}.txt')
    return send_file(filename, as_attachment=True, download_name='text file.txt')

# @app.route('/viewm')
# def viewm():
#     rows = execute_query("""SELECT * FROM users""")
#     users = organize_users(rows)
#     return render_template('viewm.html', users=users)
#     # return render_template('viewm.html', messages=messages)

@app.route('/viewinfo')
def viewinfo():
    username = session['username']
    rows = execute_query("""SELECT * FROM users WHERE username=?""", (username,))
    users = organize_users(rows)
    with open(os.path.join(app.config['UPLOAD_FOLDER'], f'{username}.txt'), 'r') as f:
        data = f.read()
        num_words = len(data.split())
    return render_template('viewinfo.html', users=users, num_words=num_words)

@app.route('/login/', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not (username and password):
            flash('Please fill in every field')
        else:
            rows = execute_query("""SELECT * FROM users WHERE username=? AND password=?""", (username, password))
            if len(rows) == 0:
                flash('User does not exist or wrong password')
            else:
                session['username'] = username
                return redirect(url_for('viewinfo'))
    return render_template('login.html')

@app.route('/register/', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        file = request.files['file']

        if not (username and password and firstname and lastname and email and file):
            flash('Please fill in every field')
        elif execute_query("""SELECT * FROM users WHERE username=?""", (username,)) != []:
            flash('Username already existed, please choose a different one')
        else:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], f'{username}.txt'))
            flash('File successfully uploaded')
            execute_post("INSERT INTO users (username, password, firstname, lastname, email) VALUES (?,?,?,?,?)",
                        (username, password, firstname, lastname, email))
            session['username'] = username
            return redirect(url_for('viewinfo'))
    return render_template('register.html')

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
        
def execute_post(post, args=()):
    conn = get_db()
    conn.execute(post, args)
    conn.commit()
    conn.close()
    
def execute_query(query, args=()):
    cur = get_db().execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows

# @app.route("/viewdb")
# def viewdb():
#     rows = execute_query("""SELECT * FROM users""")
#     return '<br>'.join(str(row) for row in rows)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# @app.route('/countme/<input_str>')
# def count_me(input_str):
#     input_counter = Counter(input_str)
#     response = []
#     for letter, count in input_counter.most_common():
#         response.append('"{}": {}'.format(letter, count))
#     return '<br>'.join(response)

if __name__ == '__main__':
  app.run()
