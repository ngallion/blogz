from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "axbxcd98"

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        flash("Login to access this page")
        return redirect('/login')

@app.route('/newpost', methods=['POST','GET'])
def newpost():
    
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']

        title_error = ""
        body_error = ""
        
        owner = User.query.filter_by(username=session['username']).first()

        if blog_title == "":
            title_error = "Please fill in the title"
        if blog_body == "":
            body_error = "Please fill in the body"

        if not title_error and not body_error:
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={0}'.format(new_blog.id))
        else:
            return render_template('newpost.html', title="Add Blog Entry",
                blog_title=blog_title, blog_body=blog_body, title_error=title_error,
                body_error=body_error)
    else:
        return render_template('newpost.html', title="Add Blog Entry")

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    username = request.args.get("user")
    user = User.query.filter_by(username=username).first()
    blog_id = request.args.get("id")
    if blog_id:
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('blog.html', title=blog.title,
                        blog=blog)
    if username:
        blogs = Blog.query.filter_by(owner_id=user.id).order_by(Blog.id.desc())
        return render_template('blog.html', title="Blogz", blogs=blogs)
    else:
        blogs = Blog.query.order_by(Blog.id.desc())
        return render_template('blog.html', title="Blogz",
                        blogs=blogs)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error = ''
        password_error = ''
        verify_error = ''

        if username == '':
            username_error = "Please enter a username"
        if re.match("^[a-zA-Z0-9_.-]{3,20}$", username) is None:
            username_error = "Invalid username"
        if password == '':
            password_error = "Please enter a password"
        if re.match("^[a-zA-Z0-9_.-]{3,20}$", password) is None:
            password_error = "Invalid password"
        if verify != password:
            verify_error = "Passwords do not match"

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            username_error = "User already exists"

        if not password_error and not verify_error and not username_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/blog')
        else:
            
            return render_template('signup.html',username_error=username_error,
                password_error=password_error, verify_error=verify_error)
    else:
        return render_template('signup.html')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        username_error = ''
        password_error = ''

        if not user:
            username_error = "Username does not exist"
        elif user.password != password:
            password_error = "Incorrect password"

        if not username_error and not password_error:
            session['username'] = username
            flash("Logged in")
            print(session)
            return redirect('/')
        else:
            return render_template('login.html', username=username, 
                username_error=username_error, password_error=password_error)
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    flash("Logged out")
    return redirect('blog.html')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

if __name__ == '__main__':
    app.run()