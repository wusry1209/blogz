from flask import request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi
from app import app, db
from models import User, Blog
from hashutils import make_pw_hash, check_pw_hash


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index', '/static/styles/main.css']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login') 

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            flash('Logged in')
            return redirect('/newpost')
        elif user and user.password != password:
            flash('Incorrect Password', 'error')
            return redirect('/login')
        elif not user:
            flash('This username does not exist', 'error')
            return redirect('/login')
    else:
        return render_template('login.html')   

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        if not username or not password or not verify:
            flash('One or more fields are empty', 'error')
            return redirect('/signup')
        elif len(password) < 6 or len(username) < 6:
            flash('Usernames and passwords must at least 6 characters long', 'error')
            return redirect('/signup')
        elif existing_user:
            flash('Username already exists', 'error')
            return redirect('/signup')
        elif password != verify:
            flash('Passwords do not match', 'error')
            return redirect('/signup')
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
    else:
        return render_template('signup.html')


@app.route("/blog", methods=["POST", "GET"])   
def blog():

    if request.args.get('id'):
        blog_id = request.args.get('id')
        blog = Blog.query.filter_by(id = blog_id).first()
        return render_template('singlepost.html', title='Blogs | Blogz', blog=blog)
    if request.args.get('user'):
        user_id= request.args.get('user')
        user = User.query.get(user_id)
        blogs = Blog.query.filter_by(owner=user).all()
        return render_template('blog.html', title='Blogs | Blogz', blogs=blogs)
    blogs = Blog.query.all()
    users = User.query.all()
    return render_template('blog.html', title='Blogs | Blogz', blogs=blogs, users=users)

@app.route("/blogpost", methods=["GET"])
def blogpost():

    blog_id = request.args.get('id')
    blog = Blog.query.filter_by(id=blog_id).first()
    return render_template('blogpost.html', blog=blog)

@app.route("/newpost", methods=["POST", "GET"])    
def newpost():
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()

        title_error = ''
        body_error = ''
        
        if not blog_title:
            title_error = "Please enter a title"
            return render_template('newpost.html', body=blog_body, title_error=title_error, blog_body=blog_body)
        if not blog_body:
            body_error = "Please enter a blog post dummy!"
            return render_template('newpost.html', blog_title=blog_title, body_error=body_error)
        else:

            new_blog_post = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog_post)
            db.session.commit()
            blog_id = new_blog_post.id
            blog = Blog.query.filter_by(id = blog_id).first()
            return render_template('singlepost.html', title='Newpost | Blogz', blog=blog)
    return render_template('newpost.html', title="Post New Blog")

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('/index.html', title='Home | Blogz', users=users)

   

if __name__ == '__main__':  
    app.run()