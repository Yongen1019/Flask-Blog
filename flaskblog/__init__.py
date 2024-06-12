from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# initialize the database
db = SQLAlchemy()

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

    # create model
    class Users(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(200), nullable=False)
        email = db.Column(db.String(120), nullable=False, unique=True)
        date_added = db.Column(db.DateTime, default=datetime.now)

        # create a string
        def __repr__(self):
            return '<Name %r>' % self.name
    
    # create a form class
    class UserForm(FlaskForm):
        name = StringField("Name", validators=[DataRequired()])
        email = StringField("Email", validators=[DataRequired()])
        submit = SubmitField("Submit")

    # create a form class
    class NamerForm(FlaskForm):
        name = StringField("What is your name", validators=[DataRequired()])
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
            user = Users.query.filter_by(email=email).first()
            if user is None:
                user = Users(name=name, email=email)
                db.session.add(user)
                db.session.commit()
                message = "User Added Successfully"
            else:
                message = "Email Registered Before"
            
            form.name.data = ''
            form.email.data = ''
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

        # validate form
        if form.validate_on_submit():
            # check if database consist the same email
            name = form.name.data
            email = form.email.data
            user = Users.query.filter_by(email=email).first()
            if user is None:
                user = Users(name=name, email=email)
                db.session.add(user)
                db.session.commit()
                message = "User Added Successfully"
            else:
                message = "Email Registered Before"
            
            form.name.data = ''
            form.email.data = ''
            flash(message)

        user_list = Users.query.order_by(Users.date_added)

        context = {
            'form': form,
            'user_list': user_list
        }
        return render_template('user_management/add_user.html', **context)

    # create custom error pages

    # invalid url
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error/404.html'), 404

    # internal server error
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error/500.html'), 500

    return app