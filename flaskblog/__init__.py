from flask import Flask, render_template, flash, redirect, url_for
from flask_migrate import Migrate
from werkzeug.security import check_password_hash
from flask_login import login_user, LoginManager, login_required, logout_user
from webforms import LoginForm, PasswordForm, SearchForm
from models import db, Users, Posts
from flask_ckeditor import CKEditor
from .views.user_management import manage_users 
from .views.post_management import manage_posts
from .views.admin import admins

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

    # add CKEditor for rich text textarea
    ckeditor = CKEditor(app)
    
    # Flask_Login stuff
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))
    
    # pass stuff to navbar
    @app.context_processor
    def base():
        form = SearchForm()
        return dict(form=form)

    # create a route decorator
    @app.route('/', methods=['GET', 'POST'])
    def login():
        form = LoginForm()

        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            user = Users.query.filter_by(username=username).first()
            if user:
                # check the hash
                if check_password_hash(user.password_hash, password):
                    login_user(user)
                    flash("Login Successful")
                    return redirect(url_for('dashboard'))
                else:
                    flash("Incorrect Password")
            else:
                flash("The User Doesn't Exists")

        content = {
            'form': form
        }
        return render_template('login.html', **content)
    
    @app.route('/logout', methods=['GET', 'POST'])
    @login_required
    def logout():
        logout_user()
        flash("You Have Been Logged Out")
        return redirect(url_for('login'))

    @app.route('/dashboard', methods=['GET', 'POST'])
    @login_required
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/search', methods=['POST'])
    def search():
        form = SearchForm()
    
        if form.validate_on_submit():
            search_input = form.search_input.data
            posts = Posts.query.filter(Posts.content.like('%' + search_input + '%')).order_by(Posts.title).all()

            content = {
                'posts': posts
            }
            return render_template('search.html', **content)
    
    app.register_blueprint(manage_users, url_prefix='/user')
    app.register_blueprint(manage_posts, url_prefix='/post')
    app.register_blueprint(admins, url_prefix='/admin')
    

    # custom error pages

    # invalid url
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error/404.html'), 404

    # internal server error
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error/500.html'), 500
    

    # test pages

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