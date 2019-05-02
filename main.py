from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://get-it-done:beproductive@localhost:8889/get-it-done'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, body, owner):
        self.name = name
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['log_in','sign_up','signup','users','blogposts','user_blogs','blogpost']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/log_in')

#changed to /home from /   , to meet blogz requirements
@app.route('/home', methods=['POST', 'GET'])
def index():
    owner = User.query.filter_by(username=session['username']).first()

    blogposts = Blog.query.filter_by(owner=owner).all()
    return render_template('home.html',title="< My blog >", 
        blogposts=blogposts,username=session['username'])

@app.route('/new_post', methods=['GET','POST'])
def new_post():
    owner = User.query.filter_by(username=session['username']).first() #check who user is
    message = ""
    blogpost_name = ""
    blogpost_body = ""
    if request.method == 'POST':
        blogpost_name = request.form['blogpost']
        blogpost_body = request.form['body']
        if len(blogpost_name) <3 or len(blogpost_body) <3:
            message = "Your blog title or content is too short."
            
        else:
            message = "Success!"
            new_blogpost = Blog(blogpost_name,blogpost_body,owner)
            db.session.add(new_blogpost)
            db.session.commit()
            return render_template('blogpost.html',title="< My blog >", 
            blogpost_name=blogpost_name, blogpost_body=blogpost_body,blogpost_owner=owner)
    
    blogposts = Blog.query.filter_by(owner=owner).all()
    return render_template('new_post.html',title="< My blog >", 
        message=message,name=blogpost_name,content=blogpost_body)
    
@app.route('/blogpost', methods=['GET'])
def blogpost():
    blogpost_id = request.args.get("blogpost-id")
    blogpost = Blog.query.get(blogpost_id)
    blogpost_name = blogpost.name
    blogpost_body = blogpost.body
    owner_id = blogpost.owner_id
    blogpost_owner = User.query.filter_by(id=owner_id).first()
    return render_template('blogpost.html', 
        blogpost_name=blogpost_name, blogpost_body=blogpost_body,blogpost_owner=blogpost_owner)

@app.route("/register", methods=['POST'])
def signup():
    username_error = ''
    password_error = ''
    confirm_error = ''
    email_error = ''

    username = request.form['username']
    password = request.form['password']
    password_confirm = request.form['password_confirm']
    email = request.form['email']
    existing_user = User.query.filter_by(username=username).first() #makes sure there isn't already a user with same name
    if email != '':
        if email.find('@') == -1 or email.find('.') == -1 or len(email) <3:
            email_error = ' Emails must be formatted properly'
    if existing_user or len(username) <3 or len(password) <3 or password != password_confirm or email_error != '':
        error = "Error(s) detected"
        if len(username) <3:
            username_error = ' Username should be 3 or more characters'
        if len(password) <3:
            password_error = ' Password should be 3 or more characters'
        if password_confirm != password:
            confirm_error = ' Passwords must match'
        if existing_user:
            username_error = ' Username already taken'
        return render_template('sign_up.html',username=username,email=email,username_error=username_error,password_error=password_error,confirm_error=confirm_error,email_error=email_error,error=error) #redirect("/?error")

    new_user = User(username,password)
    db.session.add(new_user)
    db.session.commit()
    session['username'] = username
    users = User.query.all()
    return render_template('welcome.html',username=username, users=users)

@app.route("/register")
def sign_up():
    encoded_error = request.args.get("error")
    return render_template('sign_up.html', error=encoded_error and cgi.escape(encoded_error, quote=True))

@app.route("/log_in",methods=['POST','GET'])
def log_in():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            # cookies - user has logged in!!!
            session['username'] = username
            return redirect('/')
        else:
            message = '( ͠° ͟ʖ ͡°) Incorrect username or password ( ͡° ʖ̯ ͡°)'
            return render_template('log_in.html',message=message)
    return render_template('log_in.html')

@app.route('/log_out')
def log_out():
    del session['username']
    return redirect('/')

@app.route('/')
def users():
    users = User.query.all()
    return render_template('users.html',title="< My blog >", users=users)

@app.route('/user_blogs')
def user_blogs():
    user_id = request.args.get("user")
    user = User.query.filter_by(id=user_id).first()
    username = user.username
    blogposts = Blog.query.filter_by(owner_id=user_id).all()
    return render_template('user_blogs.html',title="< My blog >", blogposts=blogposts,id=user_id,username=username)

@app.route('/blogposts')
def blogposts():
    blogposts = Blog.query.all()
    users = User.query.all()
    return render_template('blogposts.html',title="< My blog >", 
        blogposts=blogposts)

if __name__ == '__main__':
    app.run()