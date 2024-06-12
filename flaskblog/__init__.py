from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

# initialize the database
db = SQLAlchemy()

# create a user model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    mobile = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.now())
    # password stuff
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute!')
        
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # create a string
    def __repr__(self):
        return '<Name %r>' % self.name
    
# create a blog post model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.now())
    slug = db.Column(db.String(255))

def create_app():
    # create a flask instance
    app = Flask(__name__)
    # add database
    # old sqlite db
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    # new mysql db
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:abc123@localhost/flaskblog'
    # secret key
    app.secret_key = 'hday9o32ej382jjdi09hh3'

    db.init_app(app)
    migrate = Migrate(app, db)

    # create a form class
    class UserForm(FlaskForm):
        name = StringField("Name", validators=[DataRequired()])
        email = StringField("Email", validators=[DataRequired()])
        mobile = StringField("Mobile")
        password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Password must match!!')])
        password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
        submit = SubmitField("Submit")

    # create a form class
    class PasswordForm(FlaskForm):
        email = StringField("Email", validators=[DataRequired()])
        password_hash = PasswordField('Password', validators=[DataRequired()])
        submit = SubmitField("Submit")

    # create a form class
    class NamerForm(FlaskForm):
        name = StringField("What is your name", validators=[DataRequired()])
        submit = SubmitField("Submit")

    # create a post form class
    class PostForm(FlaskForm):
        title = StringField("Title", validators=[DataRequired()])
        content = StringField("Content", validators=[DataRequired()], widget=TextArea())
        author = StringField("Author", validators=[DataRequired()])
        slug = StringField("Slug", validators=[DataRequired()])
        submit = SubmitField("Submit")

    # create a route decorator
    @app.route('/')
    def index():
        return "Hello"
    
    @app.route('/profile/<name>')
    def profile(name):
        context = {
            'name': name
        }
        return render_template('user_management/profile.html', **context)
    
    @app.route('/name', methods=['GET', 'POST'])
    def name():
        name = None
        form = NamerForm()

        # validate form
        if form.validate_on_submit():
            name = form.name.data
            form.name.data = ''
            flash("Form Submitted Successful")

        context = {
            'name': name,
            'form': form
        }
        return render_template('user_management/name.html', **context)

    @app.route('/user/add', methods=['GET', 'POST'])
    def add_user():
        form = UserForm()

        # validate form
        if form.validate_on_submit():
            # check if database consist the same email
            name = form.name.data
            email = form.email.data
            mobile = form.mobile.data
            password_hash = form.password_hash.data
            user = Users.query.filter_by(email=email).first()
            if user is None:
                # hash the password
                hashed_pw = generate_password_hash(form.password_hash.data, "pbkdf2:sha256")
                user = Users(name=name, email=email, mobile=mobile, password_hash=hashed_pw)
                db.session.add(user)
                db.session.commit()
                message = "User Added Successfully"
            else:
                message = "Email Registered Before"
            
            form.name.data = ''
            form.email.data = ''
            form.mobile.data = ''
            form.password_hash.data = ''
            flash(message)

        user_list = Users.query.order_by(Users.date_added)

        context = {
            'form': form,
            'user_list': user_list
        }
        return render_template('user_management/add_user.html', **context)
    
    @app.route('/user/update/<int:id>', methods=['GET', 'POST'])
    def update_user(id):
        form = UserForm()

        user_to_update = Users.query.get_or_404(id)
        if request.method == 'POST':
            user_to_update.name = request.form['name']
            user_to_update.email = request.form['email']
            user_to_update.mobile = request.form['mobile']
            try:
                # save into database
                db.session.commit()
                flash("User Updated Successfully")
            except:
                flash("User Not Found")

        context = {
            'form': form,
            'user_to_update': user_to_update
        }
        return render_template('user_management/update_user.html', **context)

    @app.route('/user/delete/<int:id>')
    def delete_user(id):
        form = UserForm()

        user_to_delete = Users.query.get_or_404(id)

        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("User Deleted Successfully")
        except:
            flash("User Not Found")

        user_list = Users.query.order_by(Users.date_added)

        context = {
            'form': form,
            'user_list': user_list
        }
        return render_template('user_management/add_user.html', **context)

    @app.route('/post/add', methods=['GET', 'POST'])
    def add_post():
        form = PostForm()

        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            author = form.author.data
            slug = form.slug.data
            post = Posts(title=title, content=content, author=author, slug=slug)

            form.title.data = ''
            form.content.data = ''
            form.author.data = ''
            form.slug.data = ''

            db.session.add(post)
            db.session.commit()

            flash("Blog Post Submitted Successfully")

        content = {
            'form': form
        }
        return render_template('post_management/add_post.html', **content)

    # create custom error pages

    # invalid url
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error/404.html'), 404

    # internal server error
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error/500.html'), 500
    
    # test hashed password
    @app.route('/test_pw', methods=['GET', 'POST'])
    def test_pw():
        email = None
        password = None
        pw_to_check = None
        passed = None
        form = PasswordForm()

        # validate form
        if form.validate_on_submit():
            email = form.email.data
            password = form.password_hash.data
            form.email.data = ''
            form.password_hash.data = ''

            # look up user by email
            pw_to_check = Users.query.filter_by(email=email).first()

            # check hashed password
            passed = check_password_hash(pw_to_check.password_hash, password)

            flash("Form Submitted Successful")

        context = {
            'email': email,
            'password': password,
            'pw_to_check': pw_to_check,
            'passed': passed,
            'form': form
        }
        return render_template('user_management/test_pw.html', **context)
    
    # JSON API
    @app.route('/date')
    def get_current_datetime():
        users = {
            "John": "john@gmail.com",
            "Yunna": "yunna@gmail.com",
            "Yang": "yang@gmail.com"
        } 
        return users
        #return {"DateTime": datetime.now()}

    return app