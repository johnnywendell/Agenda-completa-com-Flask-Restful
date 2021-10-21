import sqlite3
from flask import Flask, render_template, make_response, request, url_for, flash, redirect
from flask_restful import Resource, Api
from werkzeug.exceptions import abort

# ****************** MAIN FUNCTIONS  ********************

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

app = Flask(__name__)
app.config['SECRET_KEY'] = 'johnnywendell'
api = Api(app)

# ****************** USER INTERACTIONS ********************

class Index(Resource):
    def get(self):
        conn = get_db_connection()
        posts = conn.execute('SELECT * FROM posts').fetchall()
        conn.close()
        return make_response(render_template('index.html', posts=posts))

class Post(Resource):
    def get(self, post_id):
        post = get_post(post_id)
        return make_response(render_template('post.html', post=post))

class Create(Resource):
    def post(self):
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash('Title is required!')
            return redirect(url_for('create'))
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    def get(self):
        return make_response(render_template('create.html'))

class Edit(Resource):
    def post(self, id):
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    def get(self, id):
        post = get_post(id)
        return make_response(render_template('edit.html', post=post))

class Delete(Resource):
    def post(self, id):
        post = get_post(id)
        conn = get_db_connection()
        conn.execute('DELETE FROM posts WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        flash('"{}" was successfully deleted!'.format(post['title']))
        return redirect(url_for('index'))


# ****************** URL's (ROTAS)********************
api.add_resource(Index, '/')
api.add_resource(Post, '/<int:post_id>')
api.add_resource(Create, '/create')
api.add_resource(Edit, '/<int:id>/edit')
api.add_resource(Delete, '/<int:id>/delete')

# ****************** START PROJECT ********************
if __name__ == '__main__':
    app.run(debug=True)