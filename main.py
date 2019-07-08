from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:wusry1209@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '1234567890'

class Blog(db.Model):

    id =  db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    date = db.Column(db.DateTime)


    def __init__(self, title, body, date=None):
        self.title = title
        self.body = body
        if date is None:
            date = datetime.utcnow()
        self.date = date
        

@app.route('/', methods=['GET'])
def index():

    blogs = Blog.query.all()
    return render_template('blog.html',title="Build a Blog", blogs=blogs)

@app.route("/blog", methods=["GET"])   
def blog():

    blogs = Blog.query.all()
    return render_template('blog.html', title="Build A Blog", blogs=blogs)

@app.route("/blogpost", methods=["GET"])
def blogpost():

    blog_id = request.args.get('id')
    blog = Blog.query.filter_by(id=blog_id).first()
    return render_template('blogpost.html', blog=blog)

@app.route("/newpost", methods=["POST", "GET"])    
def newpost():

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        body = request.form['body']
        new_blog = Blog(blog_title, body)
        db.session.add(new_blog)
        db.session.commit()
        id = new_blog.id
        return redirect(url_for("blogpost", id=id)) 
    else:
        return render_template("/newpost.html")

if __name__ == '__main__':  
    app.run()