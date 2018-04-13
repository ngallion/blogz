from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:launchcode@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "axbxcd98"

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/newpost', methods=['POST','GET'])
def newpost():
    
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']

        title_error = ""
        body_error = ""

        if blog_title == "":
            title_error = "Please fill in the title"
        if blog_body == "":
            body_error = "Please fill in the body"

        if not title_error and not body_error:
            new_blog = Blog(blog_title, blog_body)
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
    blog_id = request.args.get("id")
    if blog_id:
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('blog.html', title=blog.title,
                        blog=blog)
    else:
        blogs = Blog.query.order_by(Blog.id.desc())
        return render_template('blog.html', title="Build-a-Blog!",
                        blogs=blogs)

    

@app.route('/')
def main():
    return redirect('/blog')

if __name__ == '__main__':
    app.run()