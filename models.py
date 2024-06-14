from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# initialize the database
db = SQLAlchemy()

# create a user model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    mobile = db.Column(db.String(120))
    about_author = db.Column(db.Text(), nullable=True)
    profile_pic = db.Column(db.String(255), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.now())
    # password stuff
    password_hash = db.Column(db.String(128))
    # a user can have many post
    post = db.relationship('Posts', backref='user')

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
    #author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.now())
    slug = db.Column(db.String(255))
    # foreign key to link user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))