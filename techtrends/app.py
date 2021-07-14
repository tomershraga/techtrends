#Tomer
#Tomer
import sqlite3
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash, Response
from werkzeug.exceptions import abort
import logging
import sys

# Function to get a database connection.
# This function connects to database with the name `database.db`
db_connections_count = 0
num_of_posts = 0
def get_db_connection():
    global db_connections_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    db_connections_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    global num_of_posts
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.info('A non existing article is accessed')
        return render_template('404.html'), 404
    else:
        app.logger.info('Article "{}" retrieved!'.format(post['title']))
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About us page is retrieved')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info('A new article is created: {}!'.format(title))
            global num_of_posts
            num_of_posts += 1
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def healthz():
    return Response('{result: OK - healthy}', status=200)

@app.route('/metrics')
def metrics():
    global db_connections_count
    global num_of_posts
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    res = {'db_connection_count': db_connections_count, 'post_count': num_of_posts + len(posts)}
    return Response(json.dumps(res), status=200)

# start the application on port 3111
if __name__ == "__main__":
    a_logger = logging.getLogger()
    a_logger.setLevel(logging.DEBUG)
    output_file_handler = logging.FileHandler("app.log")
    stdout_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s : %(message)s')
    stdout_handler.setFormatter(formatter)
    a_logger.addHandler(output_file_handler)
    a_logger.addHandler(stdout_handler)
    app.run(host='0.0.0.0', port='3111', debug=True)
